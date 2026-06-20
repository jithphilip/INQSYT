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
with open(os.path.join(PIPELINE_DIR, "data", "intents_schema.json"), "r", encoding="utf-8") as f:
    intents_schema = json.load(f)

chunk_to_intents = {}
for entry in intents_schema:
    intent_name = entry["intent"]
    for cid in entry["source_chunks"]:
        if cid not in chunk_to_intents:
            chunk_to_intents[cid] = []
        chunk_to_intents[cid].append(intent_name)

# Load LLM few-shot predictions
with open(os.path.join(ws_dir, "scratch", "llm_eval_few_shot_progress.json"), "r") as f:
    llm_progress = json.load(f)

# Load LR Classifier
with open(os.path.join(GEN_DIR, "intent_classifier.pkl"), "rb") as f:
    classifier_data = pickle.load(f)
clf = classifier_data["classifier"]
le = classifier_data["label_encoder"]

# Load embedder to get LR predictions
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

# Precompute LR predictions, top1 probs, and margins
lr_predictions = []
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
    lr_predictions.append({
        "question": question,
        "true_intent": row['intent'],
        "true_chunk_id": row['reference_chunk_id'],
        "top1_intent": top1_intent,
        "top2_intent": top2_intent,
        "top1_prob": float(top1_prob),
        "margin": float(margin)
    })

# Map LLM predictions by question for lookup
llm_map = {item["question"]: (item["pred_primary"], item["pred_secondary"]) for item in llm_progress}

def run_evaluation(condition_fn, name):
    correct_routing = 0
    fallback_count = 0
    
    for idx, lr_pred in enumerate(lr_predictions):
        question = lr_pred["question"]
        true_chunk_id = lr_pred["true_chunk_id"]
        
        # Decide router based on the condition function
        use_llm = condition_fn(lr_pred["margin"], lr_pred["top1_prob"])
        
        if use_llm:
            fallback_count += 1
            primary, secondary = llm_map.get(question, ("other_query", None))
        else:
            primary = lr_pred["top1_intent"]
            secondary = lr_pred["top2_intent"] if lr_pred["margin"] <= 0.2 else None
            
        pred_intents = [primary]
        if secondary:
            pred_intents.append(secondary)
            
        is_correct_routing = any(intent in chunk_to_intents.get(true_chunk_id, []) for intent in pred_intents)
        if is_correct_routing:
            correct_routing += 1
            
    accuracy = correct_routing / len(lr_predictions)
    fallback_pct = (fallback_count / len(lr_predictions)) * 100
    print(f"{name}:")
    print(f"  Routing Accuracy: {accuracy*100:.2f}%")
    print(f"  Fallback Rate: {fallback_pct:.2f}% ({fallback_count}/{len(lr_predictions)})")
    print("-" * 40)

# Evaluate different conditions
print("Evaluating conditions on the evaluation set:\n")

# Baseline: margin <= 0.35
run_evaluation(lambda margin, top1: margin <= 0.35, "Baseline (margin <= 0.35)")

# Condition 1: margin <= 0.35 AND top1 < 0.13
run_evaluation(lambda margin, top1: (margin <= 0.35) and (top1 < 0.13), "Condition (margin <= 0.35) AND (top1_prob < 0.13)")

# Condition 2: margin <= 0.35 OR top1 < 0.13
run_evaluation(lambda margin, top1: (margin <= 0.35) or (top1 < 0.13), "Condition (margin <= 0.35) OR (top1_prob < 0.13)")

# What if user literally meant: margin > 0.35 AND top1 < 0.13?
run_evaluation(lambda margin, top1: (margin > 0.35) and (top1 < 0.13), "Condition (margin > 0.35) AND (top1_prob < 0.13) (literal interpretation)")
