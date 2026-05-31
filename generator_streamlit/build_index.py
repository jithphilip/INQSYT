import os
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

chunks_df = pd.read_json(os.path.join(CURRENT_DIR, "Chunks.jsonl"), lines=True)

embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

texts = chunks_df["chunk"].tolist()

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
