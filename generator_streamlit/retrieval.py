import faiss
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# Load chunk data
chunks_df = pd.read_csv("generator_streamlit/Chunks.csv")

# Load embedding model
embedder = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Load FAISS index
index = faiss.read_index("faiss_index.bin")

def retrieve(query, top_k=3):

    query_embedding = embedder.encode([query])

    distances, indices = index.search(
        np.array(query_embedding),
        top_k
    )

    retrieved_chunks = []

    for idx in indices[0]:
        retrieved_chunks.append(
            chunks_df.iloc[idx]["chunk"]
        )

    return retrieved_chunks
