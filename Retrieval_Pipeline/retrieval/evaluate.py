import pandas as pd
import numpy as np
import faiss

from sentence_transformers import (
    SentenceTransformer,
    CrossEncoder
)

import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.dirname(CURRENT_DIR)

# Load datasets
chunks_df = pd.read_csv(os.path.join(PIPELINE_DIR, "data", "chunks.csv"))

qa_df = pd.read_csv(os.path.join(PIPELINE_DIR, "data", "qa_dataset.csv"))

embeddings = np.load(os.path.join(PIPELINE_DIR, "embeddings", "chunk_embeddings.npy"))


embeddings = embeddings.astype("float32")

faiss.normalize_L2(embeddings)

# =========================
# BUILD FAISS INDEX
# Cosine similarity using Inner Product
# =========================

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

print(f"Indexed {index.ntotal} chunks")

# =========================
# LOAD MODELS
# =========================

embed_model = SentenceTransformer('BAAI/bge-base-en-v1.5')

reranker = CrossEncoder(
    'cross-encoder/ms-marco-MiniLM-L-6-v2'
)

# =========================
# METRICS VARIABLES
# =========================

INITIAL_K = 15

FINAL_K = 10

total_queries = len(qa_df)

hits = 0

precision_sum = 0

recall_sum = 0

mrr_sum = 0

# =========================
# EVALUATION LOOP
# =========================

for _, row in qa_df.iterrows():

    question = row['question']
    query = "Represent this sentence for searching relevant passages: " + question

    true_chunk_id = row['reference_chunk_id']

    # =========================
    # QUERY EMBEDDING
    # =========================

    query_embedding = embed_model.encode(
        [query],
        convert_to_numpy=True
    )

    query_embedding = query_embedding.astype("float32")

    # Normalize query embedding
    faiss.normalize_L2(query_embedding)

    # =========================
    # INITIAL RETRIEVAL
    # =========================

    scores, indices = index.search(query_embedding,INITIAL_K)

    retrieved_indices = indices[0]

    retrieved_ids = [chunks_df.iloc[idx]['chunk_id'] for idx in retrieved_indices]

    # =========================
    # FETCH RETRIEVED CHUNKS
    # =========================

    retrieved_chunks = [chunks_df.iloc[idx]['chunk_text'] for idx in retrieved_indices]

    # =========================
    # PREPARE QUERY-CHUNK PAIRS
    # =========================

    pairs = [
        [question, chunk]
        for chunk in retrieved_chunks
    ]

    # =========================
    # RE-RANKING
    # =========================

    rerank_scores = reranker.predict(pairs)

    reranked = sorted(
        zip(retrieved_ids, rerank_scores),
        key=lambda x: x[1],
        reverse=True
    )

    final_ids = [x[0] for x in reranked[:FINAL_K]]
    

    # =========================
    # HIT / RELEVANCE
    # =========================

    relevant_found = int(
        true_chunk_id in final_ids
    )
    if relevant_found == 0:
        print("\nMISSED QUERY:")
        print(question)
        print("TRUE CHUNK:", true_chunk_id)
        print("RETRIEVED:", final_ids)

    hits += relevant_found

    # =========================
    # PRECISION@K
    # =========================

    precision_sum += relevant_found / FINAL_K

    # =========================
    # RECALL@K
    # =========================

    recall_sum += relevant_found / 1

    # =========================
    # MRR
    # =========================

    reciprocal_rank = 0

    for rank, chunk_id in enumerate(final_ids):

        if chunk_id == true_chunk_id:

            reciprocal_rank = 1 / (rank + 1)

            break

    mrr_sum += reciprocal_rank

# =========================
# FINAL METRICS
# =========================

precision_at_k = precision_sum / total_queries

recall_at_k = recall_sum / total_queries

hit_rate = hits / total_queries

mrr = mrr_sum / total_queries

# =========================
# RESULTS
# =========================

print("\n========== Evaluation Results ==========\n")

print(f"Total Queries      : {total_queries}")

print(f"Precision@{FINAL_K}      : {precision_at_k:.4f}")

print(f"Recall@{FINAL_K}         : {recall_at_k:.4f}")

print(f"Hit Rate@{FINAL_K}       : {hit_rate:.4f}")

print(f"MRR                : {mrr:.4f}")

print("\n========================================\n")

# # =========================
# # EVALUATION LOOP
# # =========================

# for _, row in qa_df.iterrows():

#     question = row['question']

#     query = (
#         "Represent this sentence for searching relevant passages: "
#         + question
#     )

#     true_chunk_id = row['reference_chunk_id']

#     # =========================
#     # QUERY EMBEDDING
#     # =========================

#     query_embedding = embed_model.encode(
#         [query],
#         convert_to_numpy=True
#     )

#     query_embedding = query_embedding.astype("float32")

#     faiss.normalize_L2(query_embedding)

#     # =========================
#     # DIRECT FAISS RETRIEVAL
#     # =========================

#     scores, indices = index.search(
#         query_embedding,
#         FINAL_K
#     )

#     retrieved_indices = indices[0]

#     # =========================
#     # MAP TO CHUNK IDS
#     # =========================

#     final_ids = [
#         chunks_df.iloc[idx]['chunk_id']
#         for idx in retrieved_indices
#     ]

#     # =========================
#     # HIT / RELEVANCE
#     # =========================

#     relevant_found = int(
#         true_chunk_id in final_ids
#     )

#     hits += relevant_found

#     # =========================
#     # PRECISION@K
#     # =========================

#     precision_sum += relevant_found / FINAL_K

#     # =========================
#     # RECALL@K
#     # =========================

#     recall_sum += relevant_found

#     # =========================
#     # MRR
#     # =========================

#     reciprocal_rank = 0

#     for rank, chunk_id in enumerate(final_ids):

#         if chunk_id == true_chunk_id:

#             reciprocal_rank = 1 / (rank + 1)

#             break

#     mrr_sum += reciprocal_rank

# # # =========================
# # # FINAL METRICS
# # # =========================

# precision_at_k = precision_sum / total_queries

# recall_at_k = recall_sum / total_queries

# hit_rate = hits / total_queries

# mrr = mrr_sum / total_queries


# print("\n========== Evaluation Results ==========\n")

# print(f"Total Queries      : {total_queries}")

# print(f"Precision@{FINAL_K}      : {precision_at_k:.4f}")

# print(f"Recall@{FINAL_K}         : {recall_at_k:.4f}")

# print(f"Hit Rate@{FINAL_K}       : {hit_rate:.4f}")

# print(f"MRR                : {mrr:.4f}")

# print("\n========================================\n")
