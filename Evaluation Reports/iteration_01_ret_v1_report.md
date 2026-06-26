# 📊 RAG Evaluation & Failure Analysis Report

This report summarizes the performance evaluation of the hybrid RAG system across $K = 1, 3, 5, 7$ and provides a detailed failure mode analysis of the system at $K = 3$.

---

## 📈 E-to-E Retrieval Performance Overview

The evaluation was performed over the full **340 query dataset** using our optimized cascading hybrid router (`margin <= 0.35` and `top1_prob < 0.13`), BGE vector search embeddings, and MS-MARCO Cross-Encoder reranking. 

A query is considered a **Hit** if the ground truth chunk is retrieved within the top $K$ results.

| K Value | Hit Rate (Recall@K) | MRR (Mean Reciprocal Rank) | Failed Queries |
| :---: | :---: | :---: | :---: |
| **K = 1** | 84.12% | 0.7676 | 54 / 340 |
| **K = 3** | **90.29%** | **0.7875** | **33 / 340** |
| **K = 5** | 91.18% | 0.7892 | 30 / 340 |
| **K = 7** | 92.06% | 0.7906 | 27 / 340 |

---

## 🔍 Failure Mode Table (K = 3)

The 33 failed queries at $K=3$ have been classified into three distinct failure modes. 

| Failure Mode | Isolated Component | Impact (Count) | Root Cause Analysis | Mitigation Action |
| :--- | :---: | :---: | :--- | :--- |
| **NLU Classifier Misclassification** | NLU Classifier (Logistic Regression) | 19 / 33 (57.6%) | The intent classifier misrouted queries containing high-overlap keywords (e.g., "address", "invoice", "rules", "failed") to incorrect domains. This completely filtered out the true intent and its associated chunks. | • Expand classifier training data with focused paraphrases.<br>• Inject disambiguation keywords to break spurious correlations. |
| **LLM Router Fallback Error** | LLM Router (Few-Shot Fallback) | 5 / 33 (15.2%) | Low-confidence classifier queries fell back to the LLM (Qwen-7B), but the model failed to map specific query semantics (like checkout feedback or saving files) and routed them to `other_query`. | • Add explicit few-shot routing examples in the LLM system prompt for edge cases like surveys, feedback, and downloading invoices. |
| **Reranking / Ranking Failure** | Reranker (Cross-Encoder) | 9 / 33 (27.3%) | The router successfully predicted the correct intent, but the Cross-Encoder rerank scored other related chunks slightly higher, pushing the true chunk to Rank 4 or lower. | • Merge highly redundant or duplicate chunks.<br>• Enrich chunk metadata with context-aware question tags (sample queries). |

---

## 📝 Query-by-Query Failure Directory (K = 3)

Below is the complete analysis of the 33 failed queries at $K = 3$, showing the expected versus predicted behavior, isolated component, and the diagnostic root cause.

```carousel
### Failure Case 1: "Is it too late to edit my purchase?"
* **Expected Intent**: `modify_order`
* **True Chunk ID**: `amz_ord_001`
* **Predicted Intent(s)**: `["modify_order"]` *(Routing: Correct)*
* **Top 3 Retrieved Chunks**: 
  1. `amz_can_001` (Rerank score: -5.89)
  2. `cancel_items_and_orders_001` (Rerank score: -7.21)
  3. `change_your_order_information_001` (Rerank score: -10.51)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The query specifically asks about editing an existing order. The vector index returned cancel/change chunks, and the reranker scored them higher than the true chunk `amz_ord_001`, which fell outside the top 3.
<!-- slide -->
### Failure Case 2: "Can I correct a typo in my delivery destination?"
* **Expected Intent**: `modify_address`
* **True Chunk ID**: `billing_shipping_addresses_001`
* **Predicted Intent(s)**: `["check_shipping_policies", "modify_order"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier failed due to vocabulary overlap ("destination" and "correct typo") and routed the query to shipping policies and order modification, completely filtering out the correct `modify_address` intent.
<!-- slide -->
### Failure Case 3: "I want to save my proof of purchase to my computer."
* **Expected Intent**: `view_invoice`
* **True Chunk ID**: `print_an_invoice_001`
* **Predicted Intent(s)**: `["other_query"]` *(Routing: Fail)*
* **Isolated Component**: LLM Router (Fallback)
* **Root Cause**: The query fell back to the LLM due to low classifier confidence. The LLM failed to link "proof of purchase" to `view_invoice` and returned `other_query`, which contains no relevant chunks.
<!-- slide -->
### Failure Case 4: "Can I get a VAT invoice for my digital purchases?"
* **Expected Intent**: `view_invoice`
* **True Chunk ID**: `print_an_invoice_001`
* **Predicted Intent(s)**: `["check_tax_rates"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: The keyword "VAT" strongly biased the classifier toward `check_tax_rates` instead of recognizing the user was requesting a copy of their invoice document (`view_invoice`).
<!-- slide -->
### Failure Case 5: "How can I file a complaint about the delivery service?"
* **Expected Intent**: `submit_feedback`
* **True Chunk ID**: `amazon_consumer_surveys_001`
* **Predicted Intent(s)**: `["report_missing_package", "check_shipping_policies"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: Complaint queries about delivery were misrouted to missing packages/shipping policies due to strong keyword associations with "delivery service".
<!-- slide -->
### Failure Case 6: "I want to share my thoughts on the new checkout design."
* **Expected Intent**: `submit_feedback`
* **True Chunk ID**: `amazon_consumer_surveys_001`
* **Predicted Intent(s)**: `["other_query"]` *(Routing: Fail)*
* **Isolated Component**: LLM Router (Fallback)
* **Root Cause**: The LLM router failed to map general design feedback to the `submit_feedback` intent.
<!-- slide -->
### Failure Case 7: "How to fill out the delivery feedback form?"
* **Expected Intent**: `submit_feedback`
* **True Chunk ID**: `amazon_consumer_surveys_001`
* **Predicted Intent(s)**: `["other_query"]` *(Routing: Fail)*
* **Isolated Component**: LLM Router (Fallback)
* **Root Cause**: The LLM router classified "delivery feedback form" as `other_query` instead of routing it to `submit_feedback`.
<!-- slide -->
### Failure Case 8: "I want to leave feedback for a third-party merchant."
* **Expected Intent**: `submit_feedback`
* **True Chunk ID**: `amazon_consumer_surveys_001`
* **Predicted Intent(s)**: `["other_query"]` *(Routing: Fail)*
* **Isolated Component**: LLM Router (Fallback)
* **Root Cause**: Leaving feedback for third-party merchants was misclassified as `other_query` by the LLM.
<!-- slide -->
### Failure Case 9: "Can I change the payment method my teen uses?"
* **Expected Intent**: `manage_teen_account`
* **True Chunk ID**: `set_order_approvals_for_a_teen_login_001`
* **Predicted Intent(s)**: `["manage_teen_account", "manage_wallet_cards"]` *(Routing: Correct)*
* **Top 3 Retrieved Chunks**:
  1. `what_is_a_teen_login_001` (Rerank score: 1.77)
  2. `change_your_default_payment_methods_001` (Rerank score: 0.43)
  3. `removing_a_teen_login_from_an_amazon_household_001` (Rerank score: -0.14)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The true chunk `set_order_approvals_for_a_teen_login_001` was ranked 4th, as default payment methods and household removal chunks scored higher due to "payment method" and "teen" overlaps.
<!-- slide -->
### Failure Case 10: "How do I delete a secondary profile from my account?"
* **Expected Intent**: `manage_profile_settings`
* **True Chunk ID**: `add_a_shopping_profile_001`
* **Predicted Intent(s)**: `["close_account"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: The words "delete" and "profile from my account" triggered a false positive for the `close_account` intent.
<!-- slide -->
### Failure Case 11: "I want to change the email address linked to my profile."
* **Expected Intent**: `manage_profile_settings`
* **True Chunk ID**: `what_are_mobile_phone_number_accounts_001`
* **Predicted Intent(s)**: `["modify_address"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: The keyword "address" strongly biased the classifier toward modifying physical shipping addresses (`modify_address`) rather than account profile settings.
<!-- slide -->
### Failure Case 12: "How do I configure my account region and country preferences?"
* **Expected Intent**: `manage_account_settings`
* **True Chunk ID**: `change_your_account_settings_001`
* **Predicted Intent(s)**: `["convert_currency", "manage_notifications"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: Regional settings were misclassified as currency conversion due to overlaps between "region/country" and "currency".
<!-- slide -->
### Failure Case 13: "Where do I change my primary account location?"
* **Expected Intent**: `manage_account_settings`
* **True Chunk ID**: `change_your_account_settings_001`
* **Predicted Intent(s)**: `["modify_address", "manage_profile_settings"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: The word "location" was treated as a physical address, misrouting the query to modifying shipping addresses.
<!-- slide -->
### Failure Case 14: "My transaction failed, how do I update the payment method?"
* **Expected Intent**: `resolve_declined_payment`
* **True Chunk ID**: `resolve_a_declined_payment_001`
* **Predicted Intent(s)**: `["resolve_declined_payment", "manage_wallet_cards"]` *(Routing: Correct)*
* **Top 3 Retrieved Chunks**:
  1. `manage_your_backup_payment_methods_001` (Rerank score: 5.60)
  2. `change_your_default_payment_methods_001` (Rerank score: 4.95)
  3. `manage_payment_methods_001` (Rerank score: 3.55)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The query overlaps heavily with general wallet cards operations. As a result, backing up and changing default payment method chunks scored higher than the declined payment resolution chunk.
<!-- slide -->
### Failure Case 15: "How to update payment details on a pending transaction?"
* **Expected Intent**: `resolve_declined_payment`
* **True Chunk ID**: `resolve_a_declined_payment_001`
* **Predicted Intent(s)**: `["manage_wallet_cards"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: "Update payment details" strongly pulled the classifier to `manage_wallet_cards`, missing that it was for an active pending transaction.
<!-- slide -->
### Failure Case 16: "I received a demand for payment via gift cards."
* **Expected Intent**: `report_payment_scam`
* **True Chunk ID**: `amz_sec_004`
* **Predicted Intent(s)**: `["report_payment_scam", "manage_wallet_cards"]` *(Routing: Correct)*
* **Top 3 Retrieved Chunks**:
  1. `avoiding_payment_scams_001` (Rerank score: -2.55)
  2. `identifying_a_scam_001` (Rerank score: -3.27)
  3. `scam_trends_007` (Rerank score: -3.30)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: General scam avoidance chunks were ranked higher than the specific `amz_sec_004` (scam trends) chunk.
<!-- slide -->
### Failure Case 17: "Are opened video games or software eligible for returns?"
* **Expected Intent**: `check_return_eligibility`
* **True Chunk ID**: `amz_ret_004`
* **Predicted Intent(s)**: `["check_restocking_fees"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: Return eligibility queries on opened items were misclassified under restocking fees due to historical correlations.
<!-- slide -->
### Failure Case 18: "How do I check if my purchase can be returned?"
* **Expected Intent**: `check_return_eligibility`
* **True Chunk ID**: `amz_ret_006`
* **Predicted Intent(s)**: `["check_return_eligibility", "check_restocking_fees"]` *(Routing: Correct)*
* **Top 3 Retrieved Chunks**:
  1. `amz_ret_001` (Rerank score: 2.14)
  2. `amz_ret_012` (Rerank score: -0.95)
  3. `amz_ret_008` (Rerank score: -1.45)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The true chunk `amz_ret_006` was pushed to 4th place because other return eligibility chunks (001/012/008) scored higher.
<!-- slide -->
### Failure Case 19: "How do I manage email alerts for my packages?"
* **Expected Intent**: `manage_delivery_alerts`
* **True Chunk ID**: `turn_off_text_updates_001`
* **Predicted Intent(s)**: `["manage_notifications"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: The term "email alerts" led the classifier to route to general email/newsletter notifications (`manage_notifications`) instead of delivery-specific alerts.
<!-- slide -->
### Failure Case 20: "Where do I edit my delivery alert preferences?"
* **Expected Intent**: `manage_delivery_alerts`
* **True Chunk ID**: `turn_off_text_updates_001`
* **Predicted Intent(s)**: `["manage_notifications", "modify_order"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: "Alert preferences" was misrouted to general account notifications.
<!-- slide -->
### Failure Case 21: "My tracking is stuck in transit, how to report delay?"
* **Expected Intent**: `check_delivery_delay`
* **True Chunk ID**: `missing_tracking_information_003`
* **Predicted Intent(s)**: `["check_delivery_delay"]` *(Routing: Correct)*
* **Top 3 Retrieved Chunks**:
  1. `late_delivery_007` (Rerank score: -3.75)
  2. `missing_tracking_information_005` (Rerank score: -4.81)
  3. `missing_tracking_information_002` (Rerank score: -9.82)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: Other tracking chunks (005/002) and general late delivery chunks scored higher than the true chunk `missing_tracking_information_003`.
<!-- slide -->
### Failure Case 22: "What should I do if my shipping address was incorrect?"
* **Expected Intent**: `resolve_undeliverable_package`
* **True Chunk ID**: `undeliverable_package_002`
* **Predicted Intent(s)**: `["modify_address", "report_missing_item"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: The presence of "shipping address" caused a false routing to modifying address settings.
<!-- slide -->
### Failure Case 23: "My shipment failed delivery because the business was closed."
* **Expected Intent**: `resolve_undeliverable_package`
* **True Chunk ID**: `undeliverable_package_001`
* **Predicted Intent(s)**: `["resolve_declined_payment", "check_delivery_delay"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: "Failed delivery" triggered payment decline and delivery delay classification due to a lack of close-match training data for business closures.
<!-- slide -->
### Failure Case 24: "Do I need to be home to receive a high-value package?"
* **Expected Intent**: `check_delivery_rules`
* **True Chunk ID**: `secure_delivery_otp_001`
* **Predicted Intent(s)**: `["report_missing_package", "check_shipping_policies"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: Home-delivery availability questions were routed to missing packages/shipping policies because of generic shipping term overlaps.
<!-- slide -->
### Failure Case 25: "Can I request that my package be left inside the garage?"
* **Expected Intent**: `check_delivery_rules`
* **True Chunk ID**: `secure_delivery_otp_001`
* **Predicted Intent(s)**: `["report_missing_package", "check_shipping_policies"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: Requesting package placement was misclassified as a missing package or general policy query.
<!-- slide -->
### Failure Case 26: "What are the rules for apartment building deliveries?"
* **Expected Intent**: `check_delivery_rules`
* **True Chunk ID**: `shipping_prisons_001`
* **Predicted Intent(s)**: `["check_shipping_policies"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: Delivery rules for apartments were misrouted to general shipping policies.
<!-- slide -->
### Failure Case 27: "How do I manage my delivery preferences for my household?"
* **Expected Intent**: `check_delivery_rules`
* **True Chunk ID**: `secure_delivery_otp_001`
* **Predicted Intent(s)**: `["other_query"]` *(Routing: Fail)*
* **Isolated Component**: LLM Router (Fallback)
* **Root Cause**: The LLM router mapped household preferences to `other_query` instead of `check_delivery_rules`.
<!-- slide -->
### Failure Case 28: "What should I do if my parcel was stolen?"
* **Expected Intent**: `report_missing_package`
* **True Chunk ID**: `missing_package_delivered_002`
* **Predicted Intent(s)**: `["report_missing_package", "report_missing_item"]` *(Routing: Correct)*
* **Top 3 Retrieved Chunks**:
  1. `missing_item_from_order_003` (Rerank score: 1.27)
  2. `missing_item_from_order_002` (Rerank score: 1.25)
  3. `missing_item_from_order_005` (Rerank score: -1.61)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: Since both `report_missing_package` and `report_missing_item` were predicted, their combined candidate chunks were retrieved. Missing item chunks ranked higher than the stolen package chunk.
<!-- slide -->
### Failure Case 29: "My delivery was short one item, how to get a replacement?"
* **Expected Intent**: `report_missing_item`
* **True Chunk ID**: `missing_item_from_order_006`
* **Predicted Intent(s)**: `["report_missing_item"]` *(Routing: Correct)*
* **Top 3 Retrieved Chunks**:
  1. `missing_packing_slip_001` (Rerank score: -4.98)
  2. `missing_item_from_order_002` (Rerank score: -6.12)
  3. `missing_item_from_order_004` (Rerank score: -6.28)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The true chunk `missing_item_from_order_006` was ranked 4th due to higher overlap with general missing items 002/004 and packing slip chunks.
<!-- slide -->
### Failure Case 30: "How do I report phishing attempts on my account?"
* **Expected Intent**: `identify_phishing_scams`
* **True Chunk ID**: `report_suspicious_activity_001`
* **Predicted Intent(s)**: `["identify_phishing_scams", "report_payment_scam"]` *(Routing: Correct)*
* **Top 3 Retrieved Chunks**:
  1. `report_a_scam_001` (Rerank score: 5.22)
  2. `amz_sec_001` (Rerank score: 3.24)
  3. `avoiding_payment_scams_001` (Rerank score: -0.41)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: Chunks for reporting general scams and security 001 scored higher than the specific phishing reporting chunk.
<!-- slide -->
### Failure Case 31: "How are tax rates determined for international shipping?"
* **Expected Intent**: `check_tax_rates`
* **True Chunk ID**: `vat_rates_001`
* **Predicted Intent(s)**: `["check_international_returns"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: The phrase "international shipping" caused a false routing to checking international returns.
<!-- slide -->
### Failure Case 32: "Where do I see the tax breakdown of my invoice?"
* **Expected Intent**: `check_tax_rates`
* **True Chunk ID**: `about_us_state_sales_and_use_taxes_002`
* **Predicted Intent(s)**: `["view_invoice"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: The keyword "invoice" caused a false routing to viewing invoice instead of checking tax rates.
<!-- slide -->
### Failure Case 33: "How to turn off marketing push notifications in the app?"
* **Expected Intent**: `manage_notifications`
* **True Chunk ID**: `change_your_subscription_email_preferences_001`
* **Predicted Intent(s)**: `["manage_account_settings", "manage_delivery_alerts"]` *(Routing: Fail)*
* **Isolated Component**: NLU Classifier
* **Root Cause**: Push notifications settings in the app were misrouted to account settings or delivery alerts.
```
