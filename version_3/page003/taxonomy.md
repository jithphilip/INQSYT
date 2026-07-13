# Taxonomy

**Source Page URL:** `https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GQT5HV6YYGNDSFNW`
**Page Title:** Add, Delete, and Manage Addresses - Amazon Customer Service
**Short Page Summary:** This page explains how customers can manage their shipping addresses (add, edit, delete, set default) for future orders via the "Your Addresses" page, and provides links to change addresses on open orders or wish lists.

## Intent Hierarchy
Flat

## Extracted Candidate Intents
- `add_address`
- `edit_address`
- `delete_address`
- `set_default_address`
- `change_order_address`
- `manage_wish_list_address`

## Final Approved Intent List
- `manage_addresses`

## Parent-Child Relationships
N/A

## Synonyms or Alternate Phrasings Observed
- "add a new address"
- "edit an address"
- "delete an address"
- "set a default address"

## Duplicate or Overlapping Intents
- `add_address`, `edit_address`, `delete_address`, and `set_default_address` all represent operations on the same address configuration screen in the user account. Consolidating them into a single `manage_addresses` intent prevents duplication and keeps the taxonomy concise.

## Intent Naming Rationale
- Consolidating the core CRUD actions on addresses under `manage_addresses` creates a more cohesive intent for settings management.
- `change_order_address` and `manage_wish_list_address` were deleted because they redirect the user to external resources.

## Final Taxonomy
After all approved change proposals have been applied:
- **`manage_addresses`**: Add, edit, remove, or set a default shipping address for future orders in Your Account.

---

## Iteration 1 - Final Taxonomy (2026-07-13)

### PAGE_INTENT_FINAL

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?ref_=hp_left_v4_sib&nodeId=GQT5HV6YYGNDSFNW | manage_addresses | Add, edit, remove, or set a default shipping address for future orders in Your Account. | "To add a new address, select Add address. Enter the new address details. Add your delivery preferences and select Add address. To edit an address, select Edit below the address. Change the address details and select Update address. To delete an address, select Remove below the address. Select Yes to confirm. To set a default shipping address, select Set as Default below the preferred address." |
