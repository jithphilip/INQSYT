import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
GEN_DIR = os.path.join(ws_dir, "generator_streamlit")

# Load LR Classifier
with open(os.path.join(GEN_DIR, "intent_classifier.pkl"), "rb") as f:
    classifier_data = pickle.load(f)
clf = classifier_data["classifier"]
le = classifier_data["label_encoder"]

# Load embedder
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

query = "My package was delivered to the Marriott front desk but when I went to pick it up, it was gone. Can I get a refund?"
search_query = "Represent this sentence for searching relevant passages: " + query

query_embedding = embedder.encode([search_query], convert_to_numpy=True).astype("float32")
faiss.normalize_L2(query_embedding)

probs = clf.predict_proba(query_embedding)[0]
sorted_idxs = np.argsort(probs)[::-1]

for i in range(5):
    idx = sorted_idxs[i]
    intent = le.inverse_transform([idx])[0]
    prob = probs[idx]
    print(f"Rank {i+1}: {intent} (Prob: {prob:.4f})")

margin = probs[sorted_idxs[0]] - probs[sorted_idxs[1]]
print(f"Margin: {margin:.4f}")
