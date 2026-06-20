import os
import json
import numpy as np
import pandas as pd
import pickle
import faiss
from sentence_transformers import SentenceTransformer

ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
PIPELINE_DIR = os.path.join(ws_dir, "Retrieval_Pipeline")
GEN_DIR = os.path.join(ws_dir, "generator_streamlit")

# Load QA dataset
qa_df = pd.read_csv(os.path.join(PIPELINE_DIR, "data", "qa_dataset.csv"))

# Load LR Classifier
with open(os.path.join(GEN_DIR, "intent_classifier.pkl"), "rb") as f:
    classifier_data = pickle.load(f)
clf = classifier_data["classifier"]
le = classifier_data["label_encoder"]

# Load embedder to get LR predictions
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

print("Queries falling back to LLM under (margin <= 0.35) and (top1_prob < 0.13):")
for idx in range(len(qa_df)):
    row = qa_df.iloc[idx]
    question = row['question']
    query = "Represent this sentence for searching relevant passages: " + question
    
    query_embedding = embedder.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_embedding)
    
    probs = clf.predict_proba(query_embedding)[0]
    sorted_idxs = np.argsort(probs)[::-1]
    
    top1_idx = sorted_idxs[0]
    top1_prob = probs[top1_idx]
    top1_intent = le.inverse_transform([top1_idx])[0]
    
    top2_idx = sorted_idxs[1]
    top2_prob = probs[top2_idx]
    top2_intent = le.inverse_transform([top2_idx])[0]
    
    margin = top1_prob - top2_prob
    if margin <= 0.35 and top1_prob < 0.13:
        print(f"- Question: {question}")
        print(f"  Top 1: {top1_intent} ({top1_prob:.4f})")
        print(f"  Top 2: {top2_intent} ({top2_prob:.4f})")
        print(f"  Margin: {margin:.4f}")
        print("-" * 30)
