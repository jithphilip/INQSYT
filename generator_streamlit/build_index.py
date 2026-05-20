import os
import pandas as pd
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load chunks
chunks_df = pd.read_csv(os.path.join(CURRENT_DIR, "Chunks.csv"))

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
    os.path.join(CURRENT_DIR, "faiss_index.bin")
)

print("FAISS index saved successfully!")
