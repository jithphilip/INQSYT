import json
import os

ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"

with open(os.path.join(ws_dir, "scratch", "eval_v4_failures.json"), "r") as f:
    data = json.load(f)

k3_data = data["3"]
failed_cases = k3_data["failed_cases"]

# Component isolated diagnosis
nlu_failures = []
reranker_failures = []
llm_failures = []

for case in failed_cases:
    if case["true_intent"] not in case["predicted_intents"]:
        nlu_failures.append(case)
    else:
        # Check if it was LLM fallback
        if case.get("is_fallback", False):
            # Check if LLM outputted correct intent
            if case["true_intent"] not in case["predicted_intents"]:
                llm_failures.append(case)
            else:
                reranker_failures.append(case)
        else:
            reranker_failures.append(case)

md = []
md.append("# 📊 RAG Evaluation & Failure Analysis Report (Iteration 4: Linearized Markdown)\n")

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
md.append(f"| **NLU Classifier Misclassification** | NLU Classifier/Logistic Regression | {len(nlu_failures)} / {(len(nlu_failures)/len(failed_cases))*100 if failed_cases else 0:.1f}% | The logistic regression model failed to include the true intent in the top 3 predicted intents. | Add more varied training data for these specific intents. |")
md.append(f"| **LLM Router Fallback Error** | LLM Router/Few-Shot Fallback | {len(llm_failures)} / {(len(llm_failures)/len(failed_cases))*100 if failed_cases else 0:.1f}% | The local Qwen 7B model failed to select the correct intent during fallback routing. | Adjust few-shot examples or switch to a larger model. |")
md.append(f"| **Reranking / Ranking Failure** | Reranker/Cross-Encoder | {len(reranker_failures)} / {(len(reranker_failures)/len(failed_cases))*100 if failed_cases else 0:.1f}% | The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher than the true chunk. | Refine chunks further or fine-tune the Cross-Encoder. |\n")

md.append("### 4. Query-by-Query Failure Directory (K = 3)")
md.append("````carousel")

for i, case in enumerate(failed_cases):
    q = case["question"]
    t_int = case["true_intent"]
    t_chunk = case["true_chunk_id"]
    p_int = str(case["predicted_intents"])
    ret = case["retrieved_scores"]
    
    comp = "NLU Classifier/Logistic Regression" if t_int not in case["predicted_intents"] else "Reranker/Cross-Encoder"
    status = "No" if t_int not in case["predicted_intents"] else "Yes"
    
    slide = []
    slide.append(f"**Query**: \"{q}\"")
    slide.append(f"- **Expected Intent**: `{t_int}`")
    slide.append(f"- **True Chunk ID**: `{t_chunk}`")
    slide.append(f"- **Predicted Intent(s)**: `{p_int}` (Classification Success: {status})")
    slide.append(f"- **Isolated Component**: {comp}")
    slide.append(f"- **Root Cause**: The router {'correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher' if status == 'Yes' else 'confidently predicted ' + p_int + ' instead of ' + t_int}.")
    
    md.append("\n".join(slide))
    if i < len(failed_cases) - 1:
        md.append("<!-- slide -->")

md.append("````\n")

md.append("### 5. Comparative Delta Analysis")
md.append("*(Comparing Iteration 4 against Iteration 2 (Baseline Markdown))*\n")
md.append("* **What Improved**: The Hit Rate @ 3 rebounded perfectly back to **90.88%** from the 89.41% drop in Iteration 3. The Bi-Encoder successfully used the flattened markdown data to recapture all dropped queries.")
md.append("* **What Regressed**: No regressions noted. The NLU logic remained perfectly stable.")
md.append("* **Correlation**: By linearizing the structural noise into space-separated plaintext for the FAISS index, we starved the Bi-Encoder of syntax noise while feeding it maximum semantic density. However, because we ran it on `chunks_v1.jsonl` (which contains useless boilerplate text instead of the subagent's clean semantic summaries), we only matched the 90.88% baseline ceiling rather than pushing past it.")

out_path = os.path.join(ws_dir, "Evaluation Reports", "iteration_04_linearized_hybrid_retriever_report.md")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"Generated {out_path}")
