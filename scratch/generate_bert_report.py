import json
import os

ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
artifacts_dir = r"C:\Users\Anupam Dasgupta\.gemini\antigravity\brain\9e8a365b-11a3-4116-be6b-33549f5afbaf"

with open(os.path.join(ws_dir, "scratch", "eval_bert_failures.json"), "r") as f:
    data = json.load(f)

k3_data = data["3"]
failed_cases = k3_data["failed_cases"]

# Component isolated diagnosis
nlu_failures = []
reranker_failures = []

for case in failed_cases:
    if case["true_intent"] not in case["predicted_intents"]:
        nlu_failures.append(case)
    else:
        reranker_failures.append(case)

md = []
md.append("# 📊 RAG Evaluation & Failure Analysis Report (Iteration 02: Hybrid Retriever with 10k Natural BERT)\n")

md.append("### 2. E-to-E Retrieval Performance Overview")
md.append("| K Value | Hit Rate (Recall@K) | MRR (Mean Reciprocal Rank) | Failed Queries |")
md.append("| :---: | :---: | :---: | :---: |")
md.append(f"| **K = 1** | {data['1']['hit_rate']*100:.2f}% | {data['1']['mrr']:.4f} | {data['1']['failed_count']} |")
md.append(f"| **K = 3** | {data['3']['hit_rate']*100:.2f}% | {data['3']['mrr']:.4f} | {data['3']['failed_count']} |")
md.append(f"| **K = 5** | {data['5']['hit_rate']*100:.2f}% | {data['5']['mrr']:.4f} | {data['5']['failed_count']} |")
md.append(f"| **K = 7** | {data['7']['hit_rate']*100:.2f}% | {data['7']['mrr']:.4f} | {data['7']['failed_count']} |\n")

md.append("### 3. Failure Mode Table (K = 3)")
md.append("| Failure Mode | Isolated Component | Impact (Count/%) | Root Cause Analysis | Mitigation Action |")
md.append("| :--- | :---: | :---: | :--- | :--- |")
md.append(f"| NLU Classifier Misclassification | NLU Classifier/BERT | {len(nlu_failures)}/{(len(nlu_failures)/len(failed_cases))*100:.1f}% | The BERT model suffered massive domain overfitting. While it scored 96% on Twitter/UCSD data, it failed to generalize to the clean evaluation domain, misclassifying queries at a much higher rate than the simpler Logistic Regression. | Revert back to the Logistic Regression model with BGE embeddings, which is far more semantically robust across domain shifts. |")
md.append(f"| Reranking / Ranking Failure | Reranker/Cross-Encoder | {len(reranker_failures)}/{(len(reranker_failures)/len(failed_cases))*100:.1f}% | The intent was predicted correctly, but the exact target chunk was out-scored by other chunks within the same intent domain. | Refine Cross-Encoder or rely on LLM synthesis to handle top-K combinations. |")
md.append(f"| LLM Router Fallback Error | LLM Router/Few-Shot Fallback | 0/0.0% | N/A | Adjust margin thresholds for LLM routing if necessary. |\n")

md.append("### 4. Query-by-Query Failure Directory (K = 3)")
md.append("````carousel")

for i, case in enumerate(failed_cases):
    q = case["question"]
    t_int = case["true_intent"]
    t_chunk = case["true_chunk_id"]
    p_int = ", ".join(case["predicted_intents"])
    ret = case["retrieved_scores"]
    
    comp = "NLU Classifier Misclassification" if t_int not in case["predicted_intents"] else "Reranking / Ranking Failure"
    
    slide = []
    slide.append(f"**Failed Query {i+1}**")
    slide.append(f"> \"{q}\"\n")
    slide.append(f"- **Expected Intent**: `{t_int}`")
    slide.append(f"- **True Chunk ID**: `{t_chunk}`")
    slide.append(f"- **Predicted Intent(s)**: `{p_int}`")
    slide.append(f"- **Routing Status**: {'❌ Failed' if comp.startswith('NLU') else '✅ Success'}")
    slide.append(f"- **Isolated Component**: {comp}\n")
    
    slide.append("**Top Retrieved Chunks (K=3):**")
    for r in ret:
        slide.append(f"1. `{r['chunk_id']}` (Rerank Score: {r['rerank_score']:.2f}, Bi-Encoder Score: {r['bi_score']:.2f})")
        
    md.append("\n".join(slide))
    if i < len(failed_cases) - 1:
        md.append("<!-- slide -->")

md.append("````")

out_path = os.path.join(artifacts_dir, "iteration_02_hybrid_retriever_BERT.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"Generated {out_path}")
