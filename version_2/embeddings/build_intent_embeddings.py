import json
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

# -----------------------
# LOAD INTENTS
# -----------------------

with open("data_review/intents_descriptions_v1.json", "r", encoding="utf-8") as f:
    intents = json.load(f)

with open("data_review/intent_to_chunk_mapping.json", "r", encoding="utf-8") as f:
    mappings = json.load(f)

mapping_dict = {item["intent"]: item["chunk_ids"] for item in mappings}
for intent in intents:
    intent["source_chunks"] = mapping_dict.get(intent["intent"], [])

# -----------------------
# MODEL
# -----------------------

model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)

# -----------------------
# BUILD TEXTS
# -----------------------

texts = []

for intent in intents:
    title = intent.get("intent", "")
    desc = intent.get("description", "")
    queries = intent.get("sample_queries", [])

    text = f"Intent: {title}. Description: {desc}."
    if queries:
        text += f" Sample Queries: {' '.join(queries)}."

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
    "embeddings/intent_index.faiss"
)
# -----------------------
# SAVE METADATA
# -----------------------

with open(
    "embeddings/intent_metadata.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(intents, f, indent=2)

print("Intent index built")