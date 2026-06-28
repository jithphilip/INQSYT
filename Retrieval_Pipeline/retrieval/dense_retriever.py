import os
import faiss
import json
import pickle
import pandas as pd
import numpy as np
import streamlit as st
import requests
from sentence_transformers import SentenceTransformer

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PIPELINE_DIR = os.path.dirname(CURRENT_DIR)

PROJECT_DIR = os.path.dirname(PIPELINE_DIR)

MAIN_DATA_DIR = os.path.join(PROJECT_DIR, "Main_Data")

INDICES_DIR = os.path.join(PIPELINE_DIR, "indices")

MODELS_DIR = os.path.join(PIPELINE_DIR, "models")

@st.cache_resource
def load_intent_resources():
    # Load chunks
    chunks_df = pd.read_json(
        os.path.join(MAIN_DATA_DIR, "Chunks", "chunks_v2_fixed.jsonl"),
        lines=True
        )
    
    # Load embedder
    embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
    
    # Load FAISS index
    index = faiss.read_index(
        os.path.join(INDICES_DIR, "faiss_index_v2.bin")
        )
    
    # Load classifier
    with open(os.path.join(MODELS_DIR, "intent_classifier_v3.pkl"), "rb") as f:
        classifier_data = pickle.load(f)
        
    # Reconstruct raw embeddings from Flat index
    all_vectors = np.array([index.reconstruct(i) for i in range(index.ntotal)]).astype("float32")
    
    # Load intents schema and map each chunk_id to its intent
    with open(
        os.path.join(MAIN_DATA_DIR, "Intents", "intents_schema_v2.json"),
        "r",
        encoding="utf-8"
        ) as f:
        intents_schema = json.load(f)
        
    chunk_to_intents = {}
    for entry in intents_schema:
        intent_name = entry["intent"]
        for cid in entry["source_chunks"]:
            if cid not in chunk_to_intents:
                chunk_to_intents[cid] = []
            chunk_to_intents[cid].append(intent_name)
            
    # Add an 'intents' column to chunks_df dynamically!
    chunks_df["intents"] = chunks_df["chunk_id"].map(chunk_to_intents)
    chunks_df["intents"] = chunks_df["intents"].apply(lambda x: x if isinstance(x, list) else ["other_query"])
    
    # Build intents list and description string for LLM router
    intents_list = [entry["intent"] for entry in intents_schema]
    intents_desc = ""
    for entry in intents_schema:
        intents_desc += f"- **{entry['intent']}**: {entry['description']}\n"
        
    intent_to_desc = {entry["intent"]: entry["description"] for entry in intents_schema}
    
    intent_to_samples = {}
    for entry in intents_schema:
        intent_name = entry["intent"]
        samples = []
        for cid in entry["source_chunks"]:
            match = chunks_df[chunks_df["chunk_id"] == cid]
            if not match.empty:
                meta = match.iloc[0].get("metadata")
                if isinstance(meta, dict):
                    qs = meta.get("sample_queries", [])
                    for q in qs:
                        if q not in samples:
                            samples.append(q)
        intent_to_samples[intent_name] = samples
        
    return (
        chunks_df,
        embedder,
        index,
        classifier_data,
        all_vectors,
        intents_list,
        intents_desc,
        intent_to_desc,
        intent_to_samples,
        intents_schema
    )

@st.cache_data
def get_llm_intent(query, intents_list, intents_desc, top_suggestions=None):
    try:
        OLLAMA_URL = st.secrets.get("OLLAMA_URL") or os.getenv("OLLAMA_URL") or "http://localhost:11434"
        OLLAMA_MODEL = st.secrets.get("OLLAMA_MODEL") or os.getenv("OLLAMA_MODEL") or "qwen2.5:7b"
    except Exception:
        OLLAMA_URL = os.getenv("OLLAMA_URL") or "http://localhost:11434"
        OLLAMA_MODEL = os.getenv("OLLAMA_MODEL") or "qwen2.5:7b"
    
    ollama_schema = {
        "type": "object",
        "properties": {
            "primary_intent": {
                "type": "string",
                "enum": intents_list
            },
            "secondary_intent": {
                "type": ["string", "null"],
                "enum": intents_list + [None]
            }
        },
        "required": ["primary_intent", "secondary_intent"]
    }
    
    few_shot_examples = """Examples:

Query: "How to change the shipping destination on a pending order?"
Explanation: This is modifying an active/open order, so it maps to "modify_order" (not "modify_address" which is for saved address book management).
Output: {"primary_intent": "modify_order", "secondary_intent": null}

Query: "How do I update my debit card billing address?"
Explanation: This is updating payment card billing info in the wallet, so it maps to "manage_wallet_cards" (not "modify_address" which is for shipping addresses).
Output: {"primary_intent": "manage_wallet_cards", "secondary_intent": null}

Query: "How do I stop receiving SMS updates about my orders?"
Explanation: This is turning off SMS delivery notifications, so it maps to "manage_delivery_alerts" (not "manage_notifications" which is for email preferences/newsletter).
Output: {"primary_intent": "manage_delivery_alerts", "secondary_intent": null}

Query: "Where do I flag a fake agent asking for payment?"
Explanation: This is reporting a payment scam, so it maps to "report_payment_scam".
Output: {"primary_intent": "report_payment_scam", "secondary_intent": "identify_phishing_scams"}

Query: "How do I set delivery instructions for my driver?"
Explanation: This defines guidelines for package drop-off/delivery, so it maps to "check_delivery_rules" (not "manage_delivery_alerts" which is for text/notification alerts).
Output: {"primary_intent": "check_delivery_rules", "secondary_intent": null}

Query: "My package says delivered to hotel front desk but I don't see it. Can I get a refund?"
Explanation: Any query about shipping to hotels, including missing hotel deliveries or refund policies for hotel deliveries, maps to "check_shipping_policies" (primary) and "report_missing_package" (secondary).
Output: {"primary_intent": "check_shipping_policies", "secondary_intent": "report_missing_package"}
"""
    
    suggestions_str = ""
    if top_suggestions:
        suggestions_str = "\nClassifier Guidance:\nOur statistical classifier is unsure but predicts the following candidate intents (ordered by probability):\n"
        for rank, (intent, desc, prob) in enumerate(top_suggestions, 1):
            suggestions_str += f"{rank}. **{intent}** (Confidence: {prob:.4f}): {desc}\n"
        suggestions_str += "\nUse this guidance to prioritize these candidate intents if they fit the query. If none of these candidate intents are correct, choose from the other valid intents below.\n"

    prompt = f"""You are a precise e-commerce query routing assistant. 
Your task is to classify the user's support query into one (or at most two) of the following 34 valid intents.

Valid Intents & Descriptions:
{intents_desc}
{suggestions_str}
Rules:
1. Analyze the query carefully. Select the single best matching intent key and set it as "primary_intent".
2. If the query is genuinely ambiguous and matches two intents, select the second intent key and set it as "secondary_intent". Otherwise, set "secondary_intent" to null.
3. You must output ONLY a JSON object matching the JSON schema.
4. The values for the keys must be selected strictly from the 34 valid intent names above.

{few_shot_examples}

User support query: "{query}"
"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "format": ollama_schema,
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "num_predict": 100
                }
            },
            timeout=30
        )
        response.raise_for_status()
        res_json = response.json()
        output_text = res_json.get("response", "").strip()
        data = json.loads(output_text)
        
        primary = data.get("primary_intent")
        secondary = data.get("secondary_intent")
        
        if primary not in intents_list:
            primary = "other_query"
        if secondary not in intents_list:
            secondary = None
            
        return primary, secondary
    except Exception as e:
        print(f"Error calling Ollama fallback: {e}")
        return "other_query", None

def retrieve(query, top_k=3):
    (
        chunks_df,
        embedder,
        index,
        classifier_data,
        all_vectors,
        intents_list,
        intents_desc,
        intent_to_desc,
        intent_to_samples,
        intents_schema
    ) = load_intent_resources()

    # 1. Classify the user query intent
    clf = classifier_data["classifier"]
    le = classifier_data["label_encoder"]
    
    # Embed query (with BGE search instruction)
    search_query = "Represent this sentence for searching relevant passages: " + query
    query_embedding = embedder.encode(
        [search_query],
        convert_to_numpy=True
    ).astype("float32")
    
    # Normalize query embedding
    faiss.normalize_L2(query_embedding)
    
    # Predict intent probabilities
    probs = clf.predict_proba(query_embedding)[0]
    sorted_idxs = np.argsort(probs)[::-1]
    
    top1_idx = sorted_idxs[0]
    top1_prob = probs[top1_idx]
    top1_intent = le.inverse_transform([top1_idx])[0]
    
    top2_idx = sorted_idxs[1]
    top2_prob = probs[top2_idx]
    top2_intent = le.inverse_transform([top2_idx])[0]
    
    margin = top1_prob - top2_prob
    
    search_all = False
    
    # Check if we should fallback to local Qwen LLM router
    is_llm_fallback = (margin <= 0.35) and (top1_prob < 0.13)
    
    if is_llm_fallback:
        # Cascade to LLM router with Classifier Guidance
        top_suggestions = []
        for i in range(min(3, len(sorted_idxs))):
            idx = sorted_idxs[i]
            intent_name = le.inverse_transform([idx])[0]
            prob = float(probs[idx])
            desc = intent_to_desc.get(intent_name, "")
            top_suggestions.append((intent_name, desc, prob))
            
        primary, secondary = get_llm_intent(query, intents_list, intents_desc, top_suggestions=top_suggestions)
        predicted_intent_list = [primary]
        if secondary:
            predicted_intent_list.append(secondary)
    else:
        # Use Logistic Regression with Cumulative Probability Mass Routing
        # Route to top classes until cumulative probability >= 0.50 (min 1, max 3)
        predicted_intent_list = []
        cum_prob = 0.0
        for idx in sorted_idxs:
            intent_name = le.inverse_transform([idx])[0]
            prob = float(probs[idx])
            predicted_intent_list.append(intent_name)
            cum_prob += prob
            if cum_prob >= 0.50 or len(predicted_intent_list) >= 3:
                break
            
    # Build intent table data
    intents_table_data = []
    for idx in sorted_idxs:
        intent_name = le.inverse_transform([idx])[0]
        lr_score = float(probs[idx])
        is_selected = intent_name in predicted_intent_list
        
        if is_selected:
            if is_llm_fallback:
                score = 1.0 if intent_name == primary else 0.5
            else:
                score = lr_score
            selected_str = "Yes"
        else:
            score = lr_score
            selected_str = "No"
            
        desc = intent_to_desc.get(intent_name, "")
        samples = intent_to_samples.get(intent_name, [])
        samples_str = "\n".join([f"* {q}" for q in samples[:3]]) if samples else "No sample queries"
        
        intents_table_data.append({
            "intent_id": intent_name,
            "confidence": score,
            "description": desc,
            "is_selected": selected_str,
            "intent_metadata": samples_str,
            "raw_score": lr_score,
            "is_selected_bool": is_selected
        })
        
    # Sort: selected intents first, then by raw_score descending
    intents_table_data = sorted(
        intents_table_data,
        key=lambda x: (1 if x["is_selected_bool"] else 0, x["raw_score"]),
        reverse=True
    )
    
    # 2. Apply metadata filtering based on predicted intent list
    if search_all:
        filtered_df = chunks_df
    else:
        filtered_df = chunks_df[chunks_df["intents"].apply(lambda x: any(intent in predicted_intent_list for intent in x))]
        
    # Fallback to all chunks if filtering returns nothing
    if filtered_df.empty:
        filtered_df = chunks_df
        
    filtered_indices = filtered_df.index.tolist()
    
    # 3. Perform Vector search manually on the filtered subset for exact cosine similarity
    filtered_vectors = all_vectors[filtered_indices]
    similarities = np.dot(filtered_vectors, query_embedding.T).flatten()
    
    # Map all filtered chunks to their bi-encoder score
    chunk_to_bi_score = {}
    for local_idx, score in enumerate(similarities):
        global_idx = filtered_indices[local_idx]
        cid = chunks_df.iloc[global_idx]["chunk_id"]
        chunk_to_bi_score[cid] = float(score)
        
    # Get top-k matches
    top_indices_local = np.argsort(similarities)[::-1][:top_k]
    
    retrieved_chunks = []
    for local_idx in top_indices_local:
        score = similarities[local_idx]
        global_idx = filtered_indices[local_idx]
        row = chunks_df.iloc[global_idx]
        
        chunk_text = row["chunk"]
        meta = row.get("metadata")
        if isinstance(meta, dict):
            chunk_type = meta.get("chunk_type")
            if chunk_type == "table" and meta.get("table_markdown"):
                chunk_text = f"{row['chunk']}\n\n{meta['table_markdown']}"
            elif chunk_type == "list" and meta.get("list_markdown"):
                chunk_text = meta["list_markdown"]
                
        formatted_chunk = f"Title: {row['chunk_title']}\nContent: {chunk_text}"
        
        retrieved_chunks.append({
            "chunk": formatted_chunk,
            "score": float(score),
            "intent": ", ".join(predicted_intent_list),
            "chunk_id": row["chunk_id"],
            "source_file": row["source_file"],
            "chunk_title": row["chunk_title"],
            "chunk_text": chunk_text
        })
        
    # Build all linked chunks for predicted intents
    all_linked_chunks = []
        
    linked_chunks = []
    for intent in predicted_intent_list:
        for entry in intents_schema:
            if entry["intent"] == intent:
                for cid in entry["source_chunks"]:
                    match = chunks_df[chunks_df["chunk_id"] == cid]
                    if not match.empty:
                        row = match.iloc[0]
                        src_file = row["source_file"]
                        title = row["chunk_title"]
                        
                        linked_chunks.append({
                            "intent": intent,
                            "chunk_id": cid,
                            "chunk_title": title,
                            "source_file": src_file
                        })
                        
                        all_linked_chunks.append({
                            "chunk_id": cid,
                            "from_intent_id": intent,
                            "parent_page": src_file,
                            "chunk_title": title,
                            "content": row["chunk"],
                            "chunk_type": row.get("metadata", {}).get("chunk_type") if isinstance(row.get("metadata"), dict) else "text",
                            "table_markdown": row.get("metadata", {}).get("table_markdown") if isinstance(row.get("metadata"), dict) else None,
                            "list_markdown": row.get("metadata", {}).get("list_markdown") if isinstance(row.get("metadata"), dict) else None
                        })
                    else:
                        linked_chunks.append({
                            "intent": intent,
                            "chunk_id": cid,
                            "chunk_title": "Unknown",
                            "source_file": "Unknown"
                        })
                        
    return {
        "candidate_results": retrieved_chunks,
        "predicted_intents": intents_table_data,
        "linked_chunks": linked_chunks,
        "chunk_to_bi_score": chunk_to_bi_score,
        "all_linked_chunks": all_linked_chunks
    }
