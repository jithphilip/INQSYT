import pandas as pd
import numpy as np
import faiss
import pickle
import os
import re
from sentence_transformers import SentenceTransformer, CrossEncoder

def generate_topic(row):
    meta = row.get("metadata", {})
    cat_path = meta.get("category_path", "")
    
    parts = [p.strip() for p in cat_path.split(" > ")]
    if len(parts) >= 2:
        doc_name = parts[1]
    else:
        doc_name = row["source_file"]
        
    doc_name = re.sub(r"\(\d+\)", "", doc_name)
    doc_name = doc_name.replace(".md", "").strip()
    doc_name = re.sub(r"that Shows a$", "that Shows as Delivered", doc_name)
    doc_name = re.sub(r"Companies No$", "Companies Not Affiliated with Amazon", doc_name)
    doc_name = re.sub(r"Text Up$", "Text Updates", doc_name)
    doc_name = re.sub(r"Shipment Tra$", "Shipment Tracking", doc_name)
    
    title = row["chunk_title"].strip()
    title = re.sub(r"^\d+\s*[-.]\s*", "", title).strip()
    
    if title.lower() in doc_name.lower():
        topic = f"Topic: {doc_name}"
    elif doc_name.lower() in title.lower():
        topic = f"Topic: {title}"
    else:
        topic = f"Topic: {doc_name} - {title}"
        
    return topic

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.dirname(CURRENT_DIR)

# 1. Load datasets
chunks_df = pd.read_json(os.path.join(PIPELINE_DIR, "data", "Chunks.jsonl"), lines=True)
qa_df = pd.read_csv(os.path.join(PIPELINE_DIR, "data", "qa_dataset.csv"))
embeddings = np.load(os.path.join(PIPELINE_DIR, "embeddings", "chunk_embeddings.npy")).astype("float32")

faiss.normalize_L2(embeddings)

# Load intents schema and map each chunk_id to its intent
import json
with open(os.path.join(PIPELINE_DIR, "data", "intents_schema.json"), "r", encoding="utf-8") as f:
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

# Build FAISS Index (for fallback/global search if needed)
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)
print(f"Indexed {index.ntotal} chunks")

# 2. Load Models
embed_model = SentenceTransformer('BAAI/bge-base-en-v1.5')
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Load Classifier
CLASSIFIER_PATH = os.path.join(PIPELINE_DIR, "..", "generator_streamlit", "intent_classifier.pkl")
with open(CLASSIFIER_PATH, "rb") as f:
    classifier_data = pickle.load(f)
clf = classifier_data["classifier"]
le = classifier_data["label_encoder"]

# 3. Metrics Variables
INITIAL_K = 15
FINAL_K = 3
total_queries = len(qa_df)

hits = 0
precision_sum = 0
recall_sum = 0
mrr_sum = 0

correct_intents = 0
correct_routing = 0
total_retrieved_chunks = 0
missed_queries_list = []

# 4. Evaluation Loop
for idx_row, row in qa_df.iterrows():
    question = row['question']
    query = "Represent this sentence for searching relevant passages: " + question
    true_chunk_id = row['reference_chunk_id']
    true_intent = row['intent']

    # Embedding
    query_embedding = embed_model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_embedding)

    # Intent Classification
    probs = clf.predict_proba(query_embedding)[0]
    sorted_idxs = np.argsort(probs)[::-1]
    
    top1_idx = sorted_idxs[0]
    top1_prob = probs[top1_idx]
    predicted_intent = le.inverse_transform([top1_idx])[0]
    
    # Check intent classification
    is_correct_intent = (predicted_intent == true_intent)
    if is_correct_intent:
        correct_intents += 1
        
    is_correct_routing = (predicted_intent in chunk_to_intents.get(true_chunk_id, []))
    if is_correct_routing:
        correct_routing += 1
        
    # Set search intent list (with global search fallback disabled)
    search_all = False
    top2_idx = sorted_idxs[1]
    top2_prob = probs[top2_idx]
    if (top1_prob - top2_prob) <= 0.2:
        predicted_intent_list = [predicted_intent, le.inverse_transform([top2_idx])[0]]
    else:
        predicted_intent_list = [predicted_intent]

    # Apply metadata filtering
    if search_all:
        filtered_df = chunks_df
    else:
        filtered_df = chunks_df[chunks_df["intents"].apply(lambda x: any(intent in predicted_intent_list for intent in x))]
        
    if filtered_df.empty:
        filtered_df = chunks_df
        
    filtered_indices = filtered_df.index.tolist()
    
    # Perform vector search on the filtered subset
    filtered_embeddings = embeddings[filtered_indices]
    similarities = np.dot(filtered_embeddings, query_embedding.T).flatten()
    
    # Sort and take top INITIAL_K
    top_k_indices_filtered = np.argsort(similarities)[::-1][:INITIAL_K]
    retrieved_indices = [filtered_indices[idx] for idx in top_k_indices_filtered]
    
    retrieved_ids = []
    retrieved_bi_scores = []
    for idx in retrieved_indices:
        retrieved_ids.append(chunks_df.iloc[idx]['chunk_id'])
        # Similarity is dot product of normalized vectors
        b_score = float(np.dot(embeddings[idx], query_embedding.flatten()))
        retrieved_bi_scores.append(b_score)
    
    id_to_bi_score = dict(zip(retrieved_ids, retrieved_bi_scores))
    
    # Fetch chunk texts for reranking
    retrieved_chunks = []
    for idx in retrieved_indices:
        chunk_row = chunks_df.iloc[idx]
        chunk_text = chunk_row["chunk"]
        meta = chunk_row.get("metadata")
        if isinstance(meta, dict):
            if meta.get("chunk_type") == "table" and meta.get("table_markdown"):
                chunk_text = f"{chunk_row['chunk']}\n\n{meta['table_markdown']}"
            elif meta.get("chunk_type") == "list" and meta.get("list_markdown"):
                chunk_text = meta["list_markdown"]
        topic = generate_topic(chunk_row)
        formatted_chunk = f"{topic}\nTitle: {chunk_row['chunk_title']}\nContent: {chunk_text}"
        retrieved_chunks.append(formatted_chunk)

    # Re-ranking
    pairs = [[question, chunk] for chunk in retrieved_chunks]
    if len(pairs) > 0:
        rerank_scores = reranker.predict(pairs)
    else:
        rerank_scores = []
    
    # Combine chunk ids, bi-encoder scores, and rerank scores
    reranked = []
    for cid, r_score in zip(retrieved_ids, rerank_scores):
        b_score = id_to_bi_score.get(cid, 0.0)
        reranked.append((cid, b_score, float(r_score)))
        
    # Sort by rerank score descending
    reranked = sorted(reranked, key=lambda x: x[2], reverse=True)
    
    # Apply Dynamic K Thresholding (min_k=3, max_k=5, margin=4.0)
    final_ids = []
    if reranked:
        top_score = reranked[0][2]
        for i, (cid, b_score, r_score) in enumerate(reranked[:5]):
            if i < 3 or (top_score - r_score) <= 4.0:
                final_ids.append(cid)
                
    total_retrieved_chunks += len(final_ids)
 
    # Hit / Relevance
    relevant_found = int(true_chunk_id in final_ids)
    if relevant_found == 0:
        missed_queries_list.append({
            "question": question,
            "true_chunk": true_chunk_id,
            "true_intent": true_intent,
            "predicted_intent": predicted_intent,
            "retrieved": [(x[0], x[1], x[2]) for x in reranked[:len(final_ids)]]
        })
 
    hits += relevant_found
    precision_sum += relevant_found / len(final_ids) if final_ids else 0.0
    recall_sum += relevant_found / 1

    # MRR
    reciprocal_rank = 0
    for rank, chunk_id in enumerate(final_ids):
        if chunk_id == true_chunk_id:
            reciprocal_rank = 1 / (rank + 1)
            break
    mrr_sum += reciprocal_rank

# 5. Output Metrics
intent_accuracy = correct_intents / total_queries
routing_accuracy = correct_routing / total_queries
precision_at_k = precision_sum / total_queries
recall_at_k = recall_sum / total_queries
hit_rate = hits / total_queries
mrr = mrr_sum / total_queries
avg_chunks = total_retrieved_chunks / total_queries
 
print("\n========== Rebuilt Evaluation Results ==========\n")
print(f"Total Queries                  : {total_queries}")
print(f"Intent Classification Accuracy : {intent_accuracy:.4f} ({correct_intents}/{total_queries})")
print(f"Routing Accuracy (Overlap-Aware): {routing_accuracy:.4f} ({correct_routing}/{total_queries})")
print(f"Average Chunks Retrieved       : {avg_chunks:.4f}")
print(f"Precision@Dynamic K            : {precision_at_k:.4f}")
print(f"Recall@Dynamic K               : {recall_at_k:.4f}")
print(f"Hit Rate                       : {hit_rate:.4f}")
print(f"MRR                            : {mrr:.4f}")
print(f"Missed Queries                 : {len(missed_queries_list)}")

if missed_queries_list:
    print("\nDetailed Missed Queries:")
    for m in missed_queries_list:
        print(f"  - Query: '{m['question']}'")
        print(f"    True Chunk: '{m['true_chunk']}' | True Intent: '{m['true_intent']}'")
        print(f"    Predicted Intent: '{m['predicted_intent']}'")
        print(f"    Retrieved:")
        for rank, (cid, b_score, r_score) in enumerate(m['retrieved']):
            print(f"      * Rank {rank+1}: {cid} (Bi-Encoder Score: {b_score:.4f}, Reranker Score: {r_score:.4f})")
        print()
print("================================================\n")
