# Retrieval Pipeline Evaluation Benchmarks

This document records the baseline evaluation benchmarks for the INQSYT RAG retrieval pipeline, ran on **May 31, 2026**.

## 📊 Summary of Baseline Metrics (Top-10 Chunks)

| Metric | Score | Explanation |
| :--- | :--- | :--- |
| **Total Queries** | **70** | Total number of test queries evaluated. |
| **Hit Rate@10** | **90.00%** (`0.9000`) | The percentage of queries where the correct reference chunk was retrieved in the top 10 results. |
| **Recall@10** | **90.00%** (`0.9000`) | Out of all relevant chunks (1 per query), 90% were successfully found. |
| **Precision@10** | **9.00%** (`0.0900`) | Since there is exactly 1 true correct chunk per query, the maximum possible precision at $K=10$ is $1/10 = 10\%$. |
| **MRR (Mean Reciprocal Rank)** | **0.7286** | Evaluates how high up the correct chunk is ranked in the top results. An MRR of ~0.73 means the correct chunk is on average ranked **1st or 2nd** when retrieved. |

---

## 🔍 Detailed Analysis of Missed Queries (7/70)

The pipeline failed to retrieve the correct reference chunk for **7 out of 70** queries. Analyzing these misses reveals semantic overlaps or phrasing gaps.

### 1. Refund & Tracking Overlap
* **Query:** *"Where do I find my refund details in Amazon?"*
  * **True Chunk ID:** `amz_track_004`
  * **Retrieved Chunks:** `['hotel_delivery_003', 'amz_ref_001', 'amz_track_005', 'amz_ret_002', 'amz_ret_001', 'undeliverable_package_003', 'amz_track_003', 'track_package_003', 'amz_ref_002', 'amz_ret_012']`
* **Query:** *"How can I track the refund Amazon already issued?"*
  * **True Chunk ID:** `amz_track_004`
  * **Retrieved Chunks:** `['hotel_delivery_003', 'amz_ret_002', 'amz_ref_001', 'amz_track_005', 'amz_track_001', 'amz_track_003', 'amz_ref_003', 'amz_track_002', 'missing_tracking_information_003', 'missing_tracking_information_004']`
  * *Observation:* The true chunk (`amz_track_004`) was pushed out by other refund-related pages (`amz_ref_001`, `amz_ret_002`). This points to semantic overlap between tracking and refunds.

### 2. Colloquial Phrasing
* **Query:** *"how can i see where my parcel is now"*
  * **True Chunk ID:** `track_package_001`
  * **Retrieved Chunks:** `['track_package_003', 'track_package_004', 'missing_package_delivered_007', 'missing_package_delivered_004', 'late_delivery_004', 'missing_item_from_order_002', 'missing_item_from_order_005', 'hotel_delivery_004', 'missing_package_delivered_001', 'late_delivery_008']`
  * *Observation:* Using the word *"parcel"* (instead of standard terms like *"package"* or *"shipment"*) caused the model to miss the primary tracking overview chunk (`track_package_001`).

### 3. Carrier & Wrong Address Issues
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

---

## 💡 Recommendations for Future Improvements

To improve the Hit Rate beyond **90%** and MRR beyond **0.7286**:
1. **Query Expansion / Synonym Mapping**: Inject a preprocessing step to map colloquial terms (e.g., *"parcel"*) to standardized domain terms (e.g., *"package"*).
2. **Increase Initial Candidate Size**: Increase `INITIAL_K` from 15 to 20 or 25. This gives the Cross-Encoder a wider pool of candidates to evaluate, making it more likely that the correct chunk is captured in the initial fast-pass.
