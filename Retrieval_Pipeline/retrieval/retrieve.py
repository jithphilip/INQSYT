import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Load chunk data
df = pd.read_csv("D:/INQYST/Week 1/Task2 - Retrieval/data/chunks.csv")

# Load embeddings
embeddings = np.load("D:/INQYST/Week 1/Task2 - Retrieval/embeddings/chunk_embeddings.npy")

# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

print(f"Indexed {index.ntotal} chunks")

# Load embedding model
model = SentenceTransformer('BAAI/bge-base-en-v1.5')

# Example query
query = "How can I return a damaged item?"
query = "Represent this sentence for searching relevant passages: " + query

# Convert query to embedding
query_embedding = model.encode([query])

# Normalize query embedding
faiss.normalize_L2(query_embedding)

# Search top 3 chunks
k = 5

scores, indices = index.search(query_embedding, k)

print("\nTop Retrieved Chunks:\n")

for rank, idx in enumerate(indices[0]):

    print(f"Rank {rank+1}")
    
    print(f"Cosine Score: {scores[0][rank]:.4f}")
    
    print(df.iloc[idx]['chunk_text'])
    
    print("-" * 50)