---
name: extract-candidate-intents-from-page
description: Extract grounded candidate customer intents from a single support page.
---

# Purpose

Extract every customer intent supported by the supplied source page.

This skill performs only candidate intent extraction.

It does NOT:

- propose taxonomy changes
- finalize taxonomy
- apply approvals

---

# Inputs

- Source page URL
- Step 1 schema
- Taxonomy specification

---

# Required References

Before execution read:

- specification/step1-schema.md

These specifications define:

- extraction methodology
- naming conventions
- required markdown schemas
- evidence requirements
- validation requirements

They are the authoritative source.

---

# Procedure

1. Read the source page.

2. Understand the customer goals supported by the page.

3. Extract every supported customer intent.

4. Follow the required verb_object naming convention.

5. Ground every intent using exact evidence from the page.

6. Do not invent intents.

7. Ignore external pages referenced by the page.

8. Produce the PAGE_INTENT_CANDIDATES table exactly as defined by the Step 1 schema.

---

# Output

PAGE_INTENT_CANDIDATES

---

# Validation

Before completion verify:

- every intent has evidence
- naming convention is correct
- schema exactly matches specification
- no unsupported intents exist

---

# Failure Conditions

Stop immediately if:

- source page cannot be read
- evidence is insufficient
- schema cannot be satisfied

Never fabricate information.