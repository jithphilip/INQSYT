# Taxonomy

**Source Page URL:** `https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW`
**Page Title:** Tracking your package - Amazon Customer Service
**Short Page Summary:** This page helps customers track their orders and understand the current delivery status of their packages, including those from third-party sellers, and provides initial troubleshooting for delayed or unshipped orders.

## Intent Hierarchy
Flat

## Extracted Candidate Intents
- `track_package`
- `track_third_party_package`
- `understand_delivery_statuses`
- `solve_delivery_problems`
- `contact_carrier`

## Final Approved Intent List
- `track_package`
- `check_delivery_status_meaning`
- `understand_unshipped_order`
- `understand_delayed_order`

## Parent-Child Relationships
N/A

## Synonyms or Alternate Phrasings Observed
- "find tracking numbers"
- "delivery updates"
- "view tracking information"

## Duplicate or Overlapping Intents
- `track_third_party_package` overlapped with `track_package` as both require the customer to navigate to "Your Orders" for tracking updates.

## Intent Naming Rationale
- `understand_delivery_statuses` was renamed to `check_delivery_status_meaning` to align better with a strictly concise `verb_object` format indicating a clearer action.
- `solve_delivery_problems` was split into `understand_unshipped_order` and `understand_delayed_order` to reflect the native, actionable content on the page, excluding links to external pages for missing packages/items.

## Final Taxonomy
After all approved change proposals have been applied:
- **`track_package`**: Track a package or get delivery updates for an order, including packages sold by a third-party seller.
- **`check_delivery_status_meaning`**: Understand the meaning of different delivery statuses like Arriving, Out for delivery, Delivered, and Undeliverable.
- **`understand_unshipped_order`**: Check what to do when an order has not shipped yet.
- **`understand_delayed_order`**: Understand the reasons and cancellation options when an order is delayed.

---

## Iteration 3 - Final Taxonomy (2026-07-10)

### PAGE_INTENT_FINAL

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW | track_package | Track a package or get delivery updates of an order, including packages sold by a third-party seller. | "To get tracking numbers and delivery updates: Check Your Orders Find the order that you want to track Select Track package next to your order" |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW | check_delivery_status_meaning | Understand the meaning of different delivery statuses like Arriving, Out for delivery, Delivered, and Undeliverable. | "Understanding delivery statuses: Your delivery status is in Your Orders: - Arriving: ... - Out for delivery: ... - Delivered: ... - Undeliverable: ..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW | understand_unshipped_order | Check what to do when an order has not shipped yet. | "Order hasn't shipped yet: if you're expecting the package today and there isn't a status update, that's normal. Depending on the carrier, items may ship the same day they're delivered." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GENAFPTNLHV7ZACW | understand_delayed_order | Understand the reasons and cancellation options when an order is delayed. | "Order is delayed: things like weather and traffic can cause delivery delays. Most late parcels arrive within 48 hours of the estimated delivery date. If the order has already been shipped, you can't cancel it." |
