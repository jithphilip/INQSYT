---
description: 
---

---
name: page-level-taxonomy-iteration
description: Execute one complete taxonomy extraction, curation, approval, validation and persistence iteration.
---

# Workflow

## Required Inputs

- source_url
- remote_address
- candidate_intents_table_file_path
- change_proposal_table_file_path
- human_approval_table_file_path
- final_intents_table_file_path


---

## Step 1 — Collect Required Inputs

Ask the user for each input one by one. For remote address, use mcp.json

Verify that all required inputs are available.

Proceed only after all required inputs have been collected.

---

## Step 2 — Extract Candidate Intents

Execute Skill:

extract-candidate-intents-from-page

Inputs:

- source_url

Expected Output:

- PAGE_INTENT_CANDIDATES

---

## Step 3 — Persist Candidate Intents

Execute Skill:

write-with-git

Inputs:

- PAGE_INTENT_CANDIDATES
- candidate_intents_table_file_path
- append = true

---

## Step 4 — Generate Taxonomy Change Proposals

Execute Skill:

review-candidate-intents-from-page

Inputs:

- source_url
- PAGE_INTENT_CANDIDATES

Expected Output:

- PAGE_INTENT_CHANGE_PROPOSALS
- STEP_1_CHECKS

---

## Step 5 — Persist Change Proposals

Execute Skill:

write-with-git

Inputs:

- PAGE_INTENT_CHANGE_PROPOSALS
- change_proposal_table_file_path
- append = true

---

## Step 6 — Human Approval

Present every taxonomy change proposal.

Request explicit approval or rejection for every proposal.

Record all approvals and rejections.

---

## Step 7 — Persist Human Decisions

Execute Skill:

write-with-git

Inputs:

- Human Approval Table
- human_approval_table_file_path
- append = true

---

## Step 8 — Finalize Taxonomy

Execute Skill:

finalise-intents-from-page

Inputs:

- PAGE_INTENT_CANDIDATES
- PAGE_INTENT_CHANGE_PROPOSALS
- Human Approval Table

Expected Output:

- PAGE_INTENT_FINAL

---

## Step 9 — Persist Final Taxonomy

Execute Skill:

write-with-git

Inputs:

- PAGE_INTENT_FINAL
- final_intents_table_file_path
- append = true

---

## Step 10 — Push Version History

Execute Skill:

write-with-git

Operation:

Execute the Push section from Skill write-with-git to push all local commits to the configured remote repository.

---

# Success Criteria

The workflow succeeds only if:

- Candidate intents were extracted.
- Change proposals were generated.
- Human approvals were collected.
- Final taxonomy was generated.
- Every write operation has been versioned.
- All commits have been successfully pushed.

---

# Failure Conditions

Stop immediately if:

- source page cannot be read
- intent extraction fails
- taxonomy review fails
- human approval is unavailable
- taxonomy validation fails
- file persistence fails
- git commit fails
- git push fails

Never continue after a failed stage.

Never bypass human approval.

Never fabricate evidence.

Never skip versioning after a successful write operation.