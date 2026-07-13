# Taxonomy

**Source Page URL:** `https://www.amazon.com/gp/help/customer/display.html?nodeId=GSL37WQTJZUYA9QE`
**Page Title:** Cancel Items and Orders - Amazon Customer Service
**Short Page Summary:** This page explains how to cancel physical items or entire orders that have not yet entered the shipping process, including details on third-party seller cancellations and what to do if an order cannot be changed.

## Intent Hierarchy
Flat

## Extracted Candidate Intents
- `cancel_order`
- `cancel_item`
- `cancel_third_party_order`
- `check_cancelled_orders_history`
- `return_shipped_order`
- `contact_third_party_seller`

## Final Approved Intent List
- `cancel_order`

## Parent-Child Relationships
N/A

## Synonyms or Alternate Phrasings Observed
- "cancel items"
- "request cancellation"
- "cancel an order"

## Duplicate or Overlapping Intents
- `cancel_item` and `cancel_third_party_order` overlapped with `cancel_order` as they all use the same entry point ("Your Orders") and core user workflow. Consolidating them under `cancel_order` avoids redundancy.

## Intent Naming Rationale
- `cancel_item` and `cancel_third_party_order` were merged into `cancel_order` because the flow and entry point are the same, and any differences are minor caveats.
- `check_cancelled_orders_history`, `return_shipped_order`, and `contact_third_party_seller` were deleted because they represent minor navigation actions or redirect the user to external pages.

## Final Taxonomy
After all approved change proposals have been applied:
- **`cancel_order`**: Cancel physical items or orders that haven't entered the shipping process yet, including items/orders sold and shipped by a third-party seller.

---

## Iteration 1 - Final Taxonomy (2026-07-13)

### PAGE_INTENT_FINAL

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GSL37WQTJZUYA9QE | cancel_order | Cancel physical items or orders that haven't entered the shipping process yet, including items/orders sold and shipped by a third-party seller. | "To cancel an order that has not entered the shipping process, follow these steps: 1. Go to Your Orders. 2. Find the order that you want to cancel and select View or edit order. 3. Select Cancel items. 4. Check box of the item that you want to cancel from the order. To cancel the entire order, select all the items. 5. Choose a reason for the cancellation and select Request cancellation. Orders sold and shipped by a third-party seller can typically be canceled within one business day." |
