# Taxonomy

**Source Page URL:** `https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GNQFBWDZJN838JZF`
**Page Title:** Manage Payment Methods - Amazon Customer Service
**Short Page Summary:** This page explains how customers can manage their stored payment methods (add, remove, edit) via "Your Payments" or during checkout, registers specialized HSA/FSA cards, and describes the Tap to Pay contactless checkout feature.

## Intent Hierarchy
Flat

## Extracted Candidate Intents
- `add_payment_method`
- `remove_payment_method`
- `change_order_payment_method`
- `register_hsa_fsa_card`
- `pay_with_tap_to_pay`

## Final Approved Intent List
- `manage_payment_methods`

## Parent-Child Relationships
N/A

## Synonyms or Alternate Phrasings Observed
- "add a payment method"
- "remove from wallet"
- "register HSA or FSA card"
- "Tap to Pay"

## Duplicate or Overlapping Intents
- `add_payment_method`, `remove_payment_method`, `register_hsa_fsa_card`, and `pay_with_tap_to_pay` all represent configurations of payment cards in the wallet or checkout flow. Merging them into a single `manage_payment_methods` intent prevents redundancy and simplifies the system.

## Intent Naming Rationale
- Grouping the wallet operations and specialty card registration under a single `manage_payment_methods` intent yields a cleaner configuration settings model.
- `change_order_payment_method` was deleted because it redirects the user to "Change Your Order Information".

## Final Taxonomy
After all approved change proposals have been applied:
- **`manage_payment_methods`**: Add, update, remove, or register payment methods (including credit/debit cards, HSA/FSA cards, and Tap to Pay) in Your Account or during checkout.

---

## Iteration 1 - Final Taxonomy (2026-07-13)

### PAGE_INTENT_FINAL

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GNQFBWDZJN838JZF | manage_payment_methods | Add, update, remove, or register payment methods (including credit/debit cards, HSA/FSA cards, and Tap to Pay) in Your Account or during checkout. | "To manage your payment methods: ... select Add a payment method... select the card you wish to remove... select Remove from wallet... Certain Health Savings Accounts (HSA) cards... can still be used if they're registered as credit cards... With Tap to Pay, you can add a contactless card to your wallet to pay for your order." |
