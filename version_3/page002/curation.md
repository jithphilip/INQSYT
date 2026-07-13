# Curation

## Initial Page Observations
The page outlines the criteria and steps for cancelling physical items or orders on Amazon, handles third-party seller cancellation terms, and directs the user to returns or contact pages if the order cannot be changed.

## Page Understanding
The main customer journey is order or item cancellation prior to shipping. Secondary paths cover handling third-party seller orders and workarounds (returns/seller contact) if cancellation is no longer possible.

## Intent Extraction Notes
Extracted intents natively supported by the text content, specifically actions that can be initiated or resolved on the page, while cataloging redirects as candidates to be reviewed.

## Supporting Evidence Collected for Each Intent
- **`cancel_order`**: "To cancel an order that has not entered the shipping process, follow these steps: 1. Go to Your Orders... Select Cancel items... select all the items... Request cancellation."
- **`cancel_item`**: "To cancel an order that has not entered the shipping process... 3. Select Cancel items. 4. Check box of the item that you want to cancel from the order."
- **`cancel_third_party_order`**: "Orders sold and shipped by a third-party seller can typically be canceled within one business day. Once an order is in fulfillment, sellers are required to approve cancellation."
- **`check_cancelled_orders_history`**: "For a history of your cancelled orders, visit Your Orders under Canceled Orders."
- **`return_shipped_order`**: "If your order is shipped directly from Amazon and can't be changed, refuse or return the package using our Online Returns Center."
- **`contact_third_party_seller`**: "If your order is shipped directly from a third-party seller and can't be changed, contact the seller. For more information on contacting the seller, go to Contact Third-Party Sellers."

## Intent Boundary Discussions
Discussed whether `return_shipped_order` and `contact_third_party_seller` are valid intents for this page since they redirect the user to separate help pages/tools.

## Candidate Merge Opportunities
- MERGE `cancel_item` and `cancel_third_party_order` into `cancel_order`.

## Candidate Split Opportunities
- None.

## Candidate Rename Discussions
- None.

## Deleted Candidate Intents and the Reasons
- To be determined after human review.

## Added Candidate Intents and the Reasons
- None.

## Taxonomy Change Proposals
1. MERGE `cancel_item` into `cancel_order` to simplify since the flow is identical.
2. MERGE `cancel_third_party_order` into `cancel_order` as it uses the same "Your Orders" entry point and the third-party details are just caveats.
3. DELETE `check_cancelled_orders_history` as it represents a minor informational lookup.
4. DELETE `return_shipped_order` as it redirects to the Online Returns Center.
5. DELETE `contact_third_party_seller` as it redirects to the Contact Third-Party Sellers page.

---

## Iteration 1 - Fresh Extraction (2026-07-13)

### PAGE_INTENT_CANDIDATES

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GSL37WQTJZUYA9QE | cancel_order | Cancel an entire order that hasn't entered the shipping process yet. | "To cancel an order that has not entered the shipping process, follow these steps: 1. Go to Your Orders. 2. Find the order that you want to cancel and select View or edit order. 3. Select Cancel items. 4. Check box of the item that you want to cancel from the order. To cancel the entire order, select all the items. 5. Choose a reason for the cancellation and select Request cancellation." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GSL37WQTJZUYA9QE | cancel_item | Cancel specific items from an order that hasn't entered the shipping process yet. | "To cancel an order that has not entered the shipping process, follow these steps: ... 3. Select Cancel items. 4. Check box of the item that you want to cancel from the order. To cancel the entire order, select all the items." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GSL37WQTJZUYA9QE | cancel_third_party_order | Cancel items or orders shipped by a third-party seller. | "Orders sold and shipped by a third-party seller can typically be canceled within one business day. Once an order is in fulfillment, sellers are required to approve cancellation." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GSL37WQTJZUYA9QE | check_cancelled_orders_history | View a history of cancelled orders. | "For a history of your cancelled orders, visit Your Orders under Canceled Orders." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GSL37WQTJZUYA9QE | return_shipped_order | Return or refuse a package if the order has already shipped and cannot be changed. | "If your order is shipped directly from Amazon and can't be changed, refuse or return the package using our Online Returns Center." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GSL37WQTJZUYA9QE | contact_third_party_seller | Contact a third-party seller if the order has shipped and cannot be changed. | "If your order is shipped directly from a third-party seller and can't be changed, contact the seller. For more information on contacting the seller, go to Contact Third-Party Sellers." |

### PAGE_INTENT_CHANGE_PROPOSALS

| url | change_type | change_instruction | change_reason | change_evidence | is_approved |
|---|---|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GSL37WQTJZUYA9QE | MERGE | Merge `cancel_item` into `cancel_order`. | Both are executed through the exact same flow under "Your Orders" -> "View or edit order" -> "Cancel items", with the only difference being whether specific items or all items are selected. Consolidating them simplifies the taxonomy. | "To cancel an order that has not entered the shipping process, follow these steps: ... 3. Select Cancel items. 4. Check box of the item that you want to cancel from the order. To cancel the entire order, select all the items." | No |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GSL37WQTJZUYA9QE | MERGE | Merge `cancel_third_party_order` into `cancel_order`. | The entry point ("Your Orders") and core action are identical; the third-party specifics (one business day limit and seller approval) are caveats to the main cancellation intent rather than a separate user workflow. | "Orders sold and shipped by a third-party seller can typically be canceled within one business day. Once an order is in fulfillment, sellers are required to approve cancellation." | No |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GSL37WQTJZUYA9QE | DELETE | Delete candidate intent `check_cancelled_orders_history`. | This is a minor informational navigation step rather than a distinct customer action, and doesn't require a standalone intent on this page. | "For a history of your cancelled orders, visit Your Orders under Canceled Orders." | No |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GSL37WQTJZUYA9QE | DELETE | Delete candidate intent `return_shipped_order`. | The page does not natively handle returns; it redirects the user to the Online Returns Center, which is a separate page/intent. | "If your order is shipped directly from Amazon and can't be changed, refuse or return the package using our Online Returns Center." | No |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GSL37WQTJZUYA9QE | DELETE | Delete candidate intent `contact_third_party_seller`. | The page does not natively support contacting third-party sellers; it redirects to the "Contact Third-Party Sellers" help page. | "If your order is shipped directly from a third-party seller and can't be changed, contact the seller. For more information on contacting the seller, go to Contact Third-Party Sellers." | No |

### STEP_1_CHECKS

| check_type | check_name | check_instruction | is_approved |
|---|---|---|---|
| check_format | check_output_formats | Verify that PAGE_INTENT_CANDIDATES and PAGE_INTENT_CHANGE_PROPOSALS conform to their expected schemas. | No |
| check_evidence | check_intent_grounding | Verify that every candidate intent and every proposed change is supported by evidence from the source page. | No |
| check_reasoning | check_change_proposal_reasons | Verify that every proposed MERGE, SPLIT, RENAME, ADD, or DELETE is reasonable and clearly justified. | No |
| check_coverage | check_intent_coverage | Verify that no obvious customer goal or refinement proposal directly supported by the page has been omitted. | No |
