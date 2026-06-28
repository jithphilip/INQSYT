# Agent Customizations

## 📊 Evaluation Report Formatting Guidelines

Whenever the user asks for an "eval report", "evaluation report", or request report generation for a retrieval pipeline iteration, strictly format and structure it following the template below:

### 1. Title
`# 📊 RAG Evaluation & Failure Analysis Report ([Iteration / Configuration Name])`

### 2. E-to-E Retrieval Performance Overview
Provide a summary table comparing the Hit Rate, MRR, and failed queries across sweeps of K = 1, 3, 5, 7:
| K Value | Hit Rate (Recall@K) | MRR (Mean Reciprocal Rank) | Failed Queries |
| :---: | :---: | :---: | :---: |
| **K = 1** | ... | ... | ... |
| **K = 3** | ... | ... | ... |
| **K = 5** | ... | ... | ... |
| **K = 7** | ... | ... | ... |

### 3. Failure Mode Table (K = 3)
Categorize all failed queries at K = 3 using the three core RAG components:
* **NLU Classifier Misclassification** (NLU Classifier/Logistic Regression)
* **LLM Router Fallback Error** (LLM Router/Few-Shot Fallback)
* **Reranking / Ranking Failure** (Reranker/Cross-Encoder)

Table format:
| Failure Mode | Isolated Component | Impact (Count/%) | Root Cause Analysis | Mitigation Action |
| :--- | :---: | :---: | :--- | :--- |

### 4. Query-by-Query Failure Directory (K = 3)
List each failed query at K = 3 inside a markdown `carousel` block with:
* Expected Intent
* True Chunk ID
* Predicted Intent(s) and routing classification success status
* Top retrieved chunks with their rerank scores
* Isolated component and specific diagnostic root cause explanation

### 5. Comparative Delta Analysis
Provide a brief, explicit summary comparing the current run's metrics and failure distributions to the immediately previous report. Highlight:
* What improved (e.g., specific intents that are now routed correctly).
* What regressed or worsened (e.g., chunks that dropped in rank).
* The direct correlation between the current iteration's changes and these deltas.

# Chunk Display Formatting
Whenever the user asks to see a chunk, always output:
1. The actual JSON structure of the chunk.
2. The actual text content of the chunk (rendered nicely).


# Naming Convention Rule
All evaluation reports MUST strictly adhere to the following naming convention:
iteration_[XX]_ret_v[X]_[optional_modifier]_report.md
- iteration_[XX]: The overarching dataset iteration (e.g.,  1,  2,  3).
- et_v[X]: The retriever architecture version (e.g.,  1 for no reranker,  2 for cross-encoder reranker).
- [optional_modifier]: Any specific tweaks (e.g., 
oreranker, lin for linearized, inal).

# Interactive Chunk Review Workflow
Whenever conducting a manual, chunk-by-chunk human-in-the-loop review of source pages, strictly adhere to a **batched commit strategy**:
1. Process chunks in batches of no more than 5 source pages at a time.
2. Maintain tracking files (e.g., chunk_modify.md, delete_chunks.md, 	rack_sample_query_changes.md) in the workspace or artifacts to mirror the proposed changes.
3. Upon completing a batch, pause the review process and execute a Python script to mathematically commit the tracked changes directly into the target .jsonl database.
4. Clear the conversation context of the applied changes to prevent context window degradation and hallucination before proceeding to the next batch.

# Unified Payload Merging Logic
When you merge a non-table chunk with a table chunk, you still use the Unified Payload structure for the final merged record, but you weave the contents together like this:

1. **Merge all the text into the "chunk" field:** Take the narrative text from both chunks and combine them into a single, flowing explanation. Then, add a brief 1-2 sentence summary of the table right at the end of that text.
Example: You combine the general tax policy (Chunk 1) with the specific calculation rules (Chunk 2). At the bottom of this combined text, you add: "Items shipped to certain US states and territories are subject to tax. See the attached table for the complete list of applicable states."
Why: The embedding model now has the complete context—the policy, the rules, and the knowledge that a list of states exists—all in one perfectly readable vector.

2. **Isolate the raw table in the "table_markdown" field:** Take the raw Markdown table from the second chunk and place it into the "table_markdown" metadata field of your newly merged record. Leave it completely out of the "chunk" field.

The Final Result:
Instead of having one chunk for the policy and a separate, disconnected chunk for the table, you end up with one master database record. When a user asks, "Do I pay tax on an order shipped to Ohio?", the vector model finds the master record because the text summary matches the intent. The LLM then receives the combined text rules and the raw table together, allowing it to correctly apply the rules and confirm that Ohio is on the list.

**For standalone table chunks**, if the chunk field is boilerplate, you replace it personally with a natural language summary of the table.

# HEAD Marker Protocol
Immediately after successfully executing a batch commit script, you MUST append a 'HEAD' marker to the bottom of ALL tracking artifacts (e.g., merge_chunks.md, chunk_modify.md, delete_chunks.md, track_sample_query_changes.md, track_jargon_changes.md). This cleanly demarcates the start of the next batch and ensures that future commit scripts only process data logged *below* this marker.
- For markdown tables, use the format: | **--- [ HEAD ] ---** | **---** | **(Start of Next Commit Batch)** |`n- For standard markdown files, use the format: # --- [ HEAD: Start of Next Batch ] ---`n

# List Flattening Protocol
When a chunk contains `list_markdown` (bullet points or numbered lists), completely DELETE the existing `chunk` text (which often contains hallucinated summaries or boilerplate) and REPLACE it entirely with the raw `list_markdown` string. Markdown lists are linearly structured and embed flawlessly in Bi-Encoder architectures. This must be done for all list type chunks, whether they are being merged with other chunks or kept standalone.

# Mid-Batch Consistency Check Protocol
Midway through every batch (e.g., after logging 2 or 3 pages out of 5), the agent MUST run a Python script to tail the tracking artifacts (`track_jargon_changes.md`, `track_sample_query_changes.md`, `chunk_modify.md`, `merge_chunks.md`) and verify that all new data has been correctly appended *below* the `HEAD` marker. If discrepancies or regex misalignments are found, the agent must halt processing and fix the logs immediately before proceeding.


# Strict Obedience Protocol
You MUST DO EXACTLY WHAT THE USER TELLS YOU TO DO. 
- Do NOT take proactive actions.
- Do NOT jump ahead or assume the next steps.
- Do NOT execute multi-step workflows (like processing multiple batches or advancing to the next page) unless explicitly instructed to do so by the user.
- Wait for explicit, step-by-step instructions before proceeding.

# Strict Sourcing and Communication Protocol
1. You are to give the user source files ONLY from the generated list of remaining Top 17 source files. No deviations and no doing things on your own.

# Strict Obedience Protocol
DO ONLY WHAT I TELL YOU TO FUCKING DO. DONT JUMP AHEAD AND THINK YOU CAN DO WHATEVER THE FUCK YOU WANT



# Strict Obedience Protocol
Go slow.Recheck your logic.DO THINGS EXACTLY AS I SAY IT

# Architecture Preservation Protocol
We are building a production-style Amazon Customer Support RAG system. The architecture is:

**Knowledge Base:** 
- 138 curated chunks.
- Chunk embeddings are generated from retrieval documents consisting of: Title, LLM-generated overview, Original chunk content, Markdown tables (if present), Sample queries, Jargon/synonyms.
- These retrieval documents are embedded using `BAAI/bge-base-en-v1.5` and indexed in FAISS.
- The original chunk content remains the source of truth for answer generation.

**Retrieval Pipeline:**
- Intent routing
- Dense retrieval
- Cross-Encoder reranking
- LLM generation

**Evaluation:**
- Uses Recall@1, Recall@3, Recall@5 and Recall@7.

**Strict Rule:** 
- Preserve this architecture unless explicitly asked to change it. 
- When suggesting improvements, prefer incremental changes over redesigning the system.
- Several architectural decisions have already been experimentally validated (e.g., chunk retrieval documents, reranking pipeline, intent schema). Assume these decisions are fixed and only implement the requested modifications unless explicitly asked for a redesign.

# Workspace Constraints Protocol
- **Archive Directory**: Do NOT read, modify, or interact with the `Archive` directory unless explicitly instructed to do so by the user.
