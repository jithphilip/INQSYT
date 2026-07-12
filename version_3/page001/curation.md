# Curation

## Initial Page Observations
The page provides direct tracking steps, defines various delivery statuses, explains some troubleshooting (delayed, unshipped), and links out to carriers or missing package pages.

## Page Understanding
The primary goal is order tracking. A secondary goal is troubleshooting delivery expectations.

## Intent Extraction Notes
Extracted intents supported natively on the page. Ignored intents where the only action is navigating to another page (except where initially captured as candidates for review).

## Supporting Evidence Collected for Each Intent
- **`track_package`**: "To get tracking numbers and delivery updates... Go to Your Orders - Find the order you want to track - Select track package next to your order"
- **`track_third_party_package`**: "You can only view tracking information if: - the third-party seller shares this info with us - you chose a trackable shipping option"
- **`understand_delivery_statuses`**: "Your delivery status is in Your Orders: - Arriving: usually followed by a date... - Out for delivery: ... - Delivered: ... - Undeliverable: ..."
- **`solve_delivery_problems`**: "Solving delivery problems You can check what to do when: - Order hasn't shipped yet: ... - Order is delayed: ... - Missing package: ... - Missing items: ..."
- **`contact_carrier`**: "To contact the company that's delivering your package, go to contact a carrier."

## Intent Boundary Discussions
There was ambiguity on whether to include "missing items" and "missing packages" under `solve_delivery_problems` since the page only provides redirect links for them, rather than solving the problem natively on the page itself.

## Candidate Merge Opportunities
- MERGE `track_third_party_package` into `track_package` because the action (tracking) is identical.

## Candidate Split Opportunities
- SPLIT `solve_delivery_problems` into `understand_unshipped_order` and `understand_delayed_order` (removing missing item/package as they redirect).

## Candidate Rename Discussions
- RENAME `understand_delivery_statuses` to `check_delivery_status_meaning` to have clearer action-oriented verbs.

## Deleted Candidate Intents and the Reasons
- DELETE `contact_carrier`. Reason: The page only provides a link to an outside page for contacting a carrier.

## Added Candidate Intents and the Reasons
- None

## Taxonomy Change Proposals
1. SPLIT `solve_delivery_problems` into `understand_unshipped_order` and `understand_delayed_order`.
2. DELETE `contact_carrier`.
3. MERGE `track_third_party_package` into `track_package`.
4. RENAME `understand_delivery_statuses` to `check_delivery_status_meaning`.

## Human Approvals and Rejections
- Proposal 1 (SPLIT): Rejected by human reviewer.
- Proposal 2 (DELETE): Approved by human reviewer.
- Proposal 3 (MERGE): Approved by human reviewer.
- Proposal 4 (RENAME): Approved by human reviewer.

## Final Curation Decisions
Applied the approved Merge, Delete, and Rename proposals. Retained `solve_delivery_problems` as it was originally extracted since the split proposal was rejected.

## Validation Notes
- Verified all format constraints and schema matches.
- Verified evidence grounds the intents properly.
- All 4 step checks were explicitly approved by the human reviewer.

## Assumptions Made During Extraction
- Assumed third-party package tracking is just a variant of standard tracking due to the shared UI location ("Your Orders").

---

## Iteration 2 - Fresh Extraction (2026-07-10)

### Initial Page Observations
Performed a fresh extraction of the Amazon help page "Tracking your package" using the raw text content. The page focuses on providing self-service package tracking steps, third-party seller shipping caveats, a translation of delivery statuses, and troubleshooting steps for late or unshipped orders.

### Page Understanding
The main customer journey centers on order tracking and status clarification, with sub-flows for delivery troubleshooting (unshipped/delayed packages).

### Intent Extraction Notes
Natively supported customer intents were extracted using strict `verb_object` formatting. Captures all details on the page before structured refinement.

### Supporting Evidence Collected for Each Intent
- **`track_package`**: "To get tracking numbers and delivery updates: 1. Check Your Orders. 2. Find the order that you want to track. 3. Select 'Track package' next to your order."
- **`track_third_party_package`**: "Track packages from third-party sellers... You can only access tracking information if: - the third-party seller shares this info with us - you chose a trackable shipping option"
- **`understand_delivery_statuses`**: "Understanding delivery statuses: Your delivery status is in Your Orders: - Arriving: ... - Out for delivery: ... - Delivered: ... - Undeliverable: ..."
- **`solve_delivery_problems`**: "Fix a delivery issue: Most issues can be fixed quickly. You can check what to do when: - Order hasn't shipped yet: ... - Order is delayed: ... - Missing package: ... - Missing items: ..."
- **`contact_carrier`**: "To contact the company that's delivering your package, refer to 'Contact a carrier'."

### Intent Boundary Discussions
Discussed whether `contact_carrier`, `missing package`, and `missing items` are valid intents for this page, since they point directly to outside help pages rather than providing native resolutions. 

### Candidate Merge Opportunities
- MERGE `track_third_party_package` into `track_package` as the primary tracking entry point ("Your Orders") is the same.

### Candidate Split Opportunities
- SPLIT `solve_delivery_problems` into `understand_unshipped_order` and `understand_delayed_order` because the page provides native guidance for these, while missing items and missing packages redirect elsewhere.

### Candidate Rename Discussions
- RENAME `understand_delivery_statuses` to `check_delivery_status_meaning` to align with the verb-object style.

### Deleted Candidate Intents and the Reasons
- DELETE `contact_carrier`. Reason: Natively out of scope; only redirects to another page.

### Added Candidate Intents and the Reasons
- None.

### Taxonomy Change Proposals (Iteration 2)
1. MERGE `track_third_party_package` into `track_package`.
2. DELETE `contact_carrier`.
3. RENAME `understand_delivery_statuses` to `check_delivery_status_meaning`.
4. SPLIT `solve_delivery_problems` into `understand_unshipped_order` and `understand_delayed_order`.

### Human Approvals and Rejections (Iteration 2)
- Proposal 1 (MERGE): Approved by human reviewer.
- Proposal 2 (DELETE): Approved by human reviewer.
- Proposal 3 (RENAME): Approved by human reviewer.
- Proposal 4 (SPLIT): Approved by human reviewer.

### Final Curation Decisions (Iteration 2)
Applied all approved changes:
- Merged `track_third_party_package` into `track_package`.
- Deleted `contact_carrier` as it is out-of-scope (links to outside page).
- Renamed `understand_delivery_statuses` to `check_delivery_status_meaning`.
- Split `solve_delivery_problems` into `understand_unshipped_order` and `understand_delayed_order` (removing in-text links for missing packages and items).

### Validation Notes (Iteration 2)
- Checked formatting and schemas for tables.
- Confirmed evidence grounding for all final intents.
- Validated that splits, merges, renames, and deletions are logical and consistent.
- Validation checks completed and all 4 check checks passed.

---

## Iteration 3 - Fresh Extraction (2026-07-10)

### PAGE_INTENT_CANDIDATES

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW | track_package | Track a package or get delivery updates for an order. | To get tracking numbers and delivery updates: Check Your Orders Find the order that you want to track Select Track package next to your order |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW | track_third_party_package | Track a package shipped by a third-party seller. | Track packages from third-party sellers: ... You can only access tracking information if: - the third-party seller shares this info with us - you chose a trackable shipping option |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW | understand_delivery_statuses | Understand what different delivery statuses mean. | Understanding delivery statuses: Your delivery status is in Your Orders: - Arriving: usually followed by a date. Your package is on its way to you - Out for delivery: your package will be delivered today - Delivered: your package has been delivered, and might be in your safe space - Undeliverable: your package couldn't be delivered, and will be returned to Amazon. When we receive it, we'll automatically issue you a refund. Visit the Undeliverable packages help page. |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW | solve_delivery_problems | Fix a delivery issue such as an unshipped order, delayed order, missing package, or missing items. | Fix a delivery issue: Most issues can be fixed quickly. You can check what to do when: - Order hasn't shipped yet: ... - Order is delayed: ... - Missing package: ... - Missing items: ... |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW | contact_carrier | Contact the shipping carrier delivering the package. | To contact the company that's delivering your package, refer to Contact a carrier. |

### PAGE_INTENT_CHANGE_PROPOSALS

| url | change_type | change_instruction | change_reason | change_evidence | is_approved |
|---|---|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW | MERGE | Merge `track_third_party_package` into `track_package`. | The tracking workflow is identical (visiting 'Your Orders'), and consolidating them avoids unnecessary redundancy. | "To check if you ordered from a third-party seller, refer to Your Orders and review the seller name. You can only access tracking information if: - the third-party seller shares this info with us - you chose a trackable shipping option" | Yes |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW | DELETE | Delete candidate intent `contact_carrier`. | The page does not natively resolve carrier issues; it only points to an external page link. | "To contact the company that's delivering your package, refer to Contact a carrier." | Yes |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW | RENAME | Rename candidate intent `understand_delivery_statuses` to `check_delivery_status_meaning`. | The renamed intent better matches standard verb_object styling and clarifies the specific user action. | "Understanding delivery statuses: Your delivery status is in Your Orders: - Arriving: ... - Out for delivery: ... - Delivered: ... - Undeliverable: ..." | Yes |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW | SPLIT | Split candidate intent `solve_delivery_problems` into `understand_unshipped_order` and `understand_delayed_order`. | The page contains native troubleshooting instructions for unshipped and delayed orders, whereas missing items and packages redirect to external resources. | "Fix a delivery issue: Most issues can be fixed quickly. You can check what to do when: - Order hasn't shipped yet: ... - Order is delayed: ... - Missing package: ... - Missing items: ..." | Yes |

### STEP_1_CHECKS

| check_type | check_name | check_instruction | is_approved |
|---|---|---|---|
| check_format | check_output_formats | Verify that PAGE_INTENT_CANDIDATES and PAGE_INTENT_CHANGE_PROPOSALS conform to their expected schemas. | Yes |
| check_evidence | check_intent_grounding | Verify that every candidate intent and every proposed change is supported by evidence from the source page. | Yes |
| check_reasoning | check_change_proposal_reasons | Verify that every proposed MERGE, SPLIT, RENAME, ADD, or DELETE is reasonable and clearly justified. | Yes |
| check_coverage | check_intent_coverage | Verify that no obvious customer goal or refinement proposal directly supported by the page has been omitted. | Yes |

### Human Approvals and Rejections (Iteration 3)

| proposal | decision | rationale |
|---|---|---|
| Proposal 1 (MERGE): Merge `track_third_party_package` into `track_package` | Approved | Tracking workflow is identical (checking 'Your Orders'). |
| Proposal 2 (DELETE): Delete `contact_carrier` | Approved | Out of scope; only redirects to an external page. |
| Proposal 3 (RENAME): Rename `understand_delivery_statuses` to `check_delivery_status_meaning` | Approved | Better verb-object style and clearer action. |
| Proposal 4 (SPLIT): Split `solve_delivery_problems` into `understand_unshipped_order` and `understand_delayed_order` | Approved | Distinct native steps on page for unshipped/delayed, whereas other issues redirect. |

### Final Curation Decisions (Iteration 3)
Applied all approved proposals:
- Merged `track_third_party_package` into `track_package`.
- Deleted `contact_carrier` (links to external page).
- Renamed `understand_delivery_statuses` to `check_delivery_status_meaning`.
- Split `solve_delivery_problems` into `understand_unshipped_order` and `understand_delayed_order`.
- 
