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
    embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
    index = faiss.read_index(os.path.join(CURRENT_DIR, "faiss_index.bin"))
    return chunks_df, embedder, index

def retrieve(query, top_k=3):
    chunks_df, embedder, index = load_retrieval_resources()

    query = "Represent this sentence for searching relevant passages: " + query

    query_embedding = embedder.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, top_k)

    retrieved_chunks = []

    for idx in indices[0]:
        if idx == -1:
            continue

        retrieved_chunks.append(
            chunks_df.iloc[idx]["chunk"]
        )

    return retrieved_chunks
