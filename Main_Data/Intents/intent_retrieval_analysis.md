# Intent-Based RAG Retrieval Diagnostic Analysis (K=3)

This report analyzes the performance, errors, and optimization pathways of the intent-based routing retrieval pipeline, evaluated on **June 4, 2026** after implementing the mitigation strategies (Multi-Label Search and Confidence Fallback).

---

## 📊 1. Classifier Performance (Logistic Regression)

The Logistic Regression classifier was retrained on the balanced **1,200 labeled queries** (200 per intent) generated using existing templates and seeds.

### Validation Metrics
* **Mean Cross-Validation Accuracy (5-Fold)**: **97.33%** (`± 1.41%`)
* **Training Set Accuracy**: **98.00%**

---

## 📉 2. Retrieval Pipeline Benchmarks (K=3 Comparison)

Implementing **Multi-Label Intent Search** (difference threshold $\le 0.2$) and **Confidence Fallback** (threshold $< 0.5$) successfully narrowed the performance gap between intent-guided routing and baseline global search:

| Benchmark Metric | Baseline RAG (No Routing) | Intent-Guided RAG (Initial) | Intent-Guided RAG (Retrained Only) | Intent-Guided RAG (With Mitigations) |
| :--- | :--- | :--- | :--- | :--- |
| **Hit Rate@3** | **82.86%** (`58/70`) | **71.43%** (`50/70`) | **75.71%** (`53/70`) | **80.00%** (`56/70`) 🚀 |
| **MRR** | **0.7452** | **0.6595** | **0.6952** | **0.7214** |
| **Missed Queries** | **12** | **20** | **17** | **14** |

---

## 🔍 3. Taxonomy of Failures & Missed Queries

The remaining 14 missed queries are classified below:

### Error Type 1: Hard Boundary Routing Failures (0 Misses! 🎉)
Thanks to the retrained classifier and the mitigations (confidence fallback to `general_query` and top-2 multi-label search), **no queries failed due to hard exclusion boundaries**. Borderline queries are now gracefully routed to multiple intents or fallback to global search.

### Error Type 2: Intra-Intent Semantic Competition (14 Misses)
This is now the sole cause of misses. The retriever selects the correct intent(s), but multiple highly similar chunks within the filtered list push the exact target chunk below the top-3.

#### Representative Examples of Competition Failures:
```carousel
```python
# Miss 1: Return status tracking competition
Query = "How can I see where my return is right now?"
True_Chunk = "amz_track_001"  # Returns details
Predicted_Intent = "returns_refunds"  # (Correct!)
Retrieved = [
  "amz_track_002", # (Tracking returns)
  "missing_item_from_order_004", # (Refund details)
  "amz_ret_010"  # (Returns navigation)
]
```
<!-- slide -->
```python
# Miss 2: Late delivery status overlap
Query = "My delivery date has passed. What should I do now?"
True_Chunk = "late_delivery_002"  # What to do if delivery is late
Predicted_Intent = "track_order"  # (Correct!)
Retrieved = [
  "late_delivery_006", # (48 hours passed)
  "late_delivery_001", # (Late deliveries overview)
  "track_package_004"  # (Fix a delivery issue)
]
```
<!-- slide -->
```python
# Miss 3: Check delivery address competition
Query = "Should I check my delivery address if my package is missing?"
True_Chunk = "missing_package_delivered_002"  # Missing package delivered address check
Predicted_Intent = "track_order"  # (Correct!)
Retrieved = [
  "track_package_004",
  "missing_package_delivered_004",
  "missing_package_delivered_001"
]
```
```

---

## 🛠️ 4. Recommendations & Next Steps
With **80% Hit Rate@3**, the intent-guided system is now highly competitive with baseline global search while gaining metadata-driven routing accuracy and context isolation. To close the remaining gap:
1. **Extend Cross-Encoder Candidate Pool**: Increase `INITIAL_K` from 15 to 25 to capture target chunks during semantic competition before ranking them.
2. **Context Enriched Chunk Titles**: Adjust chunking definitions to inject document metadata directly into the first line of text to help the Bi-Encoder differentiate similar sections.
