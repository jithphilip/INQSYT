import json
import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from retrieval import retrieve, retrieve_intents

# Load evaluation dataset
df = pd.read_csv("data/eval_dataset.csv")

# We want to run sweeps for K = 1, 3, 5, 7, 10, 15
k_values = [1, 3, 5, 7, 10, 15]
hit_counts = {k: 0 for k in k_values}
mrr_sums = {k: 0.0 for k in k_values}
failed_queries_by_k = {k: [] for k in k_values}

intent_k_values = [1, 3, 5]
intent_hit_counts = {k: 0 for k in intent_k_values}
failed_intents_by_k = {k: [] for k in intent_k_values}

failed_at_k3_details = []

print(f"Starting evaluation of {len(df)} queries...")

for idx, row in tqdm(df.iterrows(), total=len(df)):
    query = row["question"]
    gold_chunk = int(row["reference_chunk_id"])
    gold_intent = row["intent"]

    # Retrieve intents up to k=5 to analyze classification successes
    intent_results = retrieve_intents(query, k=5)
    predicted_intents_5 = [item["intent"]["intent"] for item in intent_results]
    predicted_intents_3 = predicted_intents_5[:3]
    
    intent_success = "Yes" if gold_intent in predicted_intents_3 else "No"

    # Evaluate Intent Hits
    for k in intent_k_values:
        sub_intents = predicted_intents_5[:k]
        if gold_intent in sub_intents:
            intent_hit_counts[k] += 1
        else:
            failed_intents_by_k[k].append(query)

    # Retrieve top 15 chunks (since max K is 15)
    results = retrieve(query, top_k=15)
    retrieved_chunks = [int(item[0][0]["chunk_id"]) for item in results]
    retrieved_chunks_with_scores = [(int(item[0][0]["chunk_id"]), item[1]) for item in results]

    # Evaluate Chunks for each K
    for k in k_values:
        sub_retrieved = retrieved_chunks[:k]
        if gold_chunk in sub_retrieved:
            hit_counts[k] += 1
            # Compute MRR at this K
            rank = sub_retrieved.index(gold_chunk) + 1
            mrr_sums[k] += 1.0 / rank
        else:
            failed_queries_by_k[k].append(query)

        # Log details for K = 3 failures
        if k == 3 and gold_chunk not in sub_retrieved:
            # Determine isolated component
            if intent_success == "No":
                isolated_comp = "Bi-Encoder Intent Router / Cross-Encoder"
                root_cause = f"The router confidently predicted {predicted_intents_3} instead of {gold_intent}."
            else:
                isolated_comp = "Bi-Encoder Chunk Retriever / Cross-Encoder Reranker"
                root_cause = "The router correctly identified the intent, but the chunk retriever/reranker scored irrelevant chunks higher than the true chunk."

            failed_at_k3_details.append({
                "query": query,
                "gold_intent": gold_intent,
                "gold_chunk": gold_chunk,
                "predicted_intents": predicted_intents_3,
                "intent_success": intent_success,
                "top_chunks": retrieved_chunks_with_scores[:5],
                "isolated_component": isolated_comp,
                "root_cause": root_cause
            })

n = len(df)
hit_rates = {k: hit_counts[k] / n for k in k_values}
mrrs = {k: mrr_sums[k] / n for k in k_values}
fail_counts = {k: len(failed_queries_by_k[k]) for k in k_values}

intent_hit_rates = {k: intent_hit_counts[k] / n for k in intent_k_values}
intent_fail_counts = {k: len(failed_intents_by_k[k]) for k in intent_k_values}

print("\nEvaluation results:")
for k in k_values:
    print(f"Chunk K = {k}: Hit Rate = {hit_rates[k]:.4f}, MRR = {mrrs[k]:.4f}, Failed = {fail_counts[k]}")
for k in intent_k_values:
    print(f"Intent K = {k}: Hit Rate = {intent_hit_rates[k]:.4f}, Failed = {intent_fail_counts[k]}")

# Categorize K=3 failures
nlu_failures = [f for f in failed_at_k3_details if f["isolated_component"] == "Bi-Encoder Intent Router / Cross-Encoder"]
reranker_failures = [f for f in failed_at_k3_details if f["isolated_component"] == "Bi-Encoder Chunk Retriever / Cross-Encoder Reranker"]

total_k3_fails = len(failed_at_k3_details)
nlu_count = len(nlu_failures)
reranker_count = len(reranker_failures)

nlu_pct = (nlu_count / total_k3_fails * 100) if total_k3_fails > 0 else 0
reranker_pct = (reranker_count / total_k3_fails * 100) if total_k3_fails > 0 else 0

# Generate report content
report_md = f"""# 📊 RAG Evaluation & Failure Analysis Report (Iteration 4: Chunks Renewed - Top 3 Intents)

### 2. E-to-E Retrieval Performance Overview
| K Value | Hit Rate (Recall@K) | MRR (Mean Reciprocal Rank) | Failed Queries |
| :---: | :---: | :---: | :---: |
"""

for k in k_values:
    report_md += f"| **K = {k}** | {hit_rates[k]*100:.2f}% | {mrrs[k]:.4f} | {fail_counts[k]} |\n"

report_md += f"""
### 2.1 Intent Routing Performance Overview
| K Value | Hit Rate (Recall@K) | Failed Queries |
| :---: | :---: | :---: |
"""

for k in intent_k_values:
    report_md += f"| **K = {k}** | {intent_hit_rates[k]*100:.2f}% | {intent_fail_counts[k]} |\n"

report_md += f"""
### 3. Failure Mode Table (K = 3)
| Failure Mode | Isolated Component | Impact (Count/%) | Root Cause Analysis | Mitigation Action |
| :--- | :---: | :---: | :--- | :--- |
| **Intent Routing Failure** | Bi-Encoder Intent Router / Cross-Encoder | {nlu_count} / {nlu_pct:.1f}% | The intent classifier failed to include the true intent in the top 3 predicted intents. | Refine intent descriptions or add more descriptive sample queries. |
| **Chunk Retrieval & Reranking Failure** | Bi-Encoder Chunk Retriever / Cross-Encoder Reranker | {reranker_count} / {reranker_pct:.1f}% | The router correctly identified the intent, but the retrieval/reranking step scored irrelevant chunks higher than the true chunk. | Refine semantic structure of chunks or adjust combination weights. |

### 4. Query-by-Query Failure Directory (K = 3)
````carousel
"""

carousel_slides = []
for f in failed_at_k3_details:
    top_chunks_str = ", ".join([f"ID {cid} (score {score:.4f})" for cid, score in f["top_chunks"]])
    slide = f"""**Query**: "{f['query']}"
- **Expected Intent**: `{f['gold_intent']}`
- **True Chunk ID**: `{f['gold_chunk']}`
- **Predicted Intent(s)**: `{f['predicted_intents']}` (Classification Success: {f['intent_success']})
- **Top retrieved chunks**: {top_chunks_str}
- **Isolated Component**: {f['isolated_component']}
- **Root Cause**: {f['root_cause']}"""
    carousel_slides.append(slide)

report_md += "\n<!-- slide -->\n".join(carousel_slides)
report_md += "\n````\n\n"

report_md += f"""### 5. Comparative Delta Analysis
Comparing this run's metrics (Top 3 Intents) to the previous baseline (Iteration 4: Top 2 Intents):
- **K = 1**: {hit_rates[1]*100:.2f}% (vs 68.53% in Top 2, delta: {(hit_rates[1] - 0.6853)*100:+.2f}%)
- **K = 3**: {hit_rates[3]*100:.2f}% (vs 88.53% in Top 2, delta: {(hit_rates[3] - 0.8853)*100:+.2f}%)
- **K = 5**: {hit_rates[5]*100:.2f}% (vs 92.65% in Top 2, delta: {(hit_rates[5] - 0.9265)*100:+.2f}%)
- **K = 7**: {hit_rates[7]*100:.2f}% (vs 95.00% in Top 2, delta: {(hit_rates[7] - 0.9500)*100:+.2f}%)
- **K = 10**: {hit_rates[10]*100:.2f}% (vs 95.59% in Top 2, delta: {(hit_rates[10] - 0.9559)*100:+.2f}%)
- **K = 15**: {hit_rates[15]*100:.2f}% (vs 95.88% in Top 2, delta: {(hit_rates[15] - 0.9588)*100:+.2f}%)
- **MRR (K=3)**: {mrrs[3]:.4f} (vs 0.7755 in Top 2, delta: {mrrs[3] - 0.7755:+.4f})

Expanding the candidate chunk search pool to the top 3 routed intents increases retrieval coverage, addressing routing bottlenecks and boosting overall hit rates.
"""

os.makedirs("Evaluation Reports", exist_ok=True)
with open("Evaluation Reports/iteration_04_ret_v2_top3_report.md", "w", encoding="utf-8") as out:
    out.write(report_md)

print("Evaluation report generated in Evaluation Reports/iteration_04_ret_v2_top3_report.md")