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
PIPELINE_DIR = os.path.join(ws_dir, "Retrieval_Pipeline")
GEN_DIR = os.path.join(ws_dir, "generator_streamlit")

# 1. Load resources
print("Loading data...")
qa_df = pd.read_csv(os.path.join(ws_dir, "Main_Data", "Evaluation", "eval_dataset_v1.csv"))
chunks_df = pd.read_json(os.path.join(ws_dir, "Main_Data", "Chunks", "chunks_v1_cleaned.jsonl"), lines=True)

with open(os.path.join(ws_dir, "Main_Data", "Intents", "intents_schema_v1.json"), "r", encoding="utf-8") as f:
    intents_schema = json.load(f)

# Reconstruct chunk mappings
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

# Load models
print("Loading BGE embedder...")
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
index = faiss.read_index(os.path.join(GEN_DIR, "faiss_index_v1_cleaned.bin"))
all_vectors = np.array([index.reconstruct(i) for i in range(index.ntotal)]).astype("float32")

print("Loading CrossEncoder reranker...")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

print("Loading Logistic Regression classifier...")
with open(os.path.join(GEN_DIR, "intent_classifier.pkl"), "rb") as f:
    classifier_data = pickle.load(f)
clf = classifier_data["classifier"]
le = classifier_data["label_encoder"]

def get_hybrid_intents(question, query_embedding):
    probs = clf.predict_proba(query_embedding)[0]
    sorted_idxs = np.argsort(probs)[::-1]
    
    top1_idx = sorted_idxs[0]
    top1_prob = probs[top1_idx]
    top1_intent = le.inverse_transform([top1_idx])[0]
    
    top2_idx = sorted_idxs[1]
    top2_prob = probs[top2_idx]
    
    margin = top1_prob - top2_prob
    is_llm_fallback = (margin <= 0.35) and (top1_prob < 0.13)
    
    if is_llm_fallback:
        # Classifier-Guided LLM Routing: pass top suggestions
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
        # Cumulative Probability Mass Routing (Dynamic Soft-N)
        predicted = []
        cum_prob = 0.0
        for idx in sorted_idxs:
            intent_name = le.inverse_transform([idx])[0]
            prob = float(probs[idx])
            predicted.append(intent_name)
            cum_prob += prob
            if cum_prob >= 0.50 or len(predicted) >= 3:
                break
            
    return predicted, bool(is_llm_fallback), float(top1_prob), float(margin)

# Precompute query embeddings
print("Precomputing query embeddings...")
query_embeddings = []
for idx in range(len(qa_df)):
    question = qa_df.iloc[idx]['question']
    search_query = "Represent this sentence for searching relevant passages: " + question
    emb = embedder.encode([search_query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(emb)
    query_embeddings.append(emb)

k_values = [1, 3, 5, 7]  # Evaluate for K sweeps
evaluation_report = {}

for k in k_values:
    print(f"\nRunning evaluation for k = {k}...")
    hit_count = 0
    mrr_sum = 0.0
    failed_cases = []
    
    for idx in range(len(qa_df)):
        row = qa_df.iloc[idx]
        question = row['question']
        true_chunk_id = row['reference_chunk_id']
        true_intent = row['intent']
        emb = query_embeddings[idx]
        
        # 1. Routing
        predicted_intents, is_fallback, top1_prob, margin = get_hybrid_intents(question, emb)
        
        # 2. Filter chunks
        filtered_df = chunks_df[chunks_df["intents"].apply(lambda x: any(intent in predicted_intents for intent in x))]
        if filtered_df.empty:
            filtered_df = chunks_df
        filtered_indices = filtered_df.index.tolist()
        
        # 3. Vector search
        filtered_vectors = all_vectors[filtered_indices]
        similarities = np.dot(filtered_vectors, emb.T).flatten()
        
        # Get candidate results
        candidates_count = max(15, k * 2)
        top_indices_local = np.argsort(similarities)[::-1][:candidates_count]
        
        candidate_results = []
        chunk_to_bi_score = {}
        for local_idx in top_indices_local:
            global_idx = filtered_indices[local_idx]
            crow = chunks_df.iloc[global_idx]
            
            chunk_text = crow["chunk"]
            meta = crow.get("metadata")
            if isinstance(meta, dict):
                chunk_type = meta.get("chunk_type")
                if chunk_type == "table" and meta.get("table_markdown"):
                    chunk_text = f"{crow['chunk']}\n\n{meta['table_markdown']}"
                elif chunk_type == "list" and meta.get("list_markdown"):
                    chunk_text = meta["list_markdown"]
            
            formatted_chunk = f"Title: {crow['chunk_title']}\nContent: {chunk_text}"
            candidate_results.append({
                "chunk_id": crow["chunk_id"],
                "chunk": formatted_chunk,
                "chunk_title": crow["chunk_title"],
                "chunk_type": crow.get("metadata", {}).get("chunk_type") if isinstance(crow.get("metadata"), dict) else "text",
                "table_markdown": crow.get("metadata", {}).get("table_markdown") if isinstance(crow.get("metadata"), dict) else None,
                "list_markdown": crow.get("metadata", {}).get("list_markdown") if isinstance(crow.get("metadata"), dict) else None,
                "bi_score": float(similarities[local_idx])
            })
            chunk_to_bi_score[crow["chunk_id"]] = float(similarities[local_idx])
            
        # 4. Rerank
        all_linked_chunks = []
        for intent in predicted_intents:
            for entry in intents_schema:
                if entry["intent"] == intent:
                    for cid in entry["source_chunks"]:
                        match = chunks_df[chunks_df["chunk_id"] == cid]
                        if not match.empty:
                            crow = match.iloc[0]
                            all_linked_chunks.append({
                                "chunk_id": cid,
                                "chunk_title": crow["chunk_title"],
                                "content": crow["chunk"],
                                "chunk_type": crow.get("metadata", {}).get("chunk_type") if isinstance(crow.get("metadata"), dict) else "text",
                                "table_markdown": crow.get("metadata", {}).get("table_markdown") if isinstance(crow.get("metadata"), dict) else None,
                                "list_markdown": crow.get("metadata", {}).get("list_markdown") if isinstance(crow.get("metadata"), dict) else None
                            })
                            
        chunk_to_rerank_score = {}
        if all_linked_chunks:
            pairs = []
            for item in all_linked_chunks:
                chunk_text = item["content"]
                if item["chunk_type"] == "table" and item["table_markdown"]:
                    chunk_text = f"{item['content']}\n\n{item['table_markdown']}"
                elif item["chunk_type"] == "list" and item["list_markdown"]:
                    chunk_text = item["list_markdown"]
                formatted_chunk = f"Title: {item['chunk_title']}\nContent: {chunk_text}"
                pairs.append([question, formatted_chunk])
                
            rerank_scores = reranker.predict(pairs)
            for item, rerank_score in zip(all_linked_chunks, rerank_scores):
                chunk_to_rerank_score[item["chunk_id"]] = float(rerank_score)
                
        for res in candidate_results:
            res["rerank_score"] = chunk_to_rerank_score.get(res["chunk_id"], 0.0)
            
        reranked = sorted(
            candidate_results,
            key=lambda x: x.get("rerank_score", 0.0),
            reverse=True
        )
        
        # Apply Dynamic K Thresholding
        retrieved_chunks = []
        if reranked:
            top_score = reranked[0].get("rerank_score", 0.0)
            min_k = k
            max_k = min(10, k + 2)
            for i, res in enumerate(reranked[:max_k]):
                score = res.get("rerank_score", 0.0)
                if i < min_k or (top_score - score) <= 4.0:
                    retrieved_chunks.append(res)
                    
        # Calculate Hit and Reciprocal Rank
        retrieved_ids = [item["chunk_id"] for item in retrieved_chunks]
        
        hit = 0
        rr = 0.0
        if true_chunk_id in retrieved_ids:
            hit = 1
            hit_count += 1
            rank = retrieved_ids.index(true_chunk_id) + 1
            rr = 1.0 / rank
            mrr_sum += rr
        else:
            # Failure case
            failed_cases.append({
                "question": question,
                "true_intent": true_intent,
                "true_chunk_id": true_chunk_id,
                "predicted_intents": predicted_intents,
                "is_fallback": is_fallback,
                "top1_prob": top1_prob,
                "margin": margin,
                "retrieved_ids": retrieved_ids,
                "retrieved_scores": [{"chunk_id": item["chunk_id"], "bi_score": chunk_to_bi_score.get(item["chunk_id"], 0.0), "rerank_score": item.get("rerank_score", 0.0)} for item in retrieved_chunks]
            })
            
    hit_rate = hit_count / len(qa_df)
    mrr = mrr_sum / len(qa_df)
    
    evaluation_report[k] = {
        "hit_rate": hit_rate,
        "mrr": mrr,
        "failed_count": len(failed_cases),
        "failed_cases": failed_cases
    }
    print(f"k={k} -> Hit Rate: {hit_rate*100:.2f}% | MRR: {mrr:.4f} | Failed: {len(failed_cases)}")

# Print Summary Table
print("\n" + "="*50)
print("NEW HYBRID RETRIEVER EVALUATION RESULTS")
print("="*50)
print(f"| K Value | Hit Rate (Recall@K) | MRR (Mean Reciprocal Rank) | Failed Queries |")
print(f"| :---: | :---: | :---: | :---: |")
for k, report in evaluation_report.items():
    print(f"| K = {k} | {report['hit_rate']*100:.2f}% | {report['mrr']:.4f} | {report['failed_count']} |")
print("="*50 + "\n")

failures_k3 = evaluation_report[3]["failed_cases"]
with open(os.path.join(ws_dir, "scratch", "eval_v3_failures.json"), "w") as f:
    json.dump(evaluation_report, f, indent=2)
print(f"Saved failure details to scratch/eval_v3_failures.json")
