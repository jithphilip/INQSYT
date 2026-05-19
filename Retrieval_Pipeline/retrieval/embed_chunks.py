import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import faiss

# Load chunk data
df = pd.read_csv("D:/INQYST/Week 1/Task2 - Retrieval/data/chunks.csv")

# Load embedding model
model = SentenceTransformer('BAAI/bge-base-en-v1.5')

# Convert chunks to list
chunks = df['chunk_text'].tolist()


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
np.save("D:/INQYST/Week 1/Task2 - Retrieval/embeddings/chunk_embeddings.npy", embeddings)

print("Embeddings saved!")

