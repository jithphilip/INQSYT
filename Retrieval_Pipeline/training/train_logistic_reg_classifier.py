import json
import os
import pickle
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

# Directories
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PIPELINE_DIR = os.path.dirname(CURRENT_DIR)

PROJECT_DIR = os.path.dirname(PIPELINE_DIR)

MAIN_DATA_DIR = os.path.join(PROJECT_DIR, "Main_Data")

MODELS_DIR = os.path.join(PIPELINE_DIR, "models")

MODEL_SAVE_PATH = os.path.join(MODELS_DIR, "intent_classifier_v3.pkl")

# Load embedding model
print("Loading BAAI/bge-base-en-v1.5 model...")
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

# 1. Load data from queries.csv
QUERIES_CSV_PATH = os.path.join(
    MAIN_DATA_DIR,
    "Training",
    "classifier_training_dataset_v3.csv"
)

training_queries = []
labels = []

if os.path.exists(QUERIES_CSV_PATH):
    print(f"Loading queries from {QUERIES_CSV_PATH}...")
    df_queries = pd.read_csv(QUERIES_CSV_PATH)
    for _, row in df_queries.iterrows():
        question = row["question"]
        intent = row["intent label"]
        training_queries.append(f"Represent this sentence for searching relevant passages: {question}")
        labels.append(intent)
    print(f"Loaded {len(training_queries)} queries for classifier training.")
else:
    print(f"Error: {QUERIES_CSV_PATH} not found.")
    exit(1)

# 3. Generate embeddings
print("Encoding training queries (this will take a moment)...")
X = embedder.encode(
    training_queries,
    convert_to_numpy=True,
    show_progress_bar=True
).astype("float32")

# Encode labels
le = LabelEncoder()
y = le.fit_transform(labels)

# 4. Perform cross-validation
print("\nEvaluating model with Stratified 5-Fold Cross Validation...")
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = []
for train_idx, test_idx in skf.split(X, y):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    clf = LogisticRegression(class_weight="balanced", C=1.0, max_iter=1000, random_state=42)
    clf.fit(X_train, y_train)
    cv_scores.append(clf.score(X_test, y_test))

print(f"Mean Cross-Validation Accuracy: {np.mean(cv_scores):.4f} (Std: {np.std(cv_scores):.4f})")

# 5. Train final model
print("\nTraining final model on full dataset...")
final_clf = LogisticRegression(class_weight="balanced", C=1.0, max_iter=1000, random_state=42)
final_clf.fit(X, y)

# Show classification report on training set as sanity check
y_pred = final_clf.predict(X)
print("\nClassification Report (Training Set):")
print(classification_report(y, y_pred, target_names=le.classes_))

# Save the model, label encoder, and metadata
print(f"Saving classifier to {MODEL_SAVE_PATH}...")
model_data = {
    "classifier": final_clf,
    "label_encoder": le,
    "classes": le.classes_.tolist()
}
with open(MODEL_SAVE_PATH, "wb") as f:
    pickle.dump(model_data, f)

print("Done! Classifier trained and saved successfully.")
