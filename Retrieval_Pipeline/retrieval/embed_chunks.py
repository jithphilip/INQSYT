import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import faiss

import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.dirname(CURRENT_DIR)

# Load chunk data
df = pd.read_json(os.path.join(PIPELINE_DIR, "data", "chunks.jsonl"), lines=True)

# Load embedding model
model = SentenceTransformer('BAAI/bge-base-en-v1.5')

# Convert chunks to list
chunks = df['chunk'].tolist()


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

