"""
Train Logistic Regression NLU Classifier using the V2 dataset (10,000 natural queries).
Uses BAAI/bge-base-en-v1.5 embeddings and class_weight='balanced' to handle natural class imbalance.
"""
import os
import json
import pickle
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import faiss

WS = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
MAIN_DATA = os.path.join(WS, "Main_Data")
V2_FILE = os.path.join(MAIN_DATA, "classifier_training_dataset_v2.csv")
EVAL_FILE = os.path.join(MAIN_DATA, "eval_dataset.csv")
MODEL_OUT_PATH = os.path.join(WS, "generator_streamlit", "intent_classifier.pkl")

print(f"Loading V2 training dataset from {V2_FILE}...")
train_df = pd.read_csv(V2_FILE)
eval_df = pd.read_csv(EVAL_FILE)

print(f"Training set size: {len(train_df)}")
print(f"Eval set size: {len(eval_df)}")

# 1. Encode Labels
print("Encoding labels...")
le = LabelEncoder()
y_train = le.fit_transform(train_df["intent label"])
y_eval = le.transform(eval_df["intent"])

print(f"Found {len(le.classes_)} unique intents.")

# 2. Generate Embeddings using BAAI/bge-base-en-v1.5
print("Loading BAAI/bge-base-en-v1.5 embedding model...")
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

print("Generating training embeddings (this may take a few minutes)...")
# Note: Using the instruction prompt for symmetric retrieval / semantic search is best for general embedding
train_queries = ["Represent this sentence for searching relevant passages: " + str(q) for q in train_df["question"].tolist()]
X_train = embedder.encode(train_queries, convert_to_numpy=True, show_progress_bar=True).astype("float32")
faiss.normalize_L2(X_train)

print("Generating eval embeddings...")
eval_queries = ["Represent this sentence for searching relevant passages: " + str(q) for q in eval_df["question"].tolist()]
X_eval = embedder.encode(eval_queries, convert_to_numpy=True, show_progress_bar=True).astype("float32")
faiss.normalize_L2(X_eval)

# 3. Train Logistic Regression
# Using class_weight='balanced' to handle the natural data imbalance seamlessly.
print("Training Logistic Regression classifier with class_weight='balanced'...")
clf = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
clf.fit(X_train, y_train)

# 4. Evaluate Accuracy
train_acc = clf.score(X_train, y_train)
eval_acc = clf.score(X_eval, y_eval)

print(f"\nResults:")
print(f"Train Accuracy: {train_acc * 100:.2f}%")
print(f"Eval Accuracy : {eval_acc * 100:.2f}%")

# Top-3 Eval Accuracy
probs = clf.predict_proba(X_eval)
top_3_preds = np.argsort(probs, axis=1)[:, -3:]
top_3_hits = np.any(top_3_preds == y_eval.reshape(-1, 1), axis=1)
top_3_acc = np.mean(top_3_hits)
print(f"Eval Top-3 Accuracy: {top_3_acc * 100:.2f}%")

# 5. Save the updated model
print(f"\nSaving classifier to {MODEL_OUT_PATH}...")
classifier_data = {
    "classifier": clf,
    "label_encoder": le,
    "embedder_name": "BAAI/bge-base-en-v1.5"
}

with open(MODEL_OUT_PATH, "wb") as f:
    pickle.dump(classifier_data, f)
    
print("Done!")
