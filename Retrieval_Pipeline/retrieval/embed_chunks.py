import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import faiss

import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.dirname(CURRENT_DIR)

# Load chunk data
df = pd.read_json(os.path.join(PIPELINE_DIR, "data", "Chunks.jsonl"), lines=True)

# Load embedding model
model = SentenceTransformer('BAAI/bge-base-en-v1.5')

# Convert chunks to list with Title, Source, Synonym, and Query context
chunks = []
for _, row in df.iterrows():
    meta = row.get("metadata", {})
    queries = meta.get("sample_queries", [])
    syns = meta.get("jargon_synonyms", [])
    
    category_path = meta.get("category_path", "")
    category = category_path.split(" > ")[0] if " > " in category_path else "General Help"
    
    search_text = f"Category: {category} | Title: {row['chunk_title']} | Source: {row['source_file']}\n"
    search_text += f"Content: {row['chunk']}\n"
    if syns:
        search_text += f"Keywords: {', '.join(syns)}\n"
    if queries:
        search_text += "Frequently Asked Questions:\n"
        for q in queries:
            search_text += f"- {q}\n"
            
    chunks.append(search_text.strip())


# Generate embeddings
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
np.save(os.path.join(PIPELINE_DIR, "embeddings", "chunk_embeddings.npy"), embeddings)

print("Embeddings saved!")

