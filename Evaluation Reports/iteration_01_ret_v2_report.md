# 📊 RAG Evaluation & Failure Analysis Report (Optimized Hybrid Router)

This report summarizes the performance evaluation of the hybrid RAG system across $K = 1, 3, 5, 7$ and provides a detailed failure mode analysis of the system at $K = 3$ after implementing **Cumulative Probability Mass Routing (Soft-N)** and **Classifier-Guided LLM Fallback**.

---

## 📈 E-to-E Retrieval Performance Overview

The evaluation was performed over the full **340 query dataset** using our optimized cascading hybrid router (`margin <= 0.35` and `top1_prob < 0.13`), BGE vector search embeddings, MS-MARCO Cross-Encoder reranking, and relative score-margin dynamic K selection.

A query is considered a **Hit** if the ground truth chunk is retrieved within the top $K$ results.

| K Value | Hit Rate (Recall@K) | MRR (Mean Reciprocal Rank) | Failed Queries |
| :---: | :---: | :---: | :---: |
| **K = 1** | 84.41% | 0.7608 | 53 / 340 |
| **K = 3** | **90.59%** | **0.7796** | **32 / 340** |
| **K = 5** | 92.35% | 0.7836 | 26 / 340 |
| **K = 7** | 93.82% | 0.7857 | 21 / 340 |

---

## 🔍 Failure Mode Table (K = 3)

The 32 failed queries at $K=3$ have been classified into distinct failure modes. 

| Failure Mode | Isolated Component | Impact (Count/%) | Root Cause Analysis | Mitigation Action |
| :--- | :---: | :---: | :--- | :--- |
| **NLU Classifier Misclassification** | NLU Classifier (Logistic Regression) | 15 / 32 (46.9%) | The intent classifier misrouted queries containing high-overlap keywords to incorrect domains. Because these had high confidence, fallback was not triggered, and the true intent was filtered out. | • Expand classifier training data with focused paraphrases.<br>• Inject disambiguation keywords to break spurious correlations. |
| **LLM Router Fallback Error** | LLM Router (Few-Shot Fallback) | 1 / 32 (3.1%) | Low-confidence classifier queries fell back to the LLM, but the LLM failed to match the correct intent. | • Add explicit few-shot routing examples in the LLM prompt. |
| **Reranking / Ranking Failure** | Reranker (Cross-Encoder) | 16 / 32 (50.0%) | The router successfully predicted the correct intent, but the Cross-Encoder rerank scored other related chunks slightly higher, pushing the true chunk to Rank 4 or lower. | • Merge highly redundant or duplicate chunks.<br>• Enrich chunk metadata with context-aware question tags (sample queries). |

---

## 📝 Query-by-Query Failure Directory (K = 3)

Below is the complete analysis of the 32 failed queries at $K = 3$, showing the expected versus predicted behavior, isolated component, and the diagnostic root cause.

```carousel
### Failure Case 1: "Can I make edits to a shipment before it goes out?"
* **Expected Intent**: `modify_order`
* **True Chunk ID**: `amz_ord_001`
* **Predicted Intent(s)**: `['modify_order', 'manage_delivery_alerts']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `amz_can_001` (Rerank score: 1.33)
  2. `push_notifications_tracking_003` (Rerank score: -2.03)
  3. `turn_off_text_updates_001` (Rerank score: -3.10)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 2: "Is it too late to edit my purchase?"
* **Expected Intent**: `modify_order`
* **True Chunk ID**: `amz_ord_001`
* **Predicted Intent(s)**: `['modify_order', 'check_delivery_delay', 'check_return_eligibility']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `late_delivery_007` (Rerank score: -4.03)
  2. `amz_can_001` (Rerank score: -5.89)
  3. `cancel_items_and_orders_001` (Rerank score: -7.21)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 3: "Can I correct a typo in my delivery destination?"
* **Expected Intent**: `modify_address`
* **True Chunk ID**: `billing_shipping_addresses_001`
* **Predicted Intent(s)**: `['check_shipping_policies', 'modify_order', 'track_package']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `track_package_004` (Rerank score: -6.23)
  2. `hotel_delivery_003` (Rerank score: -6.56)
  3. `map_tracking_001` (Rerank score: -6.74)
  4. `track_package_003` (Rerank score: -7.21)
  5. `change_your_order_information_001` (Rerank score: -7.40)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 4: "Can I get a VAT invoice for my digital purchases?"
* **Expected Intent**: `view_invoice`
* **True Chunk ID**: `print_an_invoice_001`
* **Predicted Intent(s)**: `['check_tax_rates']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `vat_rates_002` (Rerank score: -10.20)
  2. `about_us_state_sales_and_use_taxes_002` (Rerank score: -10.61)
  3. `vat_rates_001` (Rerank score: -10.78)
  4. `about_us_state_sales_and_use_taxes_001` (Rerank score: -11.47)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 5: "How do I submit feedback about my shopping experience?"
* **Expected Intent**: `submit_feedback`
* **True Chunk ID**: `amazon_consumer_surveys_001`
* **Predicted Intent(s)**: `['submit_feedback', 'track_refund', 'manage_profile_settings']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `add_a_shopping_profile_001` (Rerank score: -2.44)
  2. `what_are_shopping_profiles_001` (Rerank score: -3.31)
  3. `sign_out_of_your_amazon_account_in_the_amazon_shopping_001` (Rerank score: -9.58)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 6: "How can I file a complaint about the delivery service?"
* **Expected Intent**: `submit_feedback`
* **True Chunk ID**: `amazon_consumer_surveys_001`
* **Predicted Intent(s)**: `['report_missing_package', 'check_shipping_policies', 'track_package']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `track_package_004` (Rerank score: -4.43)
  2. `missing_package_delivered_002` (Rerank score: -4.59)
  3. `hotel_delivery_004` (Rerank score: -4.99)
  4. `hotel_delivery_003` (Rerank score: -5.74)
  5. `third_party_company_delivery_001` (Rerank score: -6.04)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 7: "Can I change the payment method my teen uses?"
* **Expected Intent**: `manage_teen_account`
* **True Chunk ID**: `set_order_approvals_for_a_teen_login_001`
* **Predicted Intent(s)**: `['manage_teen_account', 'manage_wallet_cards']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `what_is_a_teen_login_001` (Rerank score: 1.77)
  2. `change_your_default_payment_methods_001` (Rerank score: 0.43)
  3. `removing_a_teen_login_from_an_amazon_household_001` (Rerank score: -0.14)
  4. `manage_your_backup_payment_methods_001` (Rerank score: -1.13)
  5. `manage_payment_methods_001` (Rerank score: -1.86)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 8: "I want to change the email address linked to my profile."
* **Expected Intent**: `manage_profile_settings`
* **True Chunk ID**: `what_are_mobile_phone_number_accounts_001`
* **Predicted Intent(s)**: `['modify_address', 'manage_notifications']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `add_delete_and_manage_addresses_001` (Rerank score: -3.76)
  2. `manage_an_email_address_already_in_use_error_001` (Rerank score: -4.37)
  3. `change_your_subscription_email_preferences_001` (Rerank score: -5.11)
  4. `change_your_order_information_001` (Rerank score: -5.74)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 9: "Where do I change my primary account location?"
* **Expected Intent**: `manage_account_settings`
* **True Chunk ID**: `change_your_account_settings_001`
* **Predicted Intent(s)**: `['modify_address', 'manage_profile_settings', 'reset_password']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `add_delete_and_manage_addresses_001` (Rerank score: -6.67)
  2. `change_your_order_information_001` (Rerank score: -7.98)
  3. `why_cant_i_sign_into_my_account_001` (Rerank score: -9.28)
  4. `change_your_password_001` (Rerank score: -9.32)
  5. `what_are_mobile_phone_number_accounts_001` (Rerank score: -9.40)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 10: "My transaction failed, how do I update the payment method?"
* **Expected Intent**: `resolve_declined_payment`
* **True Chunk ID**: `resolve_a_declined_payment_001`
* **Predicted Intent(s)**: `['resolve_declined_payment', 'manage_wallet_cards']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `manage_your_backup_payment_methods_001` (Rerank score: 5.60)
  2. `change_your_default_payment_methods_001` (Rerank score: 4.95)
  3. `manage_payment_methods_001` (Rerank score: 3.55)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 11: "How to update payment details on a pending transaction?"
* **Expected Intent**: `resolve_declined_payment`
* **True Chunk ID**: `resolve_a_declined_payment_001`
* **Predicted Intent(s)**: `['manage_wallet_cards']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `manage_payment_methods_001` (Rerank score: 2.48)
  2. `change_your_order_information_001` (Rerank score: 0.20)
  3. `change_your_default_payment_methods_001` (Rerank score: 0.09)
  4. `manage_your_backup_payment_methods_001` (Rerank score: -0.88)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 12: "I received a demand for payment via gift cards."
* **Expected Intent**: `report_payment_scam`
* **True Chunk ID**: `amz_sec_004`
* **Predicted Intent(s)**: `['report_payment_scam', 'manage_wallet_cards', 'check_shipping_policies']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `avoiding_payment_scams_001` (Rerank score: -2.55)
  2. `scam_trends_007` (Rerank score: -3.30)
  3. `scam_trends_002` (Rerank score: -3.55)
  4. `check_your_gift_card_balance_001` (Rerank score: -5.30)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 13: "Are opened video games or software eligible for returns?"
* **Expected Intent**: `check_return_eligibility`
* **True Chunk ID**: `amz_ret_004`
* **Predicted Intent(s)**: `['check_restocking_fees']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `amz_fee_004` (Rerank score: 0.77)
  2. `amz_fee_005` (Rerank score: -10.47)
  3. `amz_fee_001` (Rerank score: -10.52)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 14: "How do I check if my purchase can be returned?"
* **Expected Intent**: `check_return_eligibility`
* **True Chunk ID**: `amz_ret_006`
* **Predicted Intent(s)**: `['check_return_eligibility', 'check_restocking_fees']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `amz_ret_001` (Rerank score: 2.14)
  2. `amz_ret_012` (Rerank score: -0.95)
  3. `amz_ret_008` (Rerank score: -1.45)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 15: "What are the rules for returning items from outside the US?"
* **Expected Intent**: `check_international_returns`
* **True Chunk ID**: `amz_int_004`
* **Predicted Intent(s)**: `['check_international_returns', 'check_return_eligibility']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `amz_ret_012` (Rerank score: 3.38)
  2. `amz_ret_011` (Rerank score: 1.31)
  3. `amz_seg_004` (Rerank score: 0.02)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 16: "How do I return a package from another country?"
* **Expected Intent**: `check_international_returns`
* **True Chunk ID**: `amz_int_001`
* **Predicted Intent(s)**: `['check_international_returns', 'resolve_undeliverable_package']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `undeliverable_package_002` (Rerank score: 1.08)
  2. `amz_int_003` (Rerank score: -0.38)
  3. `undeliverable_package_003` (Rerank score: -1.55)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 17: "Where do I edit my delivery alert preferences?"
* **Expected Intent**: `manage_delivery_alerts`
* **True Chunk ID**: `turn_off_text_updates_001`
* **Predicted Intent(s)**: `['manage_notifications', 'modify_order', 'modify_address']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `add_delete_and_manage_addresses_001` (Rerank score: 1.77)
  2. `billing_shipping_addresses_002` (Rerank score: -1.86)
  3. `change_your_subscription_email_preferences_001` (Rerank score: -5.19)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 18: "My tracking is stuck in transit, how to report delay?"
* **Expected Intent**: `check_delivery_delay`
* **True Chunk ID**: `missing_tracking_information_003`
* **Predicted Intent(s)**: `['check_delivery_delay', 'track_package']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `late_delivery_007` (Rerank score: -3.75)
  2. `missing_tracking_information_005` (Rerank score: -4.81)
  3. `map_tracking_001` (Rerank score: -8.95)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 19: "What should I do if my shipping address was incorrect?"
* **Expected Intent**: `resolve_undeliverable_package`
* **True Chunk ID**: `undeliverable_package_002`
* **Predicted Intent(s)**: `['modify_address', 'report_missing_item', 'modify_order']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `billing_shipping_addresses_001` (Rerank score: 5.68)
  2. `add_delete_and_manage_addresses_001` (Rerank score: 2.13)
  3. `missing_item_from_order_002` (Rerank score: 0.20)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 20: "My shipment failed delivery because the business was closed."
* **Expected Intent**: `resolve_undeliverable_package`
* **True Chunk ID**: `undeliverable_package_001`
* **Predicted Intent(s)**: `['resolve_declined_payment', 'check_delivery_delay', 'report_missing_item']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `late_delivery_007` (Rerank score: -3.24)
  2. `missing_item_from_order_006` (Rerank score: -4.19)
  3. `missing_item_from_order_005` (Rerank score: -4.82)
  4. `missing_item_from_order_002` (Rerank score: -5.33)
  5. `missing_tracking_information_005` (Rerank score: -5.62)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 21: "Do I need to be home to receive a high-value package?"
* **Expected Intent**: `check_delivery_rules`
* **True Chunk ID**: `secure_delivery_otp_001`
* **Predicted Intent(s)**: `['report_missing_package', 'check_shipping_policies', 'report_missing_item']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `hotel_delivery_003` (Rerank score: -7.36)
  2. `missing_item_from_order_006` (Rerank score: -7.61)
  3. `hotel_delivery_004` (Rerank score: -8.45)
  4. `hotel_delivery_002` (Rerank score: -9.47)
  5. `missing_package_delivered_002` (Rerank score: -10.18)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 22: "Can I request that my package be left inside the garage?"
* **Expected Intent**: `check_delivery_rules`
* **True Chunk ID**: `secure_delivery_otp_001`
* **Predicted Intent(s)**: `['report_missing_package', 'check_shipping_policies', 'report_missing_item']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `missing_package_delivered_002` (Rerank score: -7.75)
  2. `missing_item_from_order_006` (Rerank score: -8.46)
  3. `hotel_delivery_004` (Rerank score: -8.54)
  4. `hotel_delivery_003` (Rerank score: -8.59)
  5. `third_party_company_delivery_001` (Rerank score: -9.02)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 23: "How do I manage my delivery preferences for my household?"
* **Expected Intent**: `check_delivery_rules`
* **True Chunk ID**: `secure_delivery_otp_001`
* **Predicted Intent(s)**: `['manage_delivery_alerts']` *(Routing: Fail | Fallback: True)*
* **Top Retrieved Chunks**:
  1. `manage_shipment_text_updates_001` (Rerank score: -4.41)
  2. `push_notifications_tracking_003` (Rerank score: -7.91)
  3. `turn_off_text_updates_001` (Rerank score: -8.91)
* **Isolated Component**: LLM Router (Fallback)
* **Root Cause**: The query fell back to the LLM due to low classifier confidence. The LLM failed to route to the correct intent.
<!-- slide -->
### Failure Case 24: "Where can I speak with a live agent about my account?"
* **Expected Intent**: `contact_support`
* **True Chunk ID**: `support_options_and_customer_service_002`
* **Predicted Intent(s)**: `['contact_support', 'close_account', 'report_payment_scam']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `request_the_closure_of_your_account_and_the_deletion_of_001` (Rerank score: -9.58)
  2. `support_options_and_customer_service_004` (Rerank score: -9.61)
  3. `what_happens_when_i_close_my_account_003` (Rerank score: -9.92)
  4. `identifying_a_scam_001` (Rerank score: -10.23)
  5. `scam_trends_005` (Rerank score: -10.44)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 25: "What should I do if my parcel was stolen?"
* **Expected Intent**: `report_missing_package`
* **True Chunk ID**: `missing_package_delivered_002`
* **Predicted Intent(s)**: `['report_missing_package', 'report_missing_item', 'check_delivery_delay']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `missing_item_from_order_003` (Rerank score: 1.27)
  2. `missing_item_from_order_002` (Rerank score: 1.25)
  3. `missing_item_from_order_005` (Rerank score: -1.61)
  4. `missing_item_from_order_001` (Rerank score: -1.71)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 26: "Who do I contact about a missing or stolen shipment?"
* **Expected Intent**: `report_missing_package`
* **True Chunk ID**: `missing_package_delivered_002`
* **Predicted Intent(s)**: `['report_missing_package', 'report_missing_item']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `missing_item_from_order_003` (Rerank score: 6.39)
  2. `missing_item_from_order_002` (Rerank score: 2.69)
  3. `missing_item_from_order_005` (Rerank score: 0.91)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 27: "My delivery was short one item, how to get a replacement?"
* **Expected Intent**: `report_missing_item`
* **True Chunk ID**: `missing_item_from_order_006`
* **Predicted Intent(s)**: `['report_missing_item', 'check_delivery_delay', 'report_missing_package']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `missing_packing_slip_001` (Rerank score: -4.98)
  2. `missing_item_from_order_002` (Rerank score: -6.12)
  3. `missing_item_from_order_004` (Rerank score: -6.28)
  4. `missing_tracking_information_002` (Rerank score: -7.90)
  5. `missing_package_delivered_002` (Rerank score: -8.01)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 28: "How do I report phishing attempts on my account?"
* **Expected Intent**: `identify_phishing_scams`
* **True Chunk ID**: `report_suspicious_activity_001`
* **Predicted Intent(s)**: `['identify_phishing_scams', 'report_payment_scam']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `report_a_scam_001` (Rerank score: 5.22)
  2. `amz_sec_001` (Rerank score: 3.24)
  3. `avoiding_payment_scams_001` (Rerank score: -0.41)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
<!-- slide -->
### Failure Case 29: "How are tax rates determined for international shipping?"
* **Expected Intent**: `check_tax_rates`
* **True Chunk ID**: `vat_rates_001`
* **Predicted Intent(s)**: `['check_international_returns']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `amz_int_003` (Rerank score: -9.60)
  2. `amz_int_004` (Rerank score: -10.81)
  3. `amz_int_005` (Rerank score: -11.21)
  4. `amz_int_001` (Rerank score: -11.27)
  5. `amz_int_007` (Rerank score: -11.32)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 30: "Where do I see the tax breakdown of my invoice?"
* **Expected Intent**: `check_tax_rates`
* **True Chunk ID**: `about_us_state_sales_and_use_taxes_002`
* **Predicted Intent(s)**: `['view_invoice']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `print_an_invoice_001` (Rerank score: -9.94)
  2. `archived_orders_001` (Rerank score: -11.39)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 31: "How to turn off marketing push notifications in the app?"
* **Expected Intent**: `manage_notifications`
* **True Chunk ID**: `change_your_subscription_email_preferences_001`
* **Predicted Intent(s)**: `['manage_account_settings', 'manage_delivery_alerts']` *(Routing: Fail | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `push_notifications_tracking_003` (Rerank score: 3.93)
  2. `turn_off_text_updates_001` (Rerank score: -2.59)
  3. `unsubscribe_from_amazon_marketing_001` (Rerank score: -6.03)
* **Isolated Component**: NLU Classifier
* **Root Cause**: The classifier predicted wrong intents with high confidence, preventing fallback.
<!-- slide -->
### Failure Case 32: "Where is the notification center settings page?"
* **Expected Intent**: `manage_notifications`
* **True Chunk ID**: `change_your_subscription_email_preferences_001`
* **Predicted Intent(s)**: `['manage_notifications', 'manage_delivery_alerts', 'manage_account_settings']` *(Routing: Correct | Fallback: False)*
* **Top Retrieved Chunks**:
  1. `push_notifications_tracking_003` (Rerank score: -4.82)
  2. `availability_alerts_001` (Rerank score: -8.93)
  3. `unsubscribe_from_amazon_marketing_001` (Rerank score: -10.62)
* **Isolated Component**: Reranker / Ranking
* **Root Cause**: The router successfully predicted the correct intent, but the target chunk fell outside the dynamic window because other related chunks scored higher.
```
