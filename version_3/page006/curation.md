# Curation

## Initial Page Observations
The page lists Amazon's comprehensive return policies, standard 30-day return windows, extensive exceptions (from 7 days to 365 days for various items/registries), list of non-returnable and final sale items, details on return fees (shipping, late, damage, restocking), refund timelines by payment method, and specific guidelines for heavy/bulky items, global store returns, gifts, bundles, and deluxe deliveries.

## Page Understanding
The main customer journey centers on checking return policies, windows, and eligibility for various product types, as well as understanding fees and timelines associated with those returns.

## Intent Extraction Notes
Extracted intents natively supported by the text content, specifically actions that can be initiated or resolved on the page, while cataloging redirects as candidates to be reviewed.

## Supporting Evidence Collected for Each Intent
- **`check_standard_return_policy`**: "Most items purchased on Amazon.com can be returned within 30 days of delivery... in their original or unused condition... Free returns at over 8,000 locations..."
- **`check_return_window_exceptions`**: "7 Days: Unread Kindle books... 15 Days: Apple Brand... 90 Days: Amazon Renewed... Baby... Birthday... Mattresses... 180 Days: Wedding... 365 Days: Amazon Renewed Premium... Baby Registry..."
- **`check_non_returnable_items`**: "Non-Returnable: Perishables, health/safety... Final Sale: Trading card games... items priced at $3 or less..."
- **`check_return_fees`**: "Return Shipping Fee... Late Fee... Damage Fee... Restocking Fee..."
- **`check_refund_timeline`**: "Gift Card: 2-3 hours... Credit Card: 3-5 business days..."
- **`check_heavy_bulky_return_policy`**: "Heavy and/or Bulky Items... May require a specialty carrier pickup and incur variable return shipping fees."
- **`check_global_store_return_policy`**: "Global Store Returns... Can take up to 25 days to reach Amazon. Amazon automatically refunds up to $20..."
- **`return_gift`**: "Gift Returns: Can be initiated using the 17-digit order number from the packing slip..."
- **`return_bundle`**: "Bundle Returns: For 'Bundle with Savings,' all items in the bundle must be returned together..."
- **`return_special_delivery_item`**: "Special Delivery: Items delivered via 'Deluxe Delivery' services can be instantly returned at the point of delivery."

## Intent Boundary Discussions
Discussed whether exceptions, bulky items, and global store returns deserve separate intents. Consolidating all return rules and exceptions under `check_return_policy` provides a more cohesive intent and avoids excessive minor intents. Similarly, timelines and fees map to intents already defined in page005.

## Candidate Merge Opportunities
- MERGE `check_standard_return_policy`, `check_return_window_exceptions`, `check_non_returnable_items`, `check_heavy_bulky_return_policy`, `check_global_store_return_policy`, `return_bundle`, and `return_special_delivery_item` into `check_return_policy`.
- MERGE `check_return_fees` into `check_refund_fees` (aligned with page005).
- MERGE `check_refund_timeline` into `check_refund_timeline` (aligned with page005).
- DELETE `return_gift` as it redirects.

## Candidate Split Opportunities
- None.

## Candidate Rename Discussions
- None.

## Deleted Candidate Intents and the Reasons
- To be determined after human review.

## Added Candidate Intents and the Reasons
- None.

## Taxonomy Change Proposals
1. MERGE `check_standard_return_policy`, `check_return_window_exceptions`, `check_non_returnable_items`, `check_heavy_bulky_return_policy`, `check_global_store_return_policy`, `return_bundle`, and `return_special_delivery_item` into a single `check_return_policy` intent. This groups all general return terms, exceptions, and specialty item policies into one central intent.
2. MERGE `check_return_fees` into the existing `check_refund_fees` intent (established in page005) to keep fee queries unified.
3. MERGE `check_refund_timeline` into the existing `check_refund_timeline` intent (established in page005) to keep refund timing lookups unified.
4. DELETE `return_gift` because gift returns are completed using an external tool/redirection.

---

## Iteration 1 - Fresh Extraction (2026-07-14)

### PAGE_INTENT_CANDIDATES

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | check_standard_return_policy | Check Amazon's standard return policy (30 days, original condition, drop-off locations). | "Most items purchased on Amazon.com can be returned within 30 days of delivery... returned in their original or unused condition... Free returns are available at over 8,000 locations..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | check_return_window_exceptions | Check return window exceptions ranging from 7 days to 365 days for specific product categories or registries. | "7 Days: Unread Kindle books... 15 Days: Apple Brand... 90 Days: Amazon Renewed... Baby... Birthday... Mattresses... 180 Days: Wedding... 365 Days: Amazon Renewed Premium... Baby Registry..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | check_non_returnable_items | Check which items are non-returnable or sold as final sale. | "Non-Returnable: Perishables, health/safety... Final Sale: Trading card games... items priced at $3 or less..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | check_return_fees | Check shipping, late, damage, or restocking fees associated with returned items. | "Return Shipping Fee... Late Fee... Damage Fee... Restocking Fee..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | check_refund_timeline | Check refund processing timelines for different payment methods. | "Gift Card: 2-3 hours... Credit Card: 3-5 business days..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | check_heavy_bulky_return_policy | Check policies and requirements for heavy and/or bulky returns. | "Heavy and/or Bulky Items... May require a specialty carrier pickup and incur variable return shipping fees." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | check_global_store_return_policy | Check return policy and postage refund guidelines for Global Store items. | "Global Store Returns... Can take up to 25 days to reach Amazon. Amazon automatically refunds up to $20..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | return_gift | Return a gift item using an order number. | "Gift Returns: Can be initiated using the 17-digit order number from the packing slip..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | return_bundle | Check return policies for bundle deals and savings bundles. | "Bundle Returns: For 'Bundle with Savings,' all items in the bundle must be returned together..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | return_special_delivery_item | Return special delivery items at the point of delivery. | "Special Delivery: Items delivered via 'Deluxe Delivery' services can be instantly returned at the point of delivery." |

### PAGE_INTENT_CHANGE_PROPOSALS

| url | change_type | change_instruction | change_reason | change_evidence | is_approved |
|---|---|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | MERGE | Merge `check_standard_return_policy`, `check_return_window_exceptions`, `check_non_returnable_items`, `check_heavy_bulky_return_policy`, `check_global_store_return_policy`, `return_bundle`, and `return_special_delivery_item` into `check_return_policy`. | Consolidating standard return terms, specific product windows, non-returnable lists, and specialty delivery policies into one core intent simplifies the taxonomy and groups general return inquiries together. | "Most items purchased on Amazon.com can be returned within 30 days of delivery... exceptions apply..." | No |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | MERGE | Merge `check_return_fees` into existing intent `check_refund_fees`. | Return fees are identical in nature to restocking/late fees. Merging them keeps all return fee policies under one intent. | "Return Shipping Fee... Late Fee... Damage Fee... Restocking Fee..." | No |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | MERGE | Merge `check_refund_timeline` into existing intent `check_refund_timeline`. | Timelines on this page are a duplicate list of the payment processing timelines in page005. Merging them avoids redundant intents. | "Gift Card: 2-3 hours... Credit Card: 3-5 business days..." | No |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | DELETE | Delete candidate intent `return_gift`. | Gift returns are initiated via an external redirection link, not solved natively on the page. | "Gift Returns: Can be initiated using the 17-digit order number..." | No |

### STEP_1_CHECKS

| check_type | check_name | check_instruction | is_approved |
|---|---|---|---|
| check_format | check_output_formats | Verify that PAGE_INTENT_CANDIDATES and PAGE_INTENT_CHANGE_PROPOSALS conform to their expected schemas. | No |
| check_evidence | check_intent_grounding | Verify that every candidate intent and every proposed change is supported by evidence from the source page. | No |
| check_reasoning | check_change_proposal_reasons | Verify that every proposed MERGE, SPLIT, RENAME, ADD, or DELETE is reasonable and clearly justified. | No |
| check_coverage | check_intent_coverage | Verify that no obvious customer goal or refinement proposal directly supported by the page has been omitted. | No |
