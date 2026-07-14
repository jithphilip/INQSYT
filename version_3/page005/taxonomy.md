# Taxonomy

**Source Page URL:** `https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B`
**Page Title:** Amazon Refund Timelines - Amazon Customer Service
**Short Page Summary:** This page details the refund processing timelines for various payment methods, return fees (shipping, late, damage, restocking), tax on restocking fees, and instructions for returning advanced refunds/replacement orders to avoid charges.

## Intent Hierarchy
Flat

## Extracted Candidate Intents
- `check_refund_timeline`
- `check_refund_status`
- `return_item_for_refund`
- `exchange_item`
- `check_refund_fees`
- `check_tax_on_restocking_fees`
- `return_gift_for_refund`
- `avoid_late_return_charges`

## Final Approved Intent List
- `check_refund_timeline`
- `check_refund_fees`
- `avoid_late_return_charges`

## Parent-Child Relationships
N/A

## Synonyms or Alternate Phrasings Observed
- "refund timelines"
- "how long does a refund take"
- "return fees"
- "restocking fee tax"
- "advanced refund return deadline"

## Duplicate or Overlapping Intents
- `check_tax_on_restocking_fees` was merged into `check_refund_fees` to simplify fee questions.
- `check_refund_status`, `return_item_for_refund`, `exchange_item`, and `return_gift_for_refund` were deleted because they represent workflows resolved on external tool/help pages.

## Intent Naming Rationale
- `check_refund_timeline` is kept as a standalone intent for looking up payment method timelines.
- `check_refund_fees` is kept to group all return-related fee questions and state-specific tax laws.
- `avoid_late_return_charges` is kept as a distinct intent representing the actions and conditions necessary to avoid automatic credit card charges when receiving advanced refunds or replacements.

## Final Taxonomy
After all approved change proposals have been applied:
- **`check_refund_timeline`**: Check processing times and timelines for different refund payment methods.
- **`check_refund_fees`**: Check return shipping fees, restocking fees, late return fees, damage fees, and restocking fee tax rules.
- **`avoid_late_return_charges`**: Check requirements to avoid charges when receiving an advanced refund or replacement order.

---

## Iteration 1 - Final Taxonomy (2026-07-14)

### PAGE_INTENT_FINAL

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | check_refund_timeline | Check processing times and timelines for different refund payment methods. | "Your bank might need extra time to process a refund. The refund timelines for different refund payment methods are: Credit card: 3-5 business days... Debit card: Up to 10 business days... Checking account: Up to 30 days..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | check_refund_fees | Check return shipping fees, restocking fees, late return fees, damage fees, and restocking fee tax rules. | "Types of return fees are: Return Shipping Fee... Late Fee... Damage Fee... Restocking Fee... Tax on restocking fees may apply to return items shipped and sold by Amazon.com, for customers in: Connecticut, Maryland, Nevada, Pennsylvania, Virginia, West Virginia, Wisconsin." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKQNFKFK5CF3C54B | avoid_late_return_charges | Check requirements to avoid charges when receiving an advanced refund or replacement order. | "To avoid charges after receiving an advanced refund or replacement order: Return items by the date shown in your return confirmation email... If you don't return the item in time... we'll notify you and charge your account..." |
