import os
import json
import torch
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder
from transformers import AutoTokenizer, AutoModelForSequenceClassification

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
    
chunk_to_intent = {}
for entry in intents_schema:
    intent_name = entry["intent"]
    for cid in entry["source_chunks"]:
        chunk_to_intent[cid] = intent_name
        
chunks_df["intent"] = chunks_df["chunk_id"].map(chunk_to_intent).fillna("other_query")

# Build FAISS Index (for fallback/global search if needed)
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)
print(f"Indexed {index.ntotal} chunks")

# 2. Load Models
print("Loading BGE embedding model...")
embed_model = SentenceTransformer('BAAI/bge-base-en-v1.5')

print("Loading CrossEncoder reranker...")
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# 3. Load BERT Classifier
BERT_DIR = os.path.join(PIPELINE_DIR, "..", "generator_streamlit", "bert_classifier")
print(f"Loading BERT classifier from {BERT_DIR}...")
bert_tokenizer = AutoTokenizer.from_pretrained(BERT_DIR)
bert_model = AutoModelForSequenceClassification.from_pretrained(BERT_DIR)
bert_model.eval()

# Load classes metadata
with open(os.path.join(BERT_DIR, "metadata.json"), "r", encoding="utf-8") as f:
    meta = json.load(f)
classes = meta["classes"]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
bert_model = bert_model.to(device)

# 4. Metrics Variables
INITIAL_K = 15
FINAL_K = 3
total_queries = len(qa_df)

hits = 0
precision_sum = 0
recall_sum = 0
mrr_sum = 0

correct_intents = 0
missed_queries_list = []

# 5. Evaluation Loop
print("Starting evaluation on 100 queries...")
for idx_row, row in qa_df.iterrows():
    question = row['question']
    query = "Represent this sentence for searching relevant passages: " + question
    true_chunk_id = row['reference_chunk_id']
    true_intent = row['intent']

    # Predict intent using BERT
    with torch.no_grad():
        inputs = bert_tokenizer(
            question,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=64
        ).to(device)
        
        outputs = bert_model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1).cpu().numpy()[0]
        
    sorted_idxs = np.argsort(probs)[::-1]
    top1_idx = sorted_idxs[0]
    top1_prob = probs[top1_idx]
    predicted_intent = classes[top1_idx]
    
    # Check intent classification
    is_correct_intent = (predicted_intent == true_intent)
    if is_correct_intent:
        correct_intents += 1
        
    # Set search intent list (with global search fallback disabled)
    search_all = False
    top2_idx = sorted_idxs[1]
    top2_prob = probs[top2_idx]
    if (top1_prob - top2_prob) <= 0.2:
        predicted_intent_list = [predicted_intent, classes[top2_idx]]
    else:
        predicted_intent_list = [predicted_intent]

    # Apply metadata filtering
    if search_all:
        filtered_df = chunks_df
    else:
        filtered_df = chunks_df[chunks_df["intent"].isin(predicted_intent_list)]
        
    if filtered_df.empty:
        filtered_df = chunks_df
        
    filtered_indices = filtered_df.index.tolist()
    
    # Perform vector search on the filtered subset
    query_embedding = embed_model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_embedding)
    
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
        meta_chunk = chunk_row.get("metadata")
        if isinstance(meta_chunk, dict):
            if meta_chunk.get("chunk_type") == "table" and meta_chunk.get("table_markdown"):
                chunk_text = f"{chunk_row['chunk']}\n\n{meta_chunk['table_markdown']}"
            elif meta_chunk.get("chunk_type") == "list" and meta_chunk.get("list_markdown"):
                chunk_text = meta_chunk["list_markdown"]
        formatted_chunk = f"Title: {chunk_row['chunk_title']}\nContent: {chunk_text}"
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
    final_ids = [x[0] for x in reranked[:FINAL_K]]

    # Hit / Relevance
    relevant_found = int(true_chunk_id in final_ids)
    if relevant_found == 0:
        missed_queries_list.append({
            "question": question,
            "true_chunk": true_chunk_id,
            "true_intent": true_intent,
            "predicted_intent": predicted_intent,
            "retrieved": [(x[0], x[1], x[2]) for x in reranked[:FINAL_K]]
        })

    hits += relevant_found
    precision_sum += relevant_found / FINAL_K
    recall_sum += relevant_found / 1

    # MRR
    reciprocal_rank = 0
    for rank, chunk_id in enumerate(final_ids):
        if chunk_id == true_chunk_id:
            reciprocal_rank = 1 / (rank + 1)
            break
    mrr_sum += reciprocal_rank

# 6. Output Metrics
intent_accuracy = correct_intents / total_queries
precision_at_k = precision_sum / total_queries
recall_at_k = recall_sum / total_queries
hit_rate = hits / total_queries
mrr = mrr_sum / total_queries

print("\n========== Rebuilt Evaluation Results (BERT Classifier) ==========\n")
print(f"Total Queries                  : {total_queries}")
print(f"Intent Classification Accuracy : {intent_accuracy:.4f} ({correct_intents}/{total_queries})")
print(f"Precision@3                    : {precision_at_k:.4f}")
print(f"Recall@3                       : {recall_at_k:.4f}")
print(f"Hit Rate@3                     : {hit_rate:.4f}")
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
print("==================================================================\n")
