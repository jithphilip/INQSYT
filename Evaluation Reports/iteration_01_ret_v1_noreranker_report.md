# 📊 RAG Evaluation & Failure Analysis Report (Optimized Hybrid Router - No Reranker)

This report summarizes the performance evaluation of the hybrid RAG system across $K = 1, 3, 5, 7$ and provides a detailed failure mode analysis of the system at $K = 3$ under the optimized routing setup with the **Cross-Encoder Reranker disabled**. Chunks are filtered by intent and ranked solely by BGE Bi-Encoder similarity.

---

## 📈 E-to-E Retrieval Performance Overview

The evaluation was performed over the full **340 query dataset** using our optimized cascading hybrid router (`margin <= 0.35` and `top1_prob < 0.13`) and BGE vector search embeddings. Reranking was disabled.

A query is considered a **Hit** if the ground truth chunk is retrieved within the top $K$ results.

| K Value | Hit Rate (Recall@K) | MRR (Mean Reciprocal Rank) | Failed Queries |
| :---: | :---: | :---: | :---: |
| **K = 1** | 72.35% | 0.7235 | 94 / 340 |
| **K = 3** | **89.41%** | **0.8010** | **36 / 340** |
| **K = 5** | 92.94% | 0.8088 | 24 / 340 |
| **K = 7** | 94.71% | 0.8116 | 18 / 340 |

---

## 🔍 Failure Mode Table (K = 3)

The 36 failed queries at $K=3$ have been classified into distinct failure modes.

| Failure Mode | Isolated Component | Impact (Count/%) | Root Cause Analysis | Mitigation Action |
| :--- | :---: | :---: | :--- | :--- |
| **NLU Classifier Misclassification** | NLU Classifier (Logistic Regression) | 15 / 36 (41.7%) | The classifier routed queries containing high-overlap keywords to incorrect intents. This completely filtered out the correct intent's chunk pool. | • Expand classifier training data with focused paraphrases.<br>• Inject disambiguation keywords to break spurious correlations. |
| **LLM Router Fallback Error** | LLM Router (Few-Shot Fallback) | 1 / 36 (2.8%) | Low-confidence classifier queries fell back to the LLM, but the LLM failed to match the correct intent. | • Add explicit few-shot routing examples in the LLM prompt. |
| **Reranking / Ranking Failure** | Reranker / Bi-Encoder | 20 / 36 (55.6%) | The router successfully predicted the correct intent, but because the reranker is disabled, the Bi-Encoder's raw similarity score ranked other chunks of the same intent higher, pushing the true chunk out of the top 3. | • Re-enable the Cross-Encoder reranker to sort the top matches.<br>• Merge highly redundant or duplicate chunks. |

---

## 📝 Query-by-Query Failure Directory (K = 3)

Below is the complete analysis of the 36 failed queries at $K = 3$, showing the expected versus predicted behavior, isolated component, and the diagnostic root cause.

```carousel
### Failure Case 1: "Can I correct a typo in my delivery destination?"
* **Expected Intent**: `modify_address`
* **True Chunk ID**: `billing_shipping_addresses_001`
* **Predicted Intent(s)**: `['check_shipping_policies', 'modify_order', 'track_package']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `track_package_004` (Bi-Encoder score: 0.6672)
  2. `hotel_delivery_002` (Bi-Encoder score: 0.6534)
  3. `change_your_order_information_001` (Bi-Encoder score: 0.6525)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 2: "Can I get a VAT invoice for my digital purchases?"
* **Expected Intent**: `view_invoice`
* **True Chunk ID**: `print_an_invoice_001`
* **Predicted Intent(s)**: `['check_tax_rates']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `vat_rates_002` (Bi-Encoder score: 0.7384)
  2. `vat_rates_001` (Bi-Encoder score: 0.6703)
  3. `about_us_state_sales_and_use_taxes_002` (Bi-Encoder score: 0.6095)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 3: "I want to rate my recent interaction with support."
* **Expected Intent**: `submit_feedback`
* **True Chunk ID**: `amazon_consumer_surveys_001`
* **Predicted Intent(s)**: `['submit_feedback', 'contact_support', 'check_promotional_balance']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `support_options_and_customer_service_002` (Bi-Encoder score: 0.5602)
  2. `support_options_and_customer_service_001` (Bi-Encoder score: 0.5348)
  3. `support_options_and_customer_service_003` (Bi-Encoder score: 0.5273)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 4: "How can I file a complaint about the delivery service?"
* **Expected Intent**: `submit_feedback`
* **True Chunk ID**: `amazon_consumer_surveys_001`
* **Predicted Intent(s)**: `['report_missing_package', 'check_shipping_policies', 'track_package']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `track_package_004` (Bi-Encoder score: 0.6259)
  2. `packaging_programs_002` (Bi-Encoder score: 0.6152)
  3. `missing_package_delivered_002` (Bi-Encoder score: 0.6049)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 5: "Where do I send suggestions for app improvement?"
* **Expected Intent**: `submit_feedback`
* **True Chunk ID**: `amazon_consumer_surveys_001`
* **Predicted Intent(s)**: `['submit_feedback', 'manage_notifications', 'manage_delivery_alerts']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `manage_shipment_text_updates_001` (Bi-Encoder score: 0.5736)
  2. `push_notifications_tracking_003` (Bi-Encoder score: 0.5712)
  3. `shipment_text_updates_terms_001` (Bi-Encoder score: 0.5409)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 6: "I want to edit my profile picture and personal info."
* **Expected Intent**: `manage_profile_settings`
* **True Chunk ID**: `add_a_shopping_profile_001`
* **Predicted Intent(s)**: `['modify_address', 'manage_profile_settings', 'reset_password']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `what_are_shopping_profiles_001` (Bi-Encoder score: 0.5358)
  2. `add_delete_and_manage_addresses_001` (Bi-Encoder score: 0.5317)
  3. `change_your_order_information_001` (Bi-Encoder score: 0.5299)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 7: "How do I delete a secondary profile from my account?"
* **Expected Intent**: `manage_profile_settings`
* **True Chunk ID**: `add_a_shopping_profile_001`
* **Predicted Intent(s)**: `['close_account', 'manage_profile_settings']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `request_the_closure_of_your_account_and_the_deletion_of_001` (Bi-Encoder score: 0.6419)
  2. `use_switch_accounts_001` (Bi-Encoder score: 0.6110)
  3. `what_are_shopping_profiles_001` (Bi-Encoder score: 0.5811)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 8: "I want to change the email address linked to my profile."
* **Expected Intent**: `manage_profile_settings`
* **True Chunk ID**: `what_are_mobile_phone_number_accounts_001`
* **Predicted Intent(s)**: `['modify_address', 'manage_notifications']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `change_your_subscription_email_preferences_001` (Bi-Encoder score: 0.5988)
  2. `add_delete_and_manage_addresses_001` (Bi-Encoder score: 0.5676)
  3. `manage_an_email_address_already_in_use_error_001` (Bi-Encoder score: 0.5658)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 9: "How do I configure my account region and country preferences?"
* **Expected Intent**: `manage_account_settings`
* **True Chunk ID**: `change_your_account_settings_001`
* **Predicted Intent(s)**: `['convert_currency', 'manage_notifications', 'manage_account_settings']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `about_currency_of_preference_on_international_shopping_001` (Bi-Encoder score: 0.6834)
  2. `change_your_language_preference_001` (Bi-Encoder score: 0.6560)
  3. `select_your_card_currency_for_amazon_currency_converter_001` (Bi-Encoder score: 0.6259)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 10: "Where do I change my primary account location?"
* **Expected Intent**: `manage_account_settings`
* **True Chunk ID**: `change_your_account_settings_001`
* **Predicted Intent(s)**: `['modify_address', 'manage_profile_settings', 'reset_password']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `use_switch_accounts_001` (Bi-Encoder score: 0.5886)
  2. `change_your_password_001` (Bi-Encoder score: 0.5685)
  3. `change_your_order_information_001` (Bi-Encoder score: 0.5584)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 11: "How to avoid conversion fees at checkout?"
* **Expected Intent**: `convert_currency`
* **True Chunk ID**: `select_your_card_currency_for_amazon_currency_converter_001`
* **Predicted Intent(s)**: `['convert_currency', 'check_restocking_fees', 'report_payment_scam']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `avoiding_payment_scams_001` (Bi-Encoder score: 0.6595)
  2. `amazon_currency_converter_exchange_rates_001` (Bi-Encoder score: 0.6566)
  3. `about_currency_of_preference_on_international_shopping_001` (Bi-Encoder score: 0.6290)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 12: "Why is my bank declining the charge from Amazon?"
* **Expected Intent**: `resolve_declined_payment`
* **True Chunk ID**: `resolve_a_declined_payment_001`
* **Predicted Intent(s)**: `['investigate_unknown_charge', 'resolve_declined_payment']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `unknown_amazon_payment_charges_004` (Bi-Encoder score: 0.7259)
  2. `unknown_amazon_payment_charges_001` (Bi-Encoder score: 0.7227)
  3. `unknown_amazon_payment_charges_005` (Bi-Encoder score: 0.7006)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 13: "How to update payment details on a pending transaction?"
* **Expected Intent**: `resolve_declined_payment`
* **True Chunk ID**: `resolve_a_declined_payment_001`
* **Predicted Intent(s)**: `['manage_wallet_cards']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `change_your_order_information_001` (Bi-Encoder score: 0.6487)
  2. `manage_payment_methods_001` (Bi-Encoder score: 0.6463)
  3. `change_your_default_payment_methods_001` (Bi-Encoder score: 0.6207)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 14: "How do I report fake billing scams on my account?"
* **Expected Intent**: `report_payment_scam`
* **True Chunk ID**: `identifying_a_scam_001`
* **Predicted Intent(s)**: `['report_payment_scam']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `report_a_scam_001` (Bi-Encoder score: 0.6882)
  2. `amz_sec_003` (Bi-Encoder score: 0.6793)
  3. `amz_sec_001` (Bi-Encoder score: 0.6562)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 15: "Are opened video games or software eligible for returns?"
* **Expected Intent**: `check_return_eligibility`
* **True Chunk ID**: `amz_ret_004`
* **Predicted Intent(s)**: `['check_restocking_fees']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `amz_fee_004` (Bi-Encoder score: 0.6932)
  2. `amz_fee_002` (Bi-Encoder score: 0.6037)
  3. `amz_fee_005` (Bi-Encoder score: 0.5951)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 16: "How do I check if my purchase can be returned?"
* **Expected Intent**: `check_return_eligibility`
* **True Chunk ID**: `amz_ret_006`
* **Predicted Intent(s)**: `['check_return_eligibility', 'check_restocking_fees']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `amz_ret_009` (Bi-Encoder score: 0.7171)
  2. `amz_ret_008` (Bi-Encoder score: 0.7116)
  3. `amz_ret_004` (Bi-Encoder score: 0.7097)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 17: "Can I return a used item for a full refund?"
* **Expected Intent**: `check_return_eligibility`
* **True Chunk ID**: `amz_seg_004`
* **Predicted Intent(s)**: `['check_restocking_fees', 'check_return_eligibility']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `amz_ret_009` (Bi-Encoder score: 0.7320)
  2. `amz_fee_002` (Bi-Encoder score: 0.7211)
  3. `amz_fee_004` (Bi-Encoder score: 0.7196)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 18: "How to know if a seller product is eligible for returns?"
* **Expected Intent**: `check_return_eligibility`
* **True Chunk ID**: `amz_seg_004`
* **Predicted Intent(s)**: `['check_return_eligibility', 'check_international_returns', 'check_restocking_fees']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `amz_ret_001` (Bi-Encoder score: 0.7200)
  2. `amz_ret_008` (Bi-Encoder score: 0.7106)
  3. `amz_ret_011` (Bi-Encoder score: 0.6996)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 19: "How much is deducted from my refund for damaged returns?"
* **Expected Intent**: `check_restocking_fees`
* **True Chunk ID**: `amz_fee_005`
* **Predicted Intent(s)**: `['check_restocking_fees']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `amz_fee_004` (Bi-Encoder score: 0.7181)
  2. `amz_fee_002` (Bi-Encoder score: 0.7140)
  3. `amz_fee_001` (Bi-Encoder score: 0.7074)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 20: "How long do international return refunds take?"
* **Expected Intent**: `check_international_returns`
* **True Chunk ID**: `amz_int_003`
* **Predicted Intent(s)**: `['check_international_returns']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `amz_int_005` (Bi-Encoder score: 0.6388)
  2. `amz_int_007` (Bi-Encoder score: 0.6358)
  3. `amz_int_006` (Bi-Encoder score: 0.6209)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 21: "Where do I edit my delivery alert preferences?"
* **Expected Intent**: `manage_delivery_alerts`
* **True Chunk ID**: `turn_off_text_updates_001`
* **Predicted Intent(s)**: `['manage_notifications', 'modify_order', 'modify_address']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `change_your_subscription_email_preferences_001` (Bi-Encoder score: 0.6937)
  2. `change_your_order_information_001` (Bi-Encoder score: 0.6713)
  3. `amz_ord_001` (Bi-Encoder score: 0.6526)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 22: "My tracking says late delivery, where is my order?"
* **Expected Intent**: `check_delivery_delay`
* **True Chunk ID**: `late_delivery_007`
* **Predicted Intent(s)**: `['check_delivery_delay']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `missing_tracking_information_003` (Bi-Encoder score: 0.6976)
  2. `missing_tracking_information_002` (Bi-Encoder score: 0.6951)
  3. `missing_tracking_information_004` (Bi-Encoder score: 0.6946)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 23: "My tracking is stuck in transit, how to report delay?"
* **Expected Intent**: `check_delivery_delay`
* **True Chunk ID**: `missing_tracking_information_003`
* **Predicted Intent(s)**: `['check_delivery_delay', 'track_package']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `track_package_004` (Bi-Encoder score: 0.7124)
  2. `map_tracking_001` (Bi-Encoder score: 0.6522)
  3. `missing_tracking_information_005` (Bi-Encoder score: 0.6394)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 24: "What should I do if my shipping address was incorrect?"
* **Expected Intent**: `resolve_undeliverable_package`
* **True Chunk ID**: `undeliverable_package_002`
* **Predicted Intent(s)**: `['modify_address', 'report_missing_item', 'modify_order']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `missing_item_from_order_002` (Bi-Encoder score: 0.6992)
  2. `billing_shipping_addresses_001` (Bi-Encoder score: 0.6876)
  3. `missing_item_from_order_006` (Bi-Encoder score: 0.6812)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 25: "My shipment failed delivery because the business was closed."
* **Expected Intent**: `resolve_undeliverable_package`
* **True Chunk ID**: `undeliverable_package_001`
* **Predicted Intent(s)**: `['resolve_declined_payment', 'check_delivery_delay', 'report_missing_item']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `missing_item_from_order_006` (Bi-Encoder score: 0.5470)
  2. `late_delivery_007` (Bi-Encoder score: 0.5422)
  3. `missing_item_from_order_005` (Bi-Encoder score: 0.5363)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 26: "Do I need to be home to receive a high-value package?"
* **Expected Intent**: `check_delivery_rules`
* **True Chunk ID**: `secure_delivery_otp_001`
* **Predicted Intent(s)**: `['report_missing_package', 'check_shipping_policies', 'report_missing_item']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `sign_for_order_001` (Bi-Encoder score: 0.5959)
  2. `missing_package_delivered_002` (Bi-Encoder score: 0.5639)
  3. `hotel_delivery_004` (Bi-Encoder score: 0.5562)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 27: "How do I set delivery instructions for my driver?"
* **Expected Intent**: `check_delivery_rules`
* **True Chunk ID**: `secure_delivery_otp_001`
* **Predicted Intent(s)**: `['track_package', 'check_delivery_rules', 'modify_address']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `map_tracking_001` (Bi-Encoder score: 0.6106)
  2. `change_your_order_information_001` (Bi-Encoder score: 0.5983)
  3. `delivery_windows_001` (Bi-Encoder score: 0.5964)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 28: "Can I request that my package be left inside the garage?"
* **Expected Intent**: `check_delivery_rules`
* **True Chunk ID**: `secure_delivery_otp_001`
* **Predicted Intent(s)**: `['report_missing_package', 'check_shipping_policies', 'report_missing_item']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `missing_package_delivered_002` (Bi-Encoder score: 0.6257)
  2. `missing_item_from_order_006` (Bi-Encoder score: 0.5745)
  3. `hotel_delivery_002` (Bi-Encoder score: 0.5707)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 29: "What are the rules for apartment building deliveries?"
* **Expected Intent**: `check_delivery_rules`
* **True Chunk ID**: `shipping_prisons_001`
* **Predicted Intent(s)**: `['check_shipping_policies', 'check_delivery_rules']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `hotel_delivery_001` (Bi-Encoder score: 0.6322)
  2. `hotel_delivery_002` (Bi-Encoder score: 0.6182)
  3. `hotel_delivery_003` (Bi-Encoder score: 0.5794)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 30: "How do I manage my delivery preferences for my household?"
* **Expected Intent**: `check_delivery_rules`
* **True Chunk ID**: `secure_delivery_otp_001`
* **Predicted Intent(s)**: `['manage_delivery_alerts']` *(Routing: Fail | Fallback: True)*
* **Top Retrieved Chunks**:
  1. `manage_shipment_text_updates_001` (Bi-Encoder score: 0.5795)
  2. `turn_off_text_updates_001` (Bi-Encoder score: 0.5561)
  3. `shipment_text_updates_terms_001` (Bi-Encoder score: 0.5106)
* **Isolated Component**: LLM Router (Fallback)
* **Root Cause**: The query fell back to the LLM due to low classifier confidence. The LLM failed to route to the correct intent.
<!-- slide -->
### Failure Case 31: "How do I cancel subscriptions for a deceased customer?"
* **Expected Intent**: `request_bereavement_support`
* **True Chunk ID**: `bereavement_support_001`
* **Predicted Intent(s)**: `['request_bereavement_support', 'modify_order', 'manage_notifications']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `amz_can_001` (Bi-Encoder score: 0.5919)
  2. `cancel_items_and_orders_001` (Bi-Encoder score: 0.5914)
  3. `amz_can_002` (Bi-Encoder score: 0.5895)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 32: "Who do I contact about a missing or stolen shipment?"
* **Expected Intent**: `report_missing_package`
* **True Chunk ID**: `missing_package_delivered_002`
* **Predicted Intent(s)**: `['report_missing_package', 'report_missing_item']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `missing_item_from_order_003` (Bi-Encoder score: 0.7163)
  2. `missing_item_from_order_002` (Bi-Encoder score: 0.7072)
  3. `missing_item_from_order_006` (Bi-Encoder score: 0.7065)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 33: "What to do if an item is missing from my package?"
* **Expected Intent**: `report_missing_item`
* **True Chunk ID**: `missing_item_from_order_001`
* **Predicted Intent(s)**: `['report_missing_item']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `missing_item_from_order_004` (Bi-Encoder score: 0.8226)
  2. `missing_item_from_order_006` (Bi-Encoder score: 0.8173)
  3. `missing_item_from_order_002` (Bi-Encoder score: 0.8109)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but without the reranker, the Bi-Encoder's raw cosine similarity score was not selective enough, ranking other chunks higher.
<!-- slide -->
### Failure Case 34: "How are tax rates determined for international shipping?"
* **Expected Intent**: `check_tax_rates`
* **True Chunk ID**: `vat_rates_001`
* **Predicted Intent(s)**: `['check_international_returns']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `amz_int_005` (Bi-Encoder score: 0.6141)
  2. `amz_int_003` (Bi-Encoder score: 0.5831)
  3. `amz_int_007` (Bi-Encoder score: 0.5822)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 35: "Where do I see the tax breakdown of my invoice?"
* **Expected Intent**: `check_tax_rates`
* **True Chunk ID**: `about_us_state_sales_and_use_taxes_002`
* **Predicted Intent(s)**: `['view_invoice']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `print_an_invoice_001` (Bi-Encoder score: 0.6499)
  2. `archived_orders_001` (Bi-Encoder score: 0.4907)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 36: "How to turn off marketing push notifications in the app?"
* **Expected Intent**: `manage_notifications`
* **True Chunk ID**: `change_your_subscription_email_preferences_001`
* **Predicted Intent(s)**: `['manage_account_settings', 'manage_delivery_alerts']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `unsubscribe_from_amazon_marketing_001` (Bi-Encoder score: 0.6489)
  2. `turn_off_text_updates_001` (Bi-Encoder score: 0.5843)
  3. `push_notifications_tracking_003` (Bi-Encoder score: 0.5786)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
```
