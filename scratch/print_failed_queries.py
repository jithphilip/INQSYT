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
llm_map = {item["question"]: (item["pred_primary"], item["pred_secondary"]) for item in llm_progress}

# Load LR Classifier
with open(os.path.join(GEN_DIR, "intent_classifier.pkl"), "rb") as f:
    classifier_data = pickle.load(f)
clf = classifier_data["classifier"]
le = classifier_data["label_encoder"]

# Load embedder to get LR predictions
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

failed_queries = []
correct_count = 0

for idx in range(len(qa_df)):
    row = qa_df.iloc[idx]
    question = row['question']
    query = "Represent this sentence for searching relevant passages: " + question
    true_chunk_id = row['reference_chunk_id']
    true_intent = row['intent']
    
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
    
    # Check optimized fallback condition
    use_llm = (margin <= 0.35) and (top1_prob < 0.13)
    
    if use_llm:
        primary, secondary = llm_map.get(question, ("other_query", None))
        router_source = "Qwen"
    else:
        primary = top1_intent
        secondary = top2_intent if margin <= 0.2 else None
        router_source = "LR"
        
    pred_intents = [primary]
    if secondary:
        pred_intents.append(secondary)
        
    is_correct_routing = any(intent in chunk_to_intents.get(true_chunk_id, []) for intent in pred_intents)
    if is_correct_routing:
        correct_count += 1
    else:
        failed_queries.append({
            "question": question,
            "true_intent": true_intent,
            "true_chunk_id": true_chunk_id,
            "true_chunk_intents": chunk_to_intents.get(true_chunk_id, []),
            "pred_primary": primary,
            "pred_secondary": secondary,
            "router_source": router_source,
            "top1_prob": float(top1_prob),
            "margin": float(margin)
        })

print(f"Total processed: {len(qa_df)}")
print(f"Correct routing: {correct_count} ({correct_count/len(qa_df)*100:.2f}%)")
print(f"Failed routing: {len(failed_queries)} ({len(failed_queries)/len(qa_df)*100:.2f}%)\n")

# Group failures by true_intent
failures_by_intent = {}
for item in failed_queries:
    intent = item["true_intent"]
    if intent not in failures_by_intent:
        failures_by_intent[intent] = []
    failures_by_intent[intent].append(item)

# Save failure data to JSON for the report
with open(os.path.join(ws_dir, "scratch", "failed_queries.json"), "w") as f:
    json.dump(failed_queries, f, indent=2)

for intent, items in sorted(failures_by_intent.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"Intent: {intent} (Count: {len(items)})")
    for item in items:
        print(f"  - Question: {item['question']}")
        print(f"    Source: {item['router_source']} | Top1 Prob: {item['top1_prob']:.4f} | Margin: {item['margin']:.4f}")
        print(f"    Predicted: Primary='{item['pred_primary']}', Secondary='{item['pred_secondary']}'")
        print(f"    True Chunk Intents: {item['true_chunk_intents']}")
        print()
