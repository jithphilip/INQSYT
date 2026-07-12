---
name: review-candidate-intents-from-page
description: Generate taxonomy refinement proposals from candidate intents.
---

# Purpose

Review extracted candidate intents and generate taxonomy refinement proposals.

This skill does NOT modify the taxonomy.

It only proposes changes.

---

# Inputs

- Source page URL
- PAGE_INTENT_CANDIDATES

---

# Required References

Read:

- specification/step1-schema.md

---

# Procedure

Review the extracted intents.

Identify opportunities to:

- MERGE
- SPLIT
- RENAME
- ADD
- DELETE

Every proposal must:

- be supported by page evidence
- contain clear reasoning
- use the required schema

Produce:

PAGE_INTENT_CHANGE_PROPOSALS

Produce:

STEP_1_CHECKS

---

# Output

- PAGE_INTENT_CHANGE_PROPOSALS
- STEP_1_CHECK

---

# Constraints

Never modify the taxonomy.

Never assume approval.

Never invent unsupported changes.

---

# Flow

Present PAGE_INTENT_CHANGE_PROPOSALS to the user for approval.

# Validation

Verify:

- every proposal has justification
- every proposal has evidence
- STEP_1_CHECKS is complete