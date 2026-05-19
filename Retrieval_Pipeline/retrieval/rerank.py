import pandas as pd
import numpy as np
import faiss

from sentence_transformers import (
    SentenceTransformer,
    CrossEncoder
)

# Load data
df = pd.read_csv("D:/INQYST/Week 1/Task2 - Retrieval/data/chunks.csv")

embeddings = np.load("D:/INQYST/Week 1/Task2 - Retrieval/embeddings/chunk_embeddings.npy")


# =========================
# NORMALIZE EMBEDDINGS
# (needed for cosine similarity)
# =========================

embeddings = embeddings.astype("float32")

faiss.normalize_L2(embeddings)

# =========================
# CREATE FAISS INDEX
# =========================

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

print(f"Indexed {index.ntotal} chunks")

# =========================
# LOAD MODELS
# =========================

print("Loading embedding model...")

embed_model = SentenceTransformer('BAAI/bge-base-en-v1.5')

print("Loading reranker model...")

reranker = CrossEncoder(
    'cross-encoder/ms-marco-MiniLM-L-6-v2'
)

# =========================
# QUERY
# =========================

query = "How can I return a damaged item?"
query = "Represent this sentence for searching relevant passages: " + query
print(f"\nQuery: {query}")

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

TOP_K = 5

scores, indices = index.search(
    query_embedding,
    TOP_K
)

print("\nInitial Retrieved Chunks:\n")

retrieved_chunks = []

retrieved_ids = []

for rank, idx in enumerate(indices[0]):

    retrieved_ids.append(idx)

    chunk = df.iloc[idx]['chunk_text']

    retrieved_chunks.append(chunk)

    print(f"Rank {rank+1}")
    
    print(f"Cosine Score: {scores[0][rank]:.4f}")
    
    print(chunk[:300])
    
    print("-" * 50)

# =========================
# PREPARE FOR RERANKING
# =========================

pairs = [
    [query, chunk]
    for chunk in retrieved_chunks
]

# =========================
# RERANKING
# =========================

print("\nRunning reranker...\n")

rerank_scores = reranker.predict(pairs)

# Combine chunk ids, chunks, and scores
reranked = list(
    zip(
        retrieved_ids,
        retrieved_chunks,
        rerank_scores
    )
)

# Sort by reranker score descending
reranked = sorted(
    reranked,
    key=lambda x: x[2],
    reverse=True
)

# =========================
# FINAL RESULTS
# =========================

print("\n========== Re-ranked Results ==========\n")

for rank, (chunk_id, chunk, score) in enumerate(reranked):

    print(f"Final Rank {rank+1}")

    print(f"Chunk ID: {chunk_id}")

    print(f"Re-ranker Score: {score:.4f}")

    print(chunk[:400])

    print("-" * 60)