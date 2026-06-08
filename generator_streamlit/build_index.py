import os
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

chunks_df = pd.read_json(os.path.join(CURRENT_DIR, "Chunks.jsonl"), lines=True)

embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

texts = []
for _, row in chunks_df.iterrows():
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

faiss.write_index(index, os.path.join(CURRENT_DIR, "faiss_index.bin"))

print("FAISS index saved successfully.")
print(f"Indexed {index.ntotal} chunks.")
