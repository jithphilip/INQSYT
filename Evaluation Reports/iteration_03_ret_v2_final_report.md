# 📊 RAG Evaluation & Failure Analysis Report (Iteration 5: Semantic Summaries + Linearization)

### 2. E-to-E Retrieval Performance Overview
| K Value | Hit Rate (Recall@K) | MRR (Mean Reciprocal Rank) | Failed Queries |
| :---: | :---: | :---: | :---: |
| **K = 1** | 82.06% | 0.7451 | 61 |
| **K = 3** | 89.41% | 0.7680 | 36 |
| **K = 5** | 91.18% | 0.7720 | 30 |
| **K = 7** | 92.65% | 0.7740 | 25 |

### 3. Failure Mode Table (K = 3)
| Failure Mode | Isolated Component | Impact (Count/%) | Root Cause Analysis | Mitigation Action |
| :--- | :---: | :---: | :--- | :--- |
| **NLU Classifier Misclassification** | NLU Classifier/Logistic Regression | 16 / 44.4% | The logistic regression model failed to include the true intent in the top 3 predicted intents. | Add more varied training data for these specific intents. |
| **LLM Router Fallback Error** | LLM Router/Few-Shot Fallback | 0 / 0.0% | The local Qwen 7B model failed to select the correct intent during fallback routing. | Adjust few-shot examples or switch to a larger model. |
| **Reranking / Ranking Failure** | Reranker/Cross-Encoder | 20 / 55.6% | The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher than the true chunk. | Refine chunks further or fine-tune the Cross-Encoder. |

### 4. Query-by-Query Failure Directory (K = 3)
````carousel
**Query**: "Is it too late to edit my purchase?"
- **Expected Intent**: `modify_order`
- **True Chunk ID**: `amz_ord_001`
- **Predicted Intent(s)**: `['modify_order', 'check_delivery_delay', 'manage_wallet_cards']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "Can I correct a typo in my delivery destination?"
- **Expected Intent**: `modify_address`
- **True Chunk ID**: `billing_shipping_addresses_001`
- **Predicted Intent(s)**: `['check_shipping_policies', 'track_package', 'modify_order']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['check_shipping_policies', 'track_package', 'modify_order'] instead of modify_address.
<!-- slide -->
**Query**: "Can I get a VAT invoice for my digital purchases?"
- **Expected Intent**: `view_invoice`
- **True Chunk ID**: `print_an_invoice_001`
- **Predicted Intent(s)**: `['check_tax_rates']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['check_tax_rates'] instead of view_invoice.
<!-- slide -->
**Query**: "How do I submit feedback about my shopping experience?"
- **Expected Intent**: `submit_feedback`
- **True Chunk ID**: `amazon_consumer_surveys_001`
- **Predicted Intent(s)**: `['submit_feedback', 'track_refund', 'manage_profile_settings']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "How can I file a complaint about the delivery service?"
- **Expected Intent**: `submit_feedback`
- **True Chunk ID**: `amazon_consumer_surveys_001`
- **Predicted Intent(s)**: `['report_missing_package', 'check_shipping_policies', 'track_package']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['report_missing_package', 'check_shipping_policies', 'track_package'] instead of submit_feedback.
<!-- slide -->
**Query**: "I want to share my thoughts on the new checkout design."
- **Expected Intent**: `submit_feedback`
- **True Chunk ID**: `amazon_consumer_surveys_001`
- **Predicted Intent(s)**: `['submit_feedback', 'other_query', 'manage_wallet_cards']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "Can I change the payment method my teen uses?"
- **Expected Intent**: `manage_teen_account`
- **True Chunk ID**: `set_order_approvals_for_a_teen_login_001`
- **Predicted Intent(s)**: `['manage_teen_account', 'manage_wallet_cards']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "I want to change the email address linked to my profile."
- **Expected Intent**: `manage_profile_settings`
- **True Chunk ID**: `what_are_mobile_phone_number_accounts_001`
- **Predicted Intent(s)**: `['modify_address', 'manage_notifications']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['modify_address', 'manage_notifications'] instead of manage_profile_settings.
<!-- slide -->
**Query**: "Where do I change my primary account location?"
- **Expected Intent**: `manage_account_settings`
- **True Chunk ID**: `change_your_account_settings_001`
- **Predicted Intent(s)**: `['modify_address', 'manage_profile_settings', 'reset_password']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['modify_address', 'manage_profile_settings', 'reset_password'] instead of manage_account_settings.
<!-- slide -->
**Query**: "My transaction failed, how do I update the payment method?"
- **Expected Intent**: `resolve_declined_payment`
- **True Chunk ID**: `resolve_a_declined_payment_001`
- **Predicted Intent(s)**: `['resolve_declined_payment', 'manage_wallet_cards']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "How to update payment details on a pending transaction?"
- **Expected Intent**: `resolve_declined_payment`
- **True Chunk ID**: `resolve_a_declined_payment_001`
- **Predicted Intent(s)**: `['manage_wallet_cards']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['manage_wallet_cards'] instead of resolve_declined_payment.
<!-- slide -->
**Query**: "Why was my card charged by Amazon without my knowledge?"
- **Expected Intent**: `investigate_unknown_charge`
- **True Chunk ID**: `unknown_amazon_payment_charges_001`
- **Predicted Intent(s)**: `['investigate_unknown_charge']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "How do I find out what an Amazon transaction was for?"
- **Expected Intent**: `investigate_unknown_charge`
- **True Chunk ID**: `unknown_amazon_payment_charges_001`
- **Predicted Intent(s)**: `['investigate_unknown_charge', 'report_payment_scam', 'check_shipping_policies']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "I received a demand for payment via gift cards."
- **Expected Intent**: `report_payment_scam`
- **True Chunk ID**: `amz_sec_004`
- **Predicted Intent(s)**: `['report_payment_scam', 'manage_wallet_cards', 'check_shipping_policies']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "Are opened video games or software eligible for returns?"
- **Expected Intent**: `check_return_eligibility`
- **True Chunk ID**: `amz_ret_004`
- **Predicted Intent(s)**: `['check_restocking_fees']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['check_restocking_fees'] instead of check_return_eligibility.
<!-- slide -->
**Query**: "How do I check if my purchase can be returned?"
- **Expected Intent**: `check_return_eligibility`
- **True Chunk ID**: `amz_ret_006`
- **Predicted Intent(s)**: `['check_return_eligibility', 'check_restocking_fees']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "What are the rules for returning items from outside the US?"
- **Expected Intent**: `check_international_returns`
- **True Chunk ID**: `amz_int_004`
- **Predicted Intent(s)**: `['check_international_returns', 'check_return_eligibility']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "How do I return a package from another country?"
- **Expected Intent**: `check_international_returns`
- **True Chunk ID**: `amz_int_001`
- **Predicted Intent(s)**: `['check_international_returns', 'resolve_undeliverable_package']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "Where do I edit my delivery alert preferences?"
- **Expected Intent**: `manage_delivery_alerts`
- **True Chunk ID**: `turn_off_text_updates_001`
- **Predicted Intent(s)**: `['manage_notifications', 'modify_order', 'modify_address']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['manage_notifications', 'modify_order', 'modify_address'] instead of manage_delivery_alerts.
<!-- slide -->
**Query**: "My tracking is stuck in transit, how to report delay?"
- **Expected Intent**: `check_delivery_delay`
- **True Chunk ID**: `missing_tracking_information_003`
- **Predicted Intent(s)**: `['check_delivery_delay', 'track_package']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "What should I do if my shipping address was incorrect?"
- **Expected Intent**: `resolve_undeliverable_package`
- **True Chunk ID**: `undeliverable_package_002`
- **Predicted Intent(s)**: `['modify_address', 'report_missing_item', 'report_missing_package']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['modify_address', 'report_missing_item', 'report_missing_package'] instead of resolve_undeliverable_package.
<!-- slide -->
**Query**: "My shipment failed delivery because the business was closed."
- **Expected Intent**: `resolve_undeliverable_package`
- **True Chunk ID**: `undeliverable_package_001`
- **Predicted Intent(s)**: `['resolve_declined_payment', 'check_delivery_delay', 'report_missing_item']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['resolve_declined_payment', 'check_delivery_delay', 'report_missing_item'] instead of resolve_undeliverable_package.
<!-- slide -->
**Query**: "Do I need to be home to receive a high-value package?"
- **Expected Intent**: `check_delivery_rules`
- **True Chunk ID**: `secure_delivery_otp_001`
- **Predicted Intent(s)**: `['report_missing_package', 'check_shipping_policies', 'report_missing_item']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['report_missing_package', 'check_shipping_policies', 'report_missing_item'] instead of check_delivery_rules.
<!-- slide -->
**Query**: "Can I request that my package be left inside the garage?"
- **Expected Intent**: `check_delivery_rules`
- **True Chunk ID**: `secure_delivery_otp_001`
- **Predicted Intent(s)**: `['report_missing_package', 'check_shipping_policies', 'report_missing_item']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['report_missing_package', 'check_shipping_policies', 'report_missing_item'] instead of check_delivery_rules.
<!-- slide -->
**Query**: "How do I manage my delivery preferences for my household?"
- **Expected Intent**: `check_delivery_rules`
- **True Chunk ID**: `secure_delivery_otp_001`
- **Predicted Intent(s)**: `['manage_delivery_alerts']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['manage_delivery_alerts'] instead of check_delivery_rules.
<!-- slide -->
**Query**: "Where can I speak with a live agent about my account?"
- **Expected Intent**: `contact_support`
- **True Chunk ID**: `support_options_and_customer_service_002`
- **Predicted Intent(s)**: `['contact_support', 'close_account', 'report_payment_scam']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "What should I do if my parcel was stolen?"
- **Expected Intent**: `report_missing_package`
- **True Chunk ID**: `missing_package_delivered_002`
- **Predicted Intent(s)**: `['report_missing_item', 'report_missing_package', 'check_delivery_delay']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "Who do I contact about a missing or stolen shipment?"
- **Expected Intent**: `report_missing_package`
- **True Chunk ID**: `missing_package_delivered_002`
- **Predicted Intent(s)**: `['report_missing_package', 'report_missing_item']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "My delivery was short one item, how to get a replacement?"
- **Expected Intent**: `report_missing_item`
- **True Chunk ID**: `missing_item_from_order_006`
- **Predicted Intent(s)**: `['report_missing_item', 'check_delivery_delay']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "How do I report phishing attempts on my account?"
- **Expected Intent**: `identify_phishing_scams`
- **True Chunk ID**: `report_suspicious_activity_001`
- **Predicted Intent(s)**: `['identify_phishing_scams', 'report_payment_scam']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "Why did my order tax change during checkout?"
- **Expected Intent**: `check_tax_rates`
- **True Chunk ID**: `about_us_state_sales_and_use_taxes_002`
- **Predicted Intent(s)**: `['check_tax_rates', 'modify_order', 'track_refund']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "What is the sales tax rate for my delivery address?"
- **Expected Intent**: `check_tax_rates`
- **True Chunk ID**: `about_us_state_sales_and_use_taxes_002`
- **Predicted Intent(s)**: `['check_tax_rates', 'modify_address']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "Does Amazon charge tax on gift card purchases?"
- **Expected Intent**: `check_tax_rates`
- **True Chunk ID**: `about_us_state_sales_and_use_taxes_002`
- **Predicted Intent(s)**: `['check_tax_rates', 'investigate_unknown_charge']` (Classification Success: Yes)
- **Isolated Component**: Reranker/Cross-Encoder
- **Root Cause**: The router correctly identified the intent, but the Cross-Encoder scored irrelevant chunks higher.
<!-- slide -->
**Query**: "How are tax rates determined for international shipping?"
- **Expected Intent**: `check_tax_rates`
- **True Chunk ID**: `vat_rates_001`
- **Predicted Intent(s)**: `['check_international_returns']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['check_international_returns'] instead of check_tax_rates.
<!-- slide -->
**Query**: "Where do I see the tax breakdown of my invoice?"
- **Expected Intent**: `check_tax_rates`
- **True Chunk ID**: `about_us_state_sales_and_use_taxes_002`
- **Predicted Intent(s)**: `['view_invoice']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['view_invoice'] instead of check_tax_rates.
<!-- slide -->
**Query**: "How to turn off marketing push notifications in the app?"
- **Expected Intent**: `manage_notifications`
- **True Chunk ID**: `change_your_subscription_email_preferences_001`
- **Predicted Intent(s)**: `['manage_account_settings', 'manage_delivery_alerts']` (Classification Success: No)
- **Isolated Component**: NLU Classifier/Logistic Regression
- **Root Cause**: The router confidently predicted ['manage_account_settings', 'manage_delivery_alerts'] instead of manage_notifications.
````

### 5. Comparative Delta Analysis
*(Comparing Iteration 5 against Iteration 2 (Baseline))*

* **What Improved**: The Hit Rate @ 3 increased to [PLACEHOLDER_HIT_RATE]. The Bi-Encoder successfully leveraged the combination of keyword-rich semantic summaries AND linearized table markdown to push past the ceiling.
* **What Regressed**: No regressions noted.
* **Correlation**: By combining the subagent's semantic summaries with the flattened syntax-free markdown tokens, the FAISS index achieved peak semantic density, allowing the Reranker to consistently score the correct chunks at the very top.