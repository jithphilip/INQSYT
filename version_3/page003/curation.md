# Curation

## Initial Page Observations
The page explains how customers can manage their shipping addresses (add, edit, delete, set default) for future orders via the "Your Addresses" page, and provides links to change addresses on open orders or wish lists.

## Page Understanding
The primary customer goal is managing shipping addresses stored in the account profile. Secondary goals cover resolving address issues on open orders or wish lists, which are handled via external page redirects.

## Intent Extraction Notes
Extracted intents natively supported by the text content, specifically actions that can be initiated or resolved on the page, while cataloging redirects as candidates to be reviewed.

## Supporting Evidence Collected for Each Intent
- **`add_address`**: "To add a new address, select Add address. Enter the new address details. Add your delivery preferences and select Add address."
- **`edit_address`**: "To edit an address, select Edit below the address. Change the address details and select Update address."
- **`delete_address`**: "To delete an address, select Remove below the address. Select Yes to confirm."
- **`set_default_address`**: "To set a default shipping address, select Set as Default below the preferred address."
- **`change_order_address`**: "For open orders, visit Change Your Order Information."
- **`manage_wish_list_address`**: "For wish lists, visit Create Your List."

## Intent Boundary Discussions
Discussed whether `change_order_address` and `manage_wish_list_address` should be included since the page only contains outbound links for them.

## Candidate Merge Opportunities
- MERGE `add_address`, `edit_address`, `delete_address`, and `set_default_address` into `manage_addresses` since they are all performed on the same "Your Addresses" settings dashboard.

## Candidate Split Opportunities
- None.

## Candidate Rename Discussions
- None.

## Deleted Candidate Intents and the Reasons
- To be determined after human review.

## Added Candidate Intents and the Reasons
- None.

## Taxonomy Change Proposals
1. MERGE `add_address`, `edit_address`, `delete_address`, and `set_default_address` into `manage_addresses`. Consolidating these under a single intent simplifies the taxonomy and reflects that they are all actions on the same account setting page.
2. DELETE `change_order_address` because it redirects the user to "Change Your Order Information".
3. DELETE `manage_wish_list_address` because it redirects the user to "Create Your List".

---

## Iteration 1 - Fresh Extraction (2026-07-13)

### PAGE_INTENT_CANDIDATES

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GQT5HV6YYGNDSFNW | add_address | Add a new shipping address to the account for future orders. | "To add a new address, select Add address. Enter the new address details. Add your delivery preferences and select Add address." |
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GQT5HV6YYGNDSFNW | edit_address | Edit an existing shipping address in the account. | "To edit an address, select Edit below the address. Change the address details and select Update address." |
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GQT5HV6YYGNDSFNW | delete_address | Delete an existing shipping address from the account. | "To delete an address, select Remove below the address. Select Yes to confirm. You can’t delete an address with pending Subscribe and Save orders." |
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GQT5HV6YYGNDSFNW | set_default_address | Set a shipping address as the default for future orders. | "To set a default shipping address, select Set as Default below the preferred address." |
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GQT5HV6YYGNDSFNW | change_order_address | Change the shipping address on an open order. | "For open orders, visit Change Your Order Information." |
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GQT5HV6YYGNDSFNW | manage_wish_list_address | Manage the shipping address associated with a wish list. | "For wish lists, visit Create Your List." |

### PAGE_INTENT_CHANGE_PROPOSALS

| url | change_type | change_instruction | change_reason | change_evidence | is_approved |
|---|---|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GQT5HV6YYGNDSFNW | MERGE | Merge `add_address`, `edit_address`, `delete_address`, and `set_default_address` into `manage_addresses`. | All four actions are sub-features of the "Your Addresses" page (`https://www.amazon.com/a/addresses/`) and are performed on that same dashboard. Merging them keeps the taxonomy clean and concise. | "How to add, edit, and delete your addresses for future orders: 1. Visit Your Addresses in Your Account." | No |
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GQT5HV6YYGNDSFNW | DELETE | Delete candidate intent `change_order_address`. | The page does not natively handle address modifications for open orders; it redirects to "Change Your Order Information". | "For open orders, visit Change Your Order Information." | No |
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GQT5HV6YYGNDSFNW | DELETE | Delete candidate intent `manage_wish_list_address`. | The page does not natively handle wish list addresses; it redirects to "Create Your List". | "For wish lists, visit Create Your List." | No |

### STEP_1_CHECKS

| check_type | check_name | check_instruction | is_approved |
|---|---|---|---|
| check_format | check_output_formats | Verify that PAGE_INTENT_CANDIDATES and PAGE_INTENT_CHANGE_PROPOSALS conform to their expected schemas. | No |
| check_evidence | check_intent_grounding | Verify that every candidate intent and every proposed change is supported by evidence from the source page. | No |
| check_reasoning | check_change_proposal_reasons | Verify that every proposed MERGE, SPLIT, RENAME, ADD, or DELETE is reasonable and clearly justified. | No |
| check_coverage | check_intent_coverage | Verify that no obvious customer goal or refinement proposal directly supported by the page has been omitted. | No |
