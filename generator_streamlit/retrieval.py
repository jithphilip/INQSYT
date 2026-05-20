import os
import faiss
import pandas as pd
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_retrieval_resources():
    chunks_df = pd.read_csv(os.path.join(CURRENT_DIR, "Chunks.csv"))
    embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    index = faiss.read_index(os.path.join(CURRENT_DIR, "faiss_index.bin"))
    return chunks_df, embedder, index

def retrieve(query, top_k=3):
    chunks_df, embedder, index = load_retrieval_resources()
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
