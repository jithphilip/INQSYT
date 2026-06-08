import os
import faiss
import json
import pickle
import pandas as pd
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_intent_resources():
    # Load chunks
    chunks_df = pd.read_json(os.path.join(CURRENT_DIR, "Chunks.jsonl"), lines=True)
    
    # Load embedder
    embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
    
    # Load FAISS index
    index = faiss.read_index(os.path.join(CURRENT_DIR, "faiss_index.bin"))
    
    # Load classifier
    with open(os.path.join(CURRENT_DIR, "intent_classifier.pkl"), "rb") as f:
        classifier_data = pickle.load(f)
        
    # Reconstruct raw embeddings from Flat index
    all_vectors = np.array([index.reconstruct(i) for i in range(index.ntotal)]).astype("float32")
    
    # Load intents schema and map each chunk_id to its intent
    with open(os.path.join(CURRENT_DIR, "intents_schema.json"), "r") as f:
        intents_schema = json.load(f)
        
    chunk_to_intent = {}
    for entry in intents_schema:
        intent_name = entry["intent"]
        for cid in entry["source_chunks"]:
            chunk_to_intent[cid] = intent_name
            
    # Add an 'intent' column to chunks_df dynamically!
    chunks_df["intent"] = chunks_df["chunk_id"].map(chunk_to_intent).fillna("other_query")
    
    return chunks_df, embedder, index, classifier_data, all_vectors

def retrieve(query, top_k=3):
    chunks_df, embedder, index, classifier_data, all_vectors = load_intent_resources()
    
    # 1. Classify the user query intent
    clf = classifier_data["classifier"]
    le = classifier_data["label_encoder"]
    
    # Embed query (with BGE search instruction)
    search_query = "Represent this sentence for searching relevant passages: " + query
    query_embedding = embedder.encode(
        [search_query],
        convert_to_numpy=True
    ).astype("float32")
    
    # Normalize query embedding
    faiss.normalize_L2(query_embedding)
    
    # Predict intent probabilities
    probs = clf.predict_proba(query_embedding)[0]
    sorted_idxs = np.argsort(probs)[::-1]
    
    top1_idx = sorted_idxs[0]
    top1_prob = probs[top1_idx]
    predicted_intent = le.inverse_transform([top1_idx])[0]
    
    # Confidence fallback: if top prediction has low confidence (< 50%), search all chunks
    if top1_prob < 0.5:
        predicted_intent_list = ["other_query"]
        search_all = True
    else:
        search_all = False
        top2_idx = sorted_idxs[1]
        top2_prob = probs[top2_idx]
        
        # Multi-label search: if top-2 is close to top-1 (difference <= 0.2), search both
        if (top1_prob - top2_prob) <= 0.2:
            intent1 = predicted_intent
            intent2 = le.inverse_transform([top2_idx])[0]
            predicted_intent_list = [intent1, intent2]
        else:
            predicted_intent_list = [predicted_intent]
    
    # 2. Apply metadata filtering based on predicted intent list
    if search_all:
        filtered_df = chunks_df
    else:
        filtered_df = chunks_df[chunks_df["intent"].isin(predicted_intent_list)]
        
    # Fallback to all chunks if filtering returns nothing
    if filtered_df.empty:
        filtered_df = chunks_df
        
    filtered_indices = filtered_df.index.tolist()
    
    # 3. Perform Vector search manually on the filtered subset for exact cosine similarity
    filtered_vectors = all_vectors[filtered_indices]
    
    # Dot product since vectors are normalized (equivalent to cosine similarity)
    similarities = np.dot(filtered_vectors, query_embedding.T).flatten()
    
    # Get top-k matches
    top_indices_local = np.argsort(similarities)[::-1][:top_k]
    
    retrieved_chunks = []
    for local_idx in top_indices_local:
        score = similarities[local_idx]
        global_idx = filtered_indices[local_idx]
        row = chunks_df.iloc[global_idx]
        
        chunk_text = row["chunk"]
        
        # Resolve table/list structures from metadata
        meta = row.get("metadata")
        if isinstance(meta, dict):
            chunk_type = meta.get("chunk_type")
            if chunk_type == "table" and meta.get("table_markdown"):
                chunk_text = f"{row['chunk']}\n\n{meta['table_markdown']}"
            elif chunk_type == "list" and meta.get("list_markdown"):
                chunk_text = meta["list_markdown"]
                
        # Prepend the title for full parent context
        formatted_chunk = f"Title: {row['chunk_title']}\nContent: {chunk_text}"
        
        retrieved_chunks.append({
            "chunk": formatted_chunk,
            "score": float(score),
            "intent": ", ".join(predicted_intent_list),
            "chunk_id": row["chunk_id"],
            "source_file": row["source_file"]
        })
        
    return retrieved_chunks
