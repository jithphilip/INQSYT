# Taxonomy

**Source Page URL:** `https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7`
**Page Title:** Amazon Return Policies - Amazon Customer Service
**Short Page Summary:** This page details Amazon's standard return window, exceptions (e.g. Kindle books, registries), non-returnable categories, return fees (shipping, late, damage, restocking), refund timelines by payment method, and specific policies for specialty items.

## Intent Hierarchy
Flat

## Extracted Candidate Intents
- `check_standard_return_policy`
- `check_return_window_exceptions`
- `check_non_returnable_items`
- `check_return_fees`
- `check_refund_timeline`
- `check_heavy_bulky_return_policy`
- `check_global_store_return_policy`
- `return_gift`
- `return_bundle`
- `return_special_delivery_item`

## Final Approved Intent List
- `check_return_policy`
- `check_refund_fees`
- `check_refund_timeline`

## Parent-Child Relationships
N/A

## Synonyms or Alternate Phrasings Observed
- "return windows"
- "exceptions to 30 days return"
- "final sale items"
- "return shipping costs"
- "refund method times"

## Duplicate or Overlapping Intents
- Standard returns, exceptions, non-returnable items, heavy items, global store, bundles, and special delivery conditions are consolidated under `check_return_policy`.
- `check_return_fees` is merged into the existing `check_refund_fees` intent.
- `check_refund_timeline` is merged into the existing `check_refund_timeline` intent.
- `return_gift` was deleted because it redirects to the gift returns tool.

## Intent Naming Rationale
- `check_return_policy` is the primary intent resolving all queries on general item return windows, conditions, eligibility, and exceptions.
- `check_refund_fees` covers all customer charges (shipping, late, damage, restocking) associated with returns.
- `check_refund_timeline` covers the expected processing duration for each refund method.

## Final Taxonomy
After all approved change proposals have been applied:
- **`check_return_policy`**: Check general return policies, return windows, exceptions (Kindle books, Baby registry, Renewed, etc.), non-returnable items, and rules for special items (bulky, global, bundles, deluxe delivery).
- **`check_refund_fees`**: Check return shipping fees, restocking fees, late return fees, damage fees, and restocking fee tax rules.
- **`check_refund_timeline`**: Check processing times and timelines for different refund payment methods.

---

## Iteration 1 - Final Taxonomy (2026-07-14)

### PAGE_INTENT_FINAL

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | check_return_policy | Check general return policies, return windows, exceptions, non-returnable items, and rules for special items. | "Most items purchased on Amazon.com can be returned within 30 days of delivery... returned in their original or unused condition... Free returns... exceptions apply... Non-Returnable: Perishables... Heavy and/or Bulky Items... Global Store Returns... Bundle Returns... Special Delivery..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | check_refund_fees | Check return shipping fees, restocking fees, late return fees, damage fees, and restocking fee tax rules. | "Return Shipping Fee: returns are free... Late Fee: did not drop off... Damage Fee: returned damaged... Restocking Fee: collectible cards..." |
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX7 | check_refund_timeline | Check processing times and timelines for different refund payment methods. | "Amazon.com Gift Card: 2-3 hours... Credit Card: 3-5 business days... Shop with Reward Points... Debit Card..." |
