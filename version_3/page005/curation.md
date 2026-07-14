# Curation

## Initial Page Observations
The page outlines how refund timelines and methods vary based on item condition and purchase details. It details processing timelines for various payment methods (credit cards, debit cards, gift cards, etc.), lists refund reduction fees (restocking, late, damage, shipping), and provides state-specific tax details on restocking fees.

## Page Understanding
The main customer journey centers on understanding how long a refund will take to process and how much will be refunded (including potential fee deductions). Secondary journeys include returning items, exchanging items, and checking refund status, which redirect to external pages.

## Intent Extraction Notes
Extracted intents natively supported by the text content, specifically actions that can be initiated or resolved on the page, while cataloging redirects as candidates to be reviewed.

## Supporting Evidence Collected for Each Intent
- **`check_refund_timeline`**: "Your bank might need extra time to process a refund. The refund timelines for different refund payment methods are: Credit card: 3-5 business days... Debit card: Up to 10 business days... Checking account: Up to 30 days..."
- **`check_refund_status`**: "To check your refund status, go to Your Returns."
- **`return_item_for_refund`**: "You can use the Online Returns Center to return most items within 30 days of delivery for a refund."
- **`exchange_item`**: "We'll offer a replacement or exchange order instead of a refund for selected items. For more information on exchanges, go to Exchange an item."
- **`check_refund_fees`**: "Types of return fees are: Return Shipping Fee... Late Fee... Damage Fee... Restocking Fee..."
- **`check_tax_on_restocking_fees`**: "Tax on restocking fees may apply to return items shipped and sold by Amazon.com, for customers in: Connecticut, Maryland, Nevada, Pennsylvania, Virginia, West Virginia, Wisconsin."
- **`return_gift_for_refund`**: "Gift: Once we've processed a gift return, we'll issue a refund to the person who returned the gift. Go to Return a Gift for more information."
- **`avoid_late_return_charges`**: "To avoid charges after receiving an advanced refund or replacement order: Return items by the date shown... If you don't return the item in time... we'll charge your account..."

## Intent Boundary Discussions
Discussed whether refund timelines and refund fees should be kept as separate intents. Timelines answer "when" the money arrives, whereas fees answer "how much" is deducted, representing two distinct customer query types that are both natively answered on this page.

## Candidate Merge Opportunities
- MERGE `check_refund_timeline` and `avoid_late_return_charges` into `check_refund_timeline`.
- MERGE `check_refund_fees` and `check_tax_on_restocking_fees` into `check_refund_fees`.
- DELETE `check_refund_status`, `return_item_for_refund`, `exchange_item`, and `return_gift_for_refund`.

## Candidate Split Opportunities
- None.

## Candidate Rename Discussions
- None.

## Deleted Candidate Intents and the Reasons
- To be determined after human review.

## Added Candidate Intents and the Reasons
- None.

## Taxonomy Change Proposals
1. MERGE `avoid_late_return_charges` into `check_refund_timeline`. Timelines for advanced refunds and late charge penalties are closely related to refund method timelines and schedules.
2. MERGE `check_tax_on_restocking_fees` into `check_refund_fees`. Restocking fee tax is a sub-regulation of restocking fees.
3. DELETE `check_refund_status` because it redirects the user to the "Your Returns" page.
4. DELETE `return_item_for_refund` because it redirects the user to the "Online Returns Center".
5. DELETE `exchange_item` because it redirects the user to the "Exchange an item" help page.
6. DELETE `return_gift_for_refund` because it redirects the user to the "Return a Gift" page.

---

## Iteration 1 - Fresh Extraction (2026-07-14)

### PAGE_INTENT_CANDIDATES

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | check_refund_timeline | Check the processing times and timelines for different refund payment methods. | "Your bank might need extra time to process a refund. The refund timelines for different refund payment methods are: Credit card: 3-5 business days... Debit card: Up to 10 business days... Checking account: Up to 30 days..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | check_refund_status | Go to the returns history to check the status of a refund. | "To check your refund status, go to Your Returns." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | return_item_for_refund | Return an item to Amazon for a refund. | "You can use the Online Returns Center to return most items within 30 days of delivery for a refund." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | exchange_item | Return an item to Amazon for a replacement or exchange instead of a refund. | "We'll offer a replacement or exchange order instead of a refund for selected items. For more information on exchanges, go to Exchange an item." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | check_refund_fees | Check the return fees (restocking, shipping, late, damage) that may reduce a refund. | "Types of return fees are: Return Shipping Fee... Late Fee... Damage Fee... Restocking Fee..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | check_tax_on_restocking_fees | Check if tax on restocking fees applies to returned items. | "Tax on restocking fees may apply to return items shipped and sold by Amazon.com, for customers in: Connecticut, Maryland, Nevada, Pennsylvania, Virginia, West Virginia, Wisconsin." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | return_gift_for_refund | Return a gift item to Amazon for a refund. | "Gift: Once we've processed a gift return, we'll issue a refund to the person who returned the gift. Go to Return a Gift for more information." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | avoid_late_return_charges | Check terms to avoid charges on advanced refunds or replacement orders. | "To avoid charges after receiving an advanced refund or replacement order: Return items by the date shown... If you don't return the item in time... we'll charge your account..." |

### PAGE_INTENT_CHANGE_PROPOSALS

| url | change_type | change_instruction | change_reason | change_evidence | is_approved |
|---|---|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | MERGE | Merge `avoid_late_return_charges` into `check_refund_timeline`. | Timelines and deadlines for advanced refunds/late return charges are closely related to processing times and refund methods. Consolidating them keeps timeline questions in one place. | "To avoid charges after receiving an advanced refund or replacement order: Return items by the date shown in your return confirmation email... If you don't return the item in time... we'll notify you and charge your account..." | No |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | MERGE | Merge `check_tax_on_restocking_fees` into `check_refund_fees`. | Restocking fee tax is a sub-topic of restocking fees and other return charges. Consolidation keeps fee inquiries grouped together. | "Tax on restocking fees may apply to return items shipped and sold by Amazon.com, for customers in: Connecticut, Maryland, Nevada, Pennsylvania, Virginia, West Virginia, Wisconsin." | No |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | DELETE | Delete candidate intent `check_refund_status`. | The page does not natively allow checking refund status; it redirects to "Your Returns". | "To check your refund status, go to Your Returns." | No |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | DELETE | Delete candidate intent `return_item_for_refund`. | The page does not natively resolve item returns; it redirects the user to the "Online Returns Center". | "You can use the Online Returns Center to return most items within 30 days of delivery for a refund." | No |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | DELETE | Delete candidate intent `exchange_item`. | The page does not natively resolve item exchanges; it redirects the user to "Exchange an item". | "For more information on exchanges, go to Exchange an item." | No |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | DELETE | Delete candidate intent `return_gift_for_refund`. | The page does not natively resolve gift returns; it redirects the user to "Return a Gift". | "Go to Return a Gift for more information." | No |

### STEP_1_CHECKS

| check_type | check_name | check_instruction | is_approved |
|---|---|---|---|
| check_format | check_output_formats | Verify that PAGE_INTENT_CANDIDATES and PAGE_INTENT_CHANGE_PROPOSALS conform to their expected schemas. | No |
| check_evidence | check_intent_grounding | Verify that every candidate intent and every proposed change is supported by evidence from the source page. | No |
| check_reasoning | check_change_proposal_reasons | Verify that every proposed MERGE, SPLIT, RENAME, ADD, or DELETE is reasonable and clearly justified. | No |
| check_coverage | check_intent_coverage | Verify that no obvious customer goal or refinement proposal directly supported by the page has been omitted. | No |
