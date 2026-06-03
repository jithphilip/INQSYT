import os
import faiss
import pandas as pd
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_retrieval_resources():
    chunks_df = pd.read_json(os.path.join(CURRENT_DIR, "Chunks_v2.jsonl"), lines=True)
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
        if idx == -1 or idx >= len(chunks_df):
            continue

        row = chunks_df.iloc[idx]
        chunk_text = row["chunk"]

        # Resolve table/list structures from metadata
        meta = row.get("metadata")
        if isinstance(meta, dict):
            chunk_type = meta.get("chunk_type")
            if chunk_type == "table" and meta.get("table_markdown"):
                # Combine the summary and the raw table
                chunk_text = f"{row['chunk']}\n\n{meta['table_markdown']}"
            elif chunk_type == "list" and meta.get("list_markdown"):
                chunk_text = meta["list_markdown"]

        # Prepend the title for full parent context
        formatted_chunk = f"Title: {row['chunk_title']}\nContent: {chunk_text}"
        retrieved_chunks.append(formatted_chunk)

    return retrieved_chunks
