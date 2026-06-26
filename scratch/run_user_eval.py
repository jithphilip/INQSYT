import os
import sys
import json
import numpy as np
import pandas as pd
import faiss
import pickle
from sentence_transformers import SentenceTransformer, CrossEncoder

ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
sys.path.append(ws_dir)
GEN_DIR = os.path.join(ws_dir, "generator_streamlit")

qa_df = pd.read_csv(os.path.join(ws_dir, "Main_Data", "Evaluation", "eval_dataset_v1.csv"))
chunks_df = pd.read_json(os.path.join(ws_dir, "Main_Data", "Chunks", "chunks_v1_cleaned.jsonl"), lines=True)

with open(os.path.join(ws_dir, "Main_Data", "Intents", "intents_schema_v1.json"), "r", encoding="utf-8") as f:
    intents_schema = json.load(f)

chunk_to_intents = {}
for entry in intents_schema:
    intent_name = entry["intent"]
    for cid in entry["source_chunks"]:
        if cid not in chunk_to_intents:
            chunk_to_intents[cid] = []
        chunk_to_intents[cid].append(intent_name)

chunks_df["intents"] = chunks_df["chunk_id"].map(chunk_to_intents)
chunks_df["intents"] = chunks_df["intents"].apply(lambda x: x if isinstance(x, list) else ["other_query"])

intents_list = [entry["intent"] for entry in intents_schema]
intents_desc = ""
for entry in intents_schema:
    intents_desc += f"- **{entry['intent']}**: {entry['description']}\n"
    
intent_to_desc = {entry["intent"]: entry["description"] for entry in intents_schema}

print("Loading Models...")
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
index = faiss.read_index(os.path.join(GEN_DIR, "faiss_index_v1_cleaned_linearised.bin"))
all_vectors = np.array([index.reconstruct(i) for i in range(index.ntotal)]).astype("float32")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

with open(os.path.join(GEN_DIR, "intent_classifier.pkl"), "rb") as f:
    classifier_data = pickle.load(f)
clf = classifier_data["classifier"]
le = classifier_data["label_encoder"]

intent_descriptions_list = list(intent_to_desc.values())
intent_names_list = list(intent_to_desc.keys())
desc_embeddings = embedder.encode(intent_descriptions_list, convert_to_numpy=True).astype("float32")
faiss.normalize_L2(desc_embeddings)

def get_hybrid_intents(question, query_embedding_raw):
    q_emb_norm = query_embedding_raw.copy()
    faiss.normalize_L2(q_emb_norm)
    
    probs = clf.predict_proba(query_embedding_raw)[0]
    sorted_idxs = np.argsort(probs)[::-1]
    
    top1_idx = sorted_idxs[0]
    top1_prob = probs[top1_idx]
    top1_intent = le.inverse_transform([top1_idx])[0]
    
    top2_idx = sorted_idxs[1]
    top2_prob = probs[top2_idx]
    
    margin = top1_prob - top2_prob
    is_llm_fallback = False
    
    # USER CASCADING FUNNEL LOGIC
    if top1_prob > 0.60:
        is_llm_fallback = False
    elif top1_prob < 0.20:
        is_llm_fallback = True
    else:
        # Purgatory Zone (0.20 to 0.60)
        bi_scores = np.dot(desc_embeddings, q_emb_norm.T).flatten()
        best_bi_idx = np.argmax(bi_scores)
        bi_top_intent = intent_names_list[best_bi_idx]
        
        if margin < 0.15:
            is_llm_fallback = True
        elif top1_intent != bi_top_intent:
            is_llm_fallback = True
            
    if is_llm_fallback:
        top_suggestions = []
        for i in range(min(3, len(sorted_idxs))):
            idx = sorted_idxs[i]
            intent_name = le.inverse_transform([idx])[0]
            prob = float(probs[idx])
            desc = intent_to_desc.get(intent_name, "")
            top_suggestions.append((intent_name, desc, prob))
            
        from generator_streamlit.retrieval import get_llm_intent
        primary, secondary = get_llm_intent(question, intents_list, intents_desc, top_suggestions=top_suggestions)
        predicted = [primary]
        if secondary:
            predicted.append(secondary)
    else:
        predicted = []
        cum_prob = 0.0
        for idx in sorted_idxs:
            intent_name = le.inverse_transform([idx])[0]
            prob = float(probs[idx])
            predicted.append(intent_name)
            cum_prob += prob
            if cum_prob >= 0.50 or len(predicted) >= 3:
                break
            
    return predicted, bool(is_llm_fallback)

print("Encoding queries...")
query_embeddings = embedder.encode(qa_df["question"].tolist(), convert_to_numpy=True).astype("float32")

k_values = [1, 3, 5, 7]
hit_rates = {k: 0 for k in k_values}
mrr_scores = {k: [] for k in k_values}
total = len(qa_df)

llm_calls = 0

print("Running E-to-E Evaluation with Cascading Funnel...")
for idx, row in qa_df.iterrows():
    q = row["question"]
    expected_chunk = row["reference_chunk_id"]
    
    q_emb_raw = query_embeddings[idx:idx+1]
    predicted_intents, is_fallback = get_hybrid_intents(q, q_emb_raw)
    
    if is_fallback: llm_calls += 1
    
    filtered_df = chunks_df[chunks_df["intents"].apply(lambda x: any(intent in predicted_intents for intent in x))]
    if filtered_df.empty: filtered_df = chunks_df
    filtered_indices = filtered_df.index.tolist()
    
    q_emb_norm = q_emb_raw.copy()
    faiss.normalize_L2(q_emb_norm)
    filtered_vectors = all_vectors[filtered_indices]
    similarities = np.dot(filtered_vectors, q_emb_norm.T).flatten()
    
    top_k_local = np.argsort(similarities)[::-1][:20]
    
    pairs = []
    chunk_ids = []
    for local_idx in top_k_local:
        global_idx = filtered_indices[local_idx]
        cid = chunks_df.iloc[global_idx]["chunk_id"]
        c_text = chunks_df.iloc[global_idx]["chunk"]
        meta = chunks_df.iloc[global_idx].get("metadata")
        if isinstance(meta, dict) and meta.get("chunk_type") == "table" and meta.get("table_markdown"):
            c_text = f"{c_text}\n\n{meta['table_markdown']}"
        pairs.append([q, c_text])
        chunk_ids.append(cid)
        
    cross_scores = reranker.predict(pairs)
    final_ranked_chunk_ids = [chunk_ids[i] for i in np.argsort(cross_scores)[::-1]]
    
    for k in k_values:
        if expected_chunk in final_ranked_chunk_ids[:k]:
            hit_rates[k] += 1
            rank = final_ranked_chunk_ids[:k].index(expected_chunk) + 1
            mrr_scores[k].append(1.0 / rank)
        else:
            mrr_scores[k].append(0)
            
for k in k_values:
    hr = hit_rates[k] / total * 100
    mrr = sum(mrr_scores[k]) / total
    print(f"K={k}: Hit Rate = {hr:.2f}%, MRR = {mrr:.4f}")
print(f"Total LLM Calls: {llm_calls} ({llm_calls/total*100:.1f}%)")
