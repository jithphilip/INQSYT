import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os
import re

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.dirname(CURRENT_DIR)

# Load chunk data
df = pd.read_json(os.path.join(PIPELINE_DIR, "..", "Main_Data", "Chunks", "chunks_optimised.jsonl"), lines=True)

# Load embedding model
model = SentenceTransformer('BAAI/bge-base-en-v1.5')

def generate_topic(row):
    meta = row.get("metadata", {})
    cat_path = meta.get("category_path", "")
    
    parts = [p.strip() for p in cat_path.split(" > ")]
    if len(parts) >= 2:
        doc_name = parts[1]
    else:
        doc_name = row.get("source_file", "")
        
    doc_name = re.sub(r"\(\d+\)", "", doc_name)
    doc_name = doc_name.replace(".md", "").strip()
    doc_name = re.sub(r"that Shows a$", "that Shows as Delivered", doc_name)
    doc_name = re.sub(r"Companies No$", "Companies Not Affiliated with Amazon", doc_name)
    doc_name = re.sub(r"Text Up$", "Text Updates", doc_name)
    doc_name = re.sub(r"Shipment Tra$", "Shipment Tracking", doc_name)
    
    title = row.get("chunk_title", "").strip()
    title = re.sub(r"^\d+\s*[-.]\s*", "", title).strip()
    
    if title.lower() in doc_name.lower():
        topic = f"Topic: {doc_name}"
    elif doc_name.lower() in title.lower():
        topic = f"Topic: {title}"
    else:
        topic = f"Topic: {doc_name} - {title}"
        
    return topic

# Convert chunks to list with Title, Source, Synonym, and Query context
chunks = []
for _, row in df.iterrows():
    meta = row.get("metadata", {})
    queries = meta.get("sample_queries", [])
    syns = meta.get("jargon_synonyms", [])
    
    category_path = meta.get("category_path", "")
    category = category_path.split(" > ")[0] if " > " in category_path else "General Help"
    
    topic = generate_topic(row)
    search_text = f"{topic}\n"
    search_text += f"Category: {category} | Title: {row.get('chunk_title', '')} | Source: {row.get('source_file', '')}\n"
    search_text += f"Content: {row.get('chunk', '')}\n"
    if syns:
        search_text += f"Keywords: {', '.join(syns)}\n"
    if queries:
        search_text += "Frequently Asked Questions:\n"
        for q in queries:
            search_text += f"- {q}\n"
            
    chunks.append(search_text.strip())

# Generate embeddings
print("Generating embeddings...")
embeddings = model.encode(
    chunks,
    convert_to_numpy=True,
    show_progress_bar=True
)

# Convert to float32
embeddings = embeddings.astype("float32")

# Normalize embeddings
faiss.normalize_L2(embeddings)

# Save embeddings
os.makedirs(os.path.join(PIPELINE_DIR, "embeddings"), exist_ok=True)
np.save(os.path.join(PIPELINE_DIR, "embeddings", "chunk_embeddings_optimised.npy"), embeddings)

print("Optimised Embeddings saved!")
