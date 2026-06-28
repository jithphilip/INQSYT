import os
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PIPELINE_DIR = os.path.dirname(CURRENT_DIR)

PROJECT_DIR = os.path.dirname(PIPELINE_DIR)

MAIN_DATA_DIR = os.path.join(PROJECT_DIR, "Main_Data")

INDICES_DIR = os.path.join(PIPELINE_DIR, "indices")

chunks_df = pd.read_json(
    os.path.join(MAIN_DATA_DIR, "Chunks", "chunks_v2_fixed.jsonl"),
    lines=True
)

embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

import re

def generate_topic(row):
    meta = row.get("metadata", {})
    cat_path = meta.get("category_path", "")
    
    parts = [p.strip() for p in cat_path.split(" > ")]
    if len(parts) >= 2:
        doc_name = parts[1]
    else:
        doc_name = row["source_file"]
        
    doc_name = re.sub(r"\(\d+\)", "", doc_name)
    doc_name = doc_name.replace(".md", "").strip()
    doc_name = re.sub(r"that Shows a$", "that Shows as Delivered", doc_name)
    doc_name = re.sub(r"Companies No$", "Companies Not Affiliated with Amazon", doc_name)
    doc_name = re.sub(r"Text Up$", "Text Updates", doc_name)
    doc_name = re.sub(r"Shipment Tra$", "Shipment Tracking", doc_name)
    
    title = row["chunk_title"].strip()
    title = re.sub(r"^\d+\s*[-.]\s*", "", title).strip()
    
    if title.lower() in doc_name.lower():
        topic = f"Topic: {doc_name}"
    elif doc_name.lower() in title.lower():
        topic = f"Topic: {title}"
    else:
        topic = f"Topic: {doc_name} - {title}"
        
    return topic

texts = []
for _, row in chunks_df.iterrows():
    meta = row.get("metadata", {})
    queries = meta.get("sample_queries", [])
    syns = meta.get("jargon_synonyms", [])
    
    category_path = meta.get("category_path", "")
    category = category_path.split(" > ")[0] if " > " in category_path else "General Help"
    
    topic = generate_topic(row)
    search_text = f"{topic}\n"
    search_text += f"Category: {category} | Title: {row['chunk_title']} | Source: {row['source_file']}\n"
    search_text += f"Content: {row['chunk']}\n"
    if syns:
        search_text += f"Keywords: {', '.join(syns)}\n"
    if queries:
        search_text += "Frequently Asked Questions:\n"
        for q in queries:
            search_text += f"- {q}\n"
    
    texts.append(search_text.strip())

embeddings = embedder.encode(
    texts,
    convert_to_numpy=True,
    show_progress_bar=True
).astype("float32")

faiss.normalize_L2(embeddings)

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

faiss.write_index(
    index,
    os.path.join(INDICES_DIR, "faiss_index_v2.bin")
)

print("FAISS index saved successfully.")
print(f"Indexed {index.ntotal} chunks.")
