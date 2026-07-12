---
name: write-with-git
description: Persist project outputs and create a Git version after every successful write operation.
---

# Purpose

Persist project artifacts.

Immediately version every successful write operation.

---

# Inputs

- Content
- Destination file
- Write mode

---

# Procedure

1. Write the supplied content to the specified destination file.

2. Verify the write succeeded.

3. Stage only modified files.

4. Generate an appropriate commit message.

5. Ask the user for confirmation before committing if required by the active workflow.

6. Create exactly one commit representing this logical write operation.

7. Report:

- modified files
- commit hash
- commit message

---

# Push

When instructed by the active workflow:

Push all local commits to the configured remote repository.

Report push status.

---

# Constraints

Never:

- use force push
- rewrite history
- commit unrelated files
- commit secrets
- ignore write failures

---

# Output

Return:

- write status
- modified files
- commit hash
- push status (if executed)

---

# Failure Conditions

Stop if:

- file write fails
- git commit fails
- git push fails

Never silently ignore failures.