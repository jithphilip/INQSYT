# Curation

## Initial Page Observations
The page details how to check refund status using "Your Returns" or the confirmation email, explains how refunds are issued to selected payment methods and tracked in "Your Transactions", and outlines refund destinations for gift returns (recipient vs. purchaser).

## Page Understanding
The main customer journey is checking the status and details of a refund. Secondary journeys cover checking where the refund was credited and understanding gift return rules, both resolved natively on this page.

## Intent Extraction Notes
Extracted intents natively supported by the text content, specifically actions that can be initiated or resolved on the page, while cataloging redirects as candidates to be reviewed.

## Supporting Evidence Collected for Each Intent
- **`check_refund_status`**: "To quickly check your refund status: Go to Your Returns... Find the returned item in the Last 3 Months section... You'll be able to see your refund details."
- **`check_refund_payment_method`**: "Refunds go to the refund method that you select in the Online Returns Center... You'll find all refunds and transactions in Your Transactions (https://www.amazon.com/cpe/yourpayments/transactions)."
- **`check_gift_refund_recipient`**: "Once we've processed a gift return, we'll issue a refund to the person who returned the gift: Gift recipient returns: the refund goes to the gift card balance... Gift purchaser returns: the refund goes to the refund method..."

## Intent Boundary Discussions
Discussed whether gift return refund details and checking transactions are distinct intents. Consolidating them into the primary `check_refund_status` intent provides a better user experience and avoids excessive small intents.

## Candidate Merge Opportunities
- MERGE `check_refund_payment_method` and `check_gift_refund_recipient` into `check_refund_status`.

## Candidate Split Opportunities
- None.

## Candidate Rename Discussions
- None.

## Deleted Candidate Intents and the Reasons
- To be determined after human review.

## Added Candidate Intents and the Reasons
- None.

## Taxonomy Change Proposals
1. MERGE `check_refund_payment_method` into `check_refund_status`. Finding the transaction log or looking up the refund method used is part of verifying refund status details.
2. MERGE `check_gift_refund_recipient` into `check_refund_status`. Gift return destination rules are a specific variant of checking where a refund is issued.

---

## Iteration 1 - Fresh Extraction (2026-07-14)

### PAGE_INTENT_CANDIDATES

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GMP8PC8KBY5FCPM2 | check_refund_status | Check the progress and status of a return refund via Your Returns or email confirmation. | "To quickly check your refund status: Go to Your Returns. Find the returned item in the Last 3 Months section. You'll be able to see your refund details. You can also check the status of your refund selecting Return/Refund Status in your return confirmation email." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GMP8PC8KBY5FCPM2 | check_refund_payment_method | Check the payment method credited and view transactions in Your Transactions. | "Refunds go to the refund method that you select in the Online Returns Center. Refund details are always visible once issued. Once we've issued a refund, we'll email you with a detailed refund summary. You'll find all refunds and transactions in Your Transactions." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GMP8PC8KBY5FCPM2 | check_gift_refund_recipient | Check the refund destination for recipient-returned or purchaser-returned gifts. | "Once we've processed a gift return, we'll issue a refund to the person who returned the gift: Gift recipient returns: the refund goes to the gift card balance of the Amazon account used to create the return request. Gift purchaser returns: the refund goes to the refund method that you selected..." |

### PAGE_INTENT_CHANGE_PROPOSALS

| url | change_type | change_instruction | change_reason | change_evidence | is_approved |
|---|---|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GMP8PC8KBY5FCPM2 | MERGE | Merge `check_refund_payment_method` into `check_refund_status`. | Checking where a refund has been credited and reviewing transaction histories are part of verification of the overall refund status. | "Refunds go to the refund method that you select... You'll find all refunds and transactions in Your Transactions." | Yes |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GMP8PC8KBY5FCPM2 | MERGE | Merge `check_gift_refund_recipient` into `check_refund_status`. | Explanations of gift refund destinations (gift card balance for recipient vs. original payment method for purchaser) are caveats of checking refund details. | "Once we've processed a gift return, we'll issue a refund... Gift recipient returns: the refund goes to the gift card balance... Gift purchaser returns: the refund goes to the refund method..." | Yes |

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
| Proposal 1 (MERGE): Merge transaction lookups into `check_refund_status` | Approved | Finding transaction summaries falls under checking refund details. |
| Proposal 2 (MERGE): Merge gift refund rules into `check_refund_status` | Approved | Simplifies the checking process and structures gift recipients as a sub-topic of refunds. |

### Final Curation Decisions (Iteration 1)
Applied all approved proposals:
- Merged `check_refund_payment_method` and `check_gift_refund_recipient` into `check_refund_status`.

