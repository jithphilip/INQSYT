# Retrieval Pipeline Evaluation Benchmarks (JSONL Database)

This document records the evaluation benchmarks for the INQSYT RAG retrieval pipeline using the new JSON Lines database (`chunks.jsonl`), ran on **May 31, 2026**.

## 📊 Summary of Baseline Metrics (Top-10 Chunks)

| Metric | Previous (CSV) | Current (JSONL) | Difference | Explanation |
| :--- | :--- | :--- | :--- | :--- |
| **Total Queries** | **70** | **70** | — | Total number of test queries evaluated. |
| **Hit Rate@10** | **90.00%** (`0.9000`) | **91.43%** (`0.9143`) | **+1.43%** 📈 | The percentage of queries where the correct reference chunk was retrieved. |
| **Recall@10** | **90.00%** (`0.9000`) | **91.43%** (`0.9143`) | **+1.43%** 📈 | Out of all relevant chunks (1 per query), 91.43% were successfully found. |
| **Precision@10** | **9.00%** (`0.0900`) | **9.14%** (`0.0914`) | **+0.14%** 📈 | The proportion of retrieved chunks that are actually relevant. |
| **MRR** | **0.7286** | **0.7185** | **-0.0101** | Mean Reciprocal Rank of the correct chunk. |

---

## 🔍 Detailed Analysis of Missed Queries (6/70)

The pipeline failed to retrieve the correct reference chunk for exactly **6 out of 70** queries (down from 7 missed queries in the CSV baseline).

### 1. Refund & Tracking Overlap
* **Query:** *"Where do I find my refund details in Amazon?"*
  * **True Chunk ID:** `amz_track_004`
  * **Retrieved Chunks:** `['hotel_delivery_003', 'amz_ref_001', 'amz_track_005', 'amz_ret_002', 'amz_ret_001', 'undeliverable_package_003', 'amz_track_003', 'amz_track_002', 'track_package_003', 'amz_ret_012']`
* **Query:** *"How can I track the refund Amazon already issued?"*
  * **True Chunk ID:** `amz_track_004`
  * **Retrieved Chunks:** `['hotel_delivery_003', 'amz_ret_002', 'amz_ref_001', 'amz_track_005', 'amz_track_001', 'amz_track_003', 'amz_ref_003', 'amz_track_002', 'missing_tracking_information_003', 'missing_tracking_information_004']`

### 2. Carrier & Wrong Address Issues
* **Query:** *"Can the carrier help find a package that says delivered?"*
  * **True Chunk ID:** `missing_package_delivered_006`
  * **Retrieved Chunks:** `['late_delivery_004', 'late_delivery_008', 'track_package_004', 'missing_item_from_order_005', 'missing_tracking_information_005', 'missing_package_delivered_001', 'hotel_delivery_003', 'hotel_delivery_004', 'missing_package_delivered_007', 'undeliverable_package_005']`
* **Query:** *"What should I do if there is a delivery attempt notice?"*
  * **True Chunk ID:** `missing_package_delivered_003`
  * **Retrieved Chunks:** `['hotel_delivery_004', 'track_package_004', 'late_delivery_001', 'late_delivery_007', 'missing_package_delivered_005', 'hotel_delivery_003', 'missing_package_delivered_001', 'late_delivery_004', 'undeliverable_package_001', 'missing_package_delivered_004']`
* **Query:** *"Should I check my delivery address if my package is missing?"*
  * **True Chunk ID:** `missing_package_delivered_002`
  * **Retrieved Chunks:** `['missing_item_from_order_002', 'missing_package_delivered_004', 'hotel_delivery_004', 'track_package_004', 'missing_item_from_order_005', 'missing_item_from_order_001', 'undeliverable_package_005', 'late_delivery_008', 'missing_package_delivered_001', 'late_delivery_002']`
* **Query:** *"My address was wrong and package is undeliverable. What now?"*
  * **True Chunk ID:** `undeliverable_package_003`
  * **Retrieved Chunks:** `['undeliverable_package_004', 'track_package_003', 'undeliverable_package_002', 'missing_item_from_order_005', 'late_delivery_008', 'missing_package_delivered_002', 'missing_package_delivered_004', 'undeliverable_package_001', 'hotel_delivery_004', 'missing_tracking_information_005']`
