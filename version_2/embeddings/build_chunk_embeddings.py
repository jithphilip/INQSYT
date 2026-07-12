import json
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

# -----------------------
# LOAD CHUNKS
# -----------------------

with open(
    "data/chunks.json",
    "r",
    encoding="utf-8"
) as f:
    chunks = json.load(f)

# -----------------------
# MODEL
# -----------------------

model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)

# -----------------------
# BUILD EMBEDDING TEXT
# -----------------------

texts = []

for chunk in chunks:
    content = chunk.get("content", "")
    path = chunk.get("path", "")
    sample_queries = chunk.get("sample_queries", [])
    retrieval_terms = chunk.get("retrieval_terms", [])
    search_phrases = chunk.get("search_phrases", [])

    text = f"Content: {content}\nPath: {path}"
    if sample_queries:
        text += f"\nSample Queries: {', '.join(sample_queries)}"
    if retrieval_terms:
        text += f"\nRetriever Terms: {', '.join(retrieval_terms)}"
    if search_phrases:
        text += f"\nCustomer Phrases: {', '.join(search_phrases)}"

    texts.append(text)

# -----------------------
# EMBEDDINGS
# -----------------------

embeddings = model.encode(
    texts,
    normalize_embeddings=True,
    convert_to_numpy=True
)

# -----------------------
# FAISS
# -----------------------

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(
    embeddings.astype(np.float32)
)

faiss.write_index(
    index,
    "embeddings/chunk_index.faiss"
)

# -----------------------
# SAVE CHUNKS
# -----------------------

with open(
    "embeddings/chunk_metadata.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        chunks,
        f,
        indent=2
    )

print("Chunk index built")