---
trigger: always_on
---

# Rule: Git Policy

Version control must remain clean and traceable.

Never:

- force push
- rewrite Git history
- commit unrelated files
- commit secrets
- commit credentials
- commit temporary files

Each commit should represent one logical change.

When uncertain about staged files, stop and request confirmation.