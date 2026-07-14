# Taxonomy

**Source Page URL:** `https://www.amazon.com/gp/help/customer/display.html?nodeId=GMP8PC8KBY5FCPM2`
**Page Title:** Check Your Refund Status - Amazon Customer Service
**Short Page Summary:** This page explains how customers can check the status and processing details of a refund using "Your Returns," find transaction summaries in "Your Transactions," and outlines where refunds are credited for standard and gift returns.

## Intent Hierarchy
Flat

## Extracted Candidate Intents
- `check_refund_status`
- `check_refund_payment_method`
- `check_gift_refund_recipient`

## Final Approved Intent List
- `check_refund_status`

## Parent-Child Relationships
N/A

## Synonyms or Alternate Phrasings Observed
- "check refund status"
- "track return refund"
- "view refund history"
- "gift return refund location"

## Duplicate or Overlapping Intents
- `check_refund_payment_method` and `check_gift_refund_recipient` represent specific aspects of checking a refund's status and destination. Merging them into a single `check_refund_status` intent prevents redundancy.

## Intent Naming Rationale
- `check_refund_status` resolves all customer questions on return tracking, refund processing states, transaction logs, and gift refund distribution rules.

## Final Taxonomy
After all approved change proposals have been applied:
- **`check_refund_status`**: Check the status, payment details, and gift return rules for refunds in Your Returns or Your Transactions.

---

## Iteration 1 - Final Taxonomy (2026-07-14)

### PAGE_INTENT_FINAL

| url | intent_name | intent_description | evidence |
|---|---|---|---|
| https://www.amazon.com/gp/help/customer/display.html?nodeId=GMP8PC8KBY5FCPM2 | check_refund_status | Check the status, payment details, and gift return rules for refunds in Your Returns or Your Transactions. | "To quickly check your refund status: Go to Your Returns. Find the returned item in the Last 3 Months section. You'll be able to see your refund details... You'll find all refunds and transactions in Your Transactions... Gift recipient returns: the refund goes to the gift card balance of the Amazon account used to create the return request. Gift purchaser returns: the refund goes to the refund method that you selected..." |
