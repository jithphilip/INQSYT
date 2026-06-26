import json
import os

ws_dir = r'c:\Users\Anupam Dasgupta\Desktop\INQSYT'
failures_path = os.path.join(ws_dir, 'scratch', 'new_failures_k3.json')
report_path = os.path.join(r'C:\Users\Anupam Dasgupta\.gemini\antigravity\brain\9e8a365b-11a3-4116-be6b-33549f5afbaf', 'Evaluation Reports', 'iteration_04_hybrid_retriever_v2.md')

with open(failures_path, 'r', encoding='utf-8') as f:
    failures = json.load(f)

# Rule: Categorize failures into NLU Classifier, LLM Router, Reranker
nlu_failures = []
llm_failures = []
reranker_failures = []

for item in failures:
    q = item['question']
    true_intent = item['true_intent']
    pred_intents = item['predicted_intents']
    is_fallback = item['is_fallback']
    
    if true_intent not in pred_intents:
        if is_fallback:
            llm_failures.append(item)
        else:
            nlu_failures.append(item)
    else:
        reranker_failures.append(item)

# Build Failure Mode Table
n_nlu = len(nlu_failures)
n_llm = len(llm_failures)
n_reranker = len(reranker_failures)
total = len(failures)

table = f'''| Failure Mode | Isolated Component | Impact (Count/%) | Root Cause Analysis | Mitigation Action |
| :--- | :---: | :---: | :--- | :--- |
| **NLU Classifier Misclassification** | NLU Classifier/Logistic Regression | {n_nlu} / {n_nlu/total*100:.1f}% | The logistic regression model failed to include the true intent in the top 3 predicted intents. | Add more varied training data for these specific intents. |
| **LLM Router Fallback Error** | LLM Router/Few-Shot Fallback | {n_llm} / {n_llm/total*100:.1f}% | The local Qwen 7B model failed to select the correct intent during fallback routing. | Adjust few-shot examples or switch to a larger model. |
| **Reranking / Ranking Failure** | Reranker/Cross-Encoder | {n_reranker} / {n_reranker/total*100:.1f}% | The router correctly identified the intent, but the dense chunks confused the reranker. | Execute the Chunk Optimization strategy (chunks_cleaned). |'''

# Build Query Directory (Carousel)
carousel_slides = []
for item in failures:
    q = item['question']
    true_intent = item['true_intent']
    true_chunk = item['true_chunk_id']
    pred_intents = item['predicted_intents']
    is_fallback = item['is_fallback']
    
    if true_intent not in pred_intents:
        if is_fallback:
            comp = 'LLM Router/Few-Shot Fallback'
            cause = 'The local Qwen model did not output the true intent in its JSON response.'
        else:
            comp = 'NLU Classifier/Logistic Regression'
            cause = f'The LR model confidently predicted {pred_intents} instead of {true_intent}.'
    else:
        comp = 'Reranker/Cross-Encoder'
        cause = 'The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher than the true chunk.'
        
    slide = f'''**Query**: "{q}"
- **Expected Intent**: `{true_intent}`
- **True Chunk ID**: `{true_chunk}`
- **Predicted Intent(s)**: `{pred_intents}` (Classification Success: {'Yes' if true_intent in pred_intents else 'No'})
- **Isolated Component**: {comp}
- **Root Cause**: {cause}'''
    carousel_slides.append(slide)

carousel_str = '````carousel\n' + '\n<!-- slide -->\n'.join(carousel_slides) + '\n````'

md = f'''# 📊 RAG Evaluation & Failure Analysis Report (Iteration 4: LR Dataset v2 + Local Qwen)

### 2. E-to-E Retrieval Performance Overview
| K Value | Hit Rate (Recall@K) | MRR (Mean Reciprocal Rank) | Failed Queries |
| :---: | :---: | :---: | :---: |
| **K = 1** | 84.41% | 0.7623 | 53/340 |
| **K = 3** | 90.88% | 0.7823 | 31/340 |
| **K = 5** | 92.35% | 0.7855 | 26/340 |
| **K = 7** | 93.82% | 0.7876 | 21/340 |

### 3. Failure Mode Table (K = 3)
{table}

### 4. Query-by-Query Failure Directory (K = 3)
{carousel_str}
'''

os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(md)

print(f'Report written to {report_path}')
