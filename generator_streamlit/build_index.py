import pandas as pd
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer

# Load chunks
chunks_df = pd.read_csv("D:/INQYST/Week 1/Task2 - Retrieval/data/chunks.csv")

# Load embedding model
embedder = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Generate embeddings
embeddings = embedder.encode(
    chunks_df["chunk"].tolist(),
    show_progress_bar=True
)

# Convert to numpy float32
embeddings = np.array(embeddings).astype("float32")

# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

# Add embeddings
index.add(embeddings)

# Save index
faiss.write_index(
    index,
    "faiss_index.bin"
)

print("FAISS index saved successfully!")