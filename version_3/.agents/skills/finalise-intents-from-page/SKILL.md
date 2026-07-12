---
name: finalise-intents-from-page
description: Apply approved taxonomy changes and generate the final taxonomy.
---

# Purpose

Apply only approved taxonomy changes.

Produce the final approved taxonomy.

---

# Inputs

- PAGE_INTENT_CANDIDATES
- PAGE_INTENT_CHANGE_PROPOSALS
- Human approvals

---

# Required References

Read:

- specification/step1-schema.md

---

# Procedure

Apply only approved changes.

Ignore rejected changes.

Update:

- taxonomy.md

Append to:

- curation.md

Append observations to:

- notes.md

Verify consistency.

Generate:

PAGE_INTENT_FINAL

---

# Validation

Verify:

Every final intent

- exists in taxonomy.md

Every approval

- is reflected in taxonomy.md

Every approval and rejection

- is recorded in curation.md

Important observations

- exist in notes.md

---

# Constraints

Never apply rejected proposals.

Never lose previous curation history.

Never overwrite audit history.

---

# Output

PAGE_INTENT_FINAL

Updated:

- taxonomy.md
- curation.md
- notes.md