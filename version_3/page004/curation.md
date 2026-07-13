# Curation

## Initial Page Observations
The page details how customers can manage their payment methods (add, remove) through "Your Payments" or during checkout, handles registering HSA/FSA cards, describes the Tap to Pay feature on the Amazon app, and redirects users looking to modify open orders.

## Page Understanding
The main customer goal is managing the payment wallet. Secondary goals include registering specialty HSA/FSA cards and using Tap to Pay at checkout. Modifying open orders is out-of-scope and handled by redirect.

## Intent Extraction Notes
Extracted intents natively supported by the text content, specifically actions that can be initiated or resolved on the page, while cataloging redirects as candidates to be reviewed.

## Supporting Evidence Collected for Each Intent
- **`add_payment_method`**: "To manage your payment methods... To add a payment method, select Add a payment method." and "You can also add a new credit/debit card to your account while placing an order through the shopping cart..."
- **`remove_payment_method`**: "To remove a payment method, select the card you wish to remove. When the card opens, select Remove from wallet."
- **`change_order_payment_method`**: "To change the payment method for an open order, go to Change Your Order Information."
- **`register_hsa_fsa_card`**: "Certain Health Savings Accounts (HSA) cards cannot be registered as Flexible Spending Accounts (FSA) or HSA cards with Amazon but can still be used if they're registered as credit cards."
- **`pay_with_tap_to_pay`**: "With Tap to Pay, you can add a contactless card to your wallet to pay for your order. Use the Amazon app with a compatible device for Tap to Pay transactions."

## Intent Boundary Discussions
Discussed whether Tap to Pay and HSA/FSA registration are distinct enough to be separate intents, or if they should be consolidated under a broader wallet management intent.

## Candidate Merge Opportunities
- MERGE `add_payment_method`, `remove_payment_method`, `register_hsa_fsa_card`, and `pay_with_tap_to_pay` into a single `manage_payment_methods` intent since they all represent actions for setting up and configuring payment options in the Amazon wallet/checkout.

## Candidate Split Opportunities
- None.

## Candidate Rename Discussions
- None.

## Deleted Candidate Intents and the Reasons
- To be determined after human review.

## Added Candidate Intents and the Reasons
- None.

## Taxonomy Change Proposals
1. MERGE `add_payment_method`, `remove_payment_method`, `register_hsa_fsa_card`, and `pay_with_tap_to_pay` into `manage_payment_methods`. These are all sub-features of configuring and managing stored payment methods (wallet settings), and consolidating them simplifies the taxonomy.
2. DELETE `change_order_payment_method` because the page does not natively support changing payment methods on open orders and redirects to another help page.

---

## Iteration 1 - Fresh Extraction (2026-07-13)

### PAGE_INTENT_CANDIDATES

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GNQFBWDZJN838JZF | add_payment_method | Add a new credit, debit, or other payment card to the Amazon account. | "To manage your payment methods: ... To add a payment method, select Add a payment method." and "You can also add a new credit/debit card to your account while placing an order through the shopping cart; when on the Select a Payment Method page, choose Add a credit or debit card and enter your details." |
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GNQFBWDZJN838JZF | remove_payment_method | Remove an existing payment card from the account. | "To remove a payment method, select the card you wish to remove. When the card opens, select Remove from wallet." |
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GNQFBWDZJN838JZF | change_order_payment_method | Change the payment method used on an open order. | "Updating a payment method in Your Payments will not change the payment method on open orders. To change the payment method for an open order, go to Change Your Order Information (https://www.amazon.com/gp/help/customer/display.html?nodeId=GSWAYSNV7RBSTND9)." |
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GNQFBWDZJN838JZF | register_hsa_fsa_card | Register a Health Savings Account (HSA) or Flexible Spending Account (FSA) card. | "Certain Health Savings Accounts (HSA) cards cannot be registered as Flexible Spending Accounts (FSA) or HSA cards with Amazon but can still be used if they're registered as credit cards. If you register your HSA card as a credit card, you'll be responsible for ensuring the card is used only for eligible products." |
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GNQFBWDZJN838JZF | pay_with_tap_to_pay | Add a contactless card and pay using Tap to Pay on the Amazon app. | "With Tap to Pay, you can add a contactless card to your wallet to pay for your order. Use the Amazon app with a compatible device for Tap to Pay transactions. There are no transaction limits. Select payment method at checkout for the Tap to Pay feature to appear." |

### PAGE_INTENT_CHANGE_PROPOSALS

| url | change_type | change_instruction | change_reason | change_evidence | is_approved |
|---|---|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GNQFBWDZJN838JZF | MERGE | Merge `add_payment_method`, `remove_payment_method`, `register_hsa_fsa_card`, and `pay_with_tap_to_pay` into `manage_payment_methods`. | All four actions are different ways of configuring, managing, or registering payment methods on the account. Consolidating them into a single intent avoids redundancy. | "Add or update your payment methods through Your Payments in Your Account." | Yes |
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GNQFBWDZJN838JZF | DELETE | Delete candidate intent `change_order_payment_method`. | The page does not natively support updating payment methods for open orders; it redirects the user to "Change Your Order Information". | "To change the payment method for an open order, go to Change Your Order Information (https://www.amazon.com/gp/help/customer/display.html?nodeId=GSWAYSNV7RBSTND9)." | Yes |

### STEP_1_CHECKS

| check_type | check_name | check_instruction | is_approved |
|---|---|---|---|
| check_format | check_output_formats | Verify that PAGE_INTENT_CANDIDATES and PAGE_INTENT_CHANGE_PROPOSALS conform to their expected schemas. | Yes |
| check_evidence | check_intent_grounding | Verify that every candidate intent and every proposed change is supported by evidence from the source page. | Yes |
| check_reasoning | check_change_proposal_reasons | Verify that every proposed MERGE, SPLIT, RENAME, ADD, or DELETE is reasonable and clearly justified. | Yes |
| check_coverage | check_intent_coverage | Verify that no obvious customer goal or refinement proposal directly supported by the page has been omitted. | Yes |

### Human Approvals and Rejections (Iteration 1)

| proposal | decision | rationale |
|---|---|---|
| Proposal 1 (MERGE): Merge payment card setup/checkout features into `manage_payment_methods` | Approved | Grouping the CRUD and specific settings actions on payment cards simplifies taxonomy. |
| Proposal 2 (DELETE): Delete `change_order_payment_method` | Approved | Redirects to external page. |

### Final Curation Decisions (Iteration 1)
Applied all approved proposals:
- Merged `add_payment_method`, `remove_payment_method`, `register_hsa_fsa_card`, and `pay_with_tap_to_pay` into `manage_payment_methods`.
- Deleted `change_order_payment_method` because it redirects to the open orders page.

