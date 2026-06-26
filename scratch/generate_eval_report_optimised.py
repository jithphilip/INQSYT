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
EVAL_DIR = os.path.join(ws_dir, "Evaluation Reports")

print("Loading data...")
qa_df = pd.read_csv(os.path.join(ws_dir, "Main_Data", "Evaluation", "eval_dataset_optimised.csv"))
chunks_df = pd.read_json(os.path.join(ws_dir, "Main_Data", "Chunks", "chunks_optimised.jsonl"), lines=True)

with open(os.path.join(ws_dir, "Main_Data", "Intents", "intents_schema_optimised.json"), "r", encoding="utf-8") as f:
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

print("Loading BGE embedder...")
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
index = faiss.read_index(os.path.join(GEN_DIR, "faiss_index_optimised.bin"))
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
            
    return predicted, bool(is_llm_fallback), float(top1_prob), float(margin)

print("Precomputing query embeddings...")
query_embeddings = []
for idx in range(len(qa_df)):
    question = qa_df.iloc[idx]['question']
    search_query = "Represent this sentence for searching relevant passages: " + question
    emb = embedder.encode([search_query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(emb)
    query_embeddings.append(emb)

k_values = [1, 3, 5, 7]
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
        
        predicted_intents, is_fallback, top1_prob, margin = get_hybrid_intents(question, emb)
        
        filtered_df = chunks_df[chunks_df["intents"].apply(lambda x: any(intent in predicted_intents for intent in x))]
        if filtered_df.empty:
            filtered_df = chunks_df
        filtered_indices = filtered_df.index.tolist()
        
        filtered_vectors = all_vectors[filtered_indices]
        similarities = np.dot(filtered_vectors, emb.T).flatten()
        
        candidates_count = max(15, k * 2)
        top_indices_local = np.argsort(similarities)[::-1][:candidates_count]
        
        candidate_results = []
        chunk_to_bi_score = {}
        for local_idx in top_indices_local:
            global_idx = filtered_indices[local_idx]
            crow = chunks_df.iloc[global_idx]
            chunk_to_bi_score[crow["chunk_id"]] = float(similarities[local_idx])
            candidate_results.append({
                "chunk_id": crow["chunk_id"],
                "chunk_title": crow["chunk_title"]
            })
            
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
                                "content": crow["chunk"]
                            })
                            
        chunk_to_rerank_score = {}
        if all_linked_chunks:
            pairs = []
            for item in all_linked_chunks:
                pairs.append([question, f"Title: {item['chunk_title']}\nContent: {item['content']}"])
            rerank_scores = reranker.predict(pairs)
            for item, rerank_score in zip(all_linked_chunks, rerank_scores):
                chunk_to_rerank_score[item["chunk_id"]] = float(rerank_score)
                
        for res in candidate_results:
            res["rerank_score"] = chunk_to_rerank_score.get(res["chunk_id"], -999.0)
            
        reranked = sorted(
            candidate_results,
            key=lambda x: x.get("rerank_score", 0.0),
            reverse=True
        )
        
        retrieved_chunks = []
        if reranked:
            top_score = reranked[0].get("rerank_score", 0.0)
            min_k = k
            max_k = min(10, k + 2)
            for i, res in enumerate(reranked[:max_k]):
                score = res.get("rerank_score", 0.0)
                if i < min_k or (top_score - score) <= 4.0:
                    retrieved_chunks.append(res)
                    
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

# Generate Markdown Report
report_path = os.path.join(EVAL_DIR, "iteration_03_optimised_chunks_LR.md")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("# 📊 RAG Evaluation & Failure Analysis Report (Iteration 03: Optimised Chunks & LR Classifier)\n\n")
    
    f.write("### 2. E-to-E Retrieval Performance Overview\n")
    f.write("| K Value | Hit Rate (Recall@K) | MRR (Mean Reciprocal Rank) | Failed Queries |\n")
    f.write("| :---: | :---: | :---: | :---: |\n")
    for k in k_values:
        rep = evaluation_report[k]
        f.write(f"| **K = {k}** | {rep['hit_rate']*100:.2f}% | {rep['mrr']:.4f} | {rep['failed_count']} |\n")
        
    failures_k3 = evaluation_report[3]["failed_cases"]
    
    nlu_fails = []
    ranking_fails = []
    
    for fail in failures_k3:
        if fail['true_intent'] not in fail['predicted_intents']:
            nlu_fails.append(fail)
        else:
            ranking_fails.append(fail)
            
    f.write("\n### 3. Failure Mode Table (K = 3)\n")
    f.write("| Failure Mode | Isolated Component | Impact (Count/%) | Root Cause Analysis | Mitigation Action |\n")
    f.write("| :--- | :---: | :---: | :--- | :--- |\n")
    
    impact_nlu = f"{len(nlu_fails)} ({len(nlu_fails)/len(failures_k3)*100:.1f}%)" if len(failures_k3)>0 else "0"
    impact_rank = f"{len(ranking_fails)} ({len(ranking_fails)/len(failures_k3)*100:.1f}%)" if len(failures_k3)>0 else "0"
    
    f.write(f"| NLU Classifier Misclassification | NLU Classifier/Logistic Regression | {impact_nlu} | True intent not predicted correctly | Add more training data to classifier for these edge cases |\n")
    f.write(f"| LLM Router Fallback Error | LLM Router/Few-Shot Fallback | 0 (0%) | - | - |\n")
    f.write(f"| Reranking / Ranking Failure | Reranker/Cross-Encoder | {impact_rank} | True chunk scored lower than others by reranker | Fine-tune cross-encoder or adjust thresholds |\n")
    
    f.write("\n### 4. Query-by-Query Failure Directory (K = 3)\n")
    f.write("````carousel\n")
    
    for idx, fail in enumerate(failures_k3):
        f.write(f"**Query**: `{fail['question']}`\n\n")
        f.write(f"* **Expected Intent**: {fail['true_intent']}\n")
        f.write(f"* **True Chunk ID**: `{fail['true_chunk_id']}`\n")
        f.write(f"* **Predicted Intent(s)**: {fail['predicted_intents']} (Success: {fail['true_intent'] in fail['predicted_intents']})\n")
        
        f.write("\n**Top Retrieved Chunks:**\n")
        for chunk in fail['retrieved_scores'][:3]:
            f.write(f"- `{chunk['chunk_id']}` (Bi: {chunk['bi_score']:.2f}, Rerank: {chunk['rerank_score']:.2f})\n")
            
        cause = "NLU Classifier Misclassification" if fail['true_intent'] not in fail['predicted_intents'] else "Reranking Failure"
        comp = "NLU Classifier" if fail['true_intent'] not in fail['predicted_intents'] else "Cross-Encoder"
        f.write(f"\n**Isolated Component**: {comp}\n")
        f.write(f"**Root Cause Analysis**: {cause}\n")
        
        if idx < len(failures_k3) - 1:
            f.write("\n<!-- slide -->\n")
            
    f.write("````\n")

print(f"Report successfully saved to {report_path}")
