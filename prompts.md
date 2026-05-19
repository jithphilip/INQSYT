# Reusable Prompt Workflow for Building a Data Preparation + RAG Retrieval + Evaluation Pipeline
These prompts are arranged in the exact logical order you followed during your retrieval task.
You can reuse them for:
•	websites
•	PDFs
•	customer support docs
•	policies
•	legal documents
•	research papers
•	internal company knowledge bases
The workflow goes from:
•	chunking
→ embeddings
→ retrieval
→ reranking
→ evaluation
→ optimization
________________________________________
PHASE 1 — UNDERSTAND THE DATASET
________________________________________
Prompt 1 — Analyze Dataset Structure
I am building a Retrieval-Augmented Generation (RAG) retrieval system.

Here is my dataset/domain:
[DESCRIBE DATASET]

Help me:
1. Understand the document structure
2. Identify logical sections
3. Suggest chunking strategies
4. Suggest metadata fields
5. Suggest possible user query types
6. Identify retrieval challenges
7. Suggest evaluation strategies
________________________________________
PHASE 2 — DOCUMENT PREPARATION
________________________________________
Prompt 2 — Clean and Structure Documents
I have raw content extracted from:
[WEBSITE/PDF/API]

Help me transform it into clean markdown documents suitable for RAG ingestion.

Requirements:
1. Preserve semantic structure
2. Remove noisy UI/navigation text
3. Preserve headings
4. Split into logical documents
5. Retain useful metadata
6. Make documents retrieval-friendly
________________________________________
PHASE 3 — CHUNKING
________________________________________
Prompt 3 — Design Chunking Strategy
I need to chunk documents for a RAG retrieval system.

Dataset type:
[DATASET TYPE]

Help me determine:
1. Optimal chunk size
2. Chunk overlap
3. Semantic chunking strategy
4. Heading-aware chunking
5. Metadata schema
6. Retrieval tradeoffs
7. Best practices for QA retrieval
________________________________________
Prompt 4 — Generate Chunking Code
Generate Python code to:

1. Load markdown/text documents
2. Chunk documents semantically
3. Preserve metadata:
   - chunk_id
   - source_document
   - section_title
4. Save output as chunks.csv

Requirements:
- reusable
- modular
- pandas-based
- VS Code compatible
- production-style
________________________________________
PHASE 4 — QA DATASET CREATION
________________________________________
Prompt 5 — Design Retrieval Evaluation Dataset
I need to create a retrieval evaluation dataset for a RAG system.

Help me generate:
1. Realistic user questions
2. Ground truth chunk mappings
3. Reference answers
4. Ambiguous queries
5. Hard negative examples
6. Multi-hop retrieval examples
7. QA dataset schema
________________________________________
Prompt 6 — Generate QA Dataset Code
Generate Python code to create a QA evaluation dataset from chunks.csv.

Output columns:
- question
- reference_chunk_id
- reference_document
- answer

Requirements:
1. Questions should resemble real user queries
2. Preserve correct chunk mappings
3. Save as qa_dataset.csv
4. Make code reusable
________________________________________
PHASE 5 — RETRIEVAL ARCHITECTURE
________________________________________
Prompt 7 — Design Retrieval Pipeline Architecture
Help me design a semantic retrieval pipeline for RAG.

Requirements:
1. Convert chunks into embeddings
2. Store embeddings in FAISS
3. Use cosine similarity
4. Retrieve top-k chunks
5. Re-rank retrieved chunks
6. Explain each component
7. Explain retrieval flow step-by-step
8. Explain architectural tradeoffs
________________________________________
PHASE 6 — ENVIRONMENT SETUP
________________________________________
Prompt 8 — VS Code Environment Setup
Help me set up a VS Code environment for a RAG retrieval pipeline.

Requirements:
1. Virtual environment setup
2. pip installations
3. requirements.txt
4. Project folder structure
5. Windows-compatible paths
6. Debugging setup
7. Recommended VS Code extensions
8. Best practices
________________________________________
PHASE 7 — EMBEDDINGS
________________________________________
Prompt 9 — Generate Embedding Pipeline
Generate Python code to:

1. Load chunks.csv
2. Generate embeddings using sentence-transformers
3. Normalize embeddings for cosine similarity
4. Save embeddings as .npy
5. Use reusable path handling
6. Add debugging logs
7. Make code modular
________________________________________
PHASE 8 — VECTOR SEARCH
________________________________________
Prompt 10 — Generate FAISS Retrieval Code
Generate Python code for semantic retrieval using FAISS.

Requirements:
1. Load embeddings
2. Use cosine similarity
3. Normalize query embeddings
4. Use IndexFlatIP
5. Retrieve top-k chunks
6. Display similarity scores
7. Preserve metadata
8. Make code reusable
9. Add debugging logs
________________________________________
PHASE 9 — RETRIEVAL OPTIMIZATION
________________________________________
Prompt 11 — Improve Retrieval Recall
My Recall@K is currently:
[CURRENT SCORE]

Target Recall@K:
[TARGET SCORE]

Current setup:
[DESCRIBE PIPELINE]

Suggest improvements that:
1. Improve recall
2. Minimize latency increase
3. Minimize infrastructure complexity
4. Improve embedding quality
5. Improve chunking quality
6. Improve retrieval strategy
7. Improve query tuning
________________________________________
PHASE 10 — QUERY TUNING
________________________________________
Prompt 12 — Optimize Queries for Retrieval Models
I am using the embedding model:
[MODEL NAME]

Help me:
1. Apply proper query instruction tuning
2. Understand model-specific formatting
3. Improve semantic retrieval performance
4. Improve Recall@K
5. Implement query preprocessing
________________________________________
PHASE 11 — RE-RANKING
________________________________________
Prompt 13 — Generate Re-ranking Pipeline
Generate Python code for CrossEncoder reranking.

Requirements:
1. Retrieve top-k candidates using FAISS
2. Re-rank candidates using CrossEncoder
3. Compare retrieval vs reranked results
4. Preserve metadata
5. Add debugging logs
6. Make code reusable
________________________________________
PHASE 12 — EVALUATION
________________________________________
Prompt 14 — Evaluate Bi-Encoder Retrieval
Generate Python code to evaluate ONLY the Bi-Encoder retrieval stage.

Requirements:
1. Evaluate FAISS retrieval directly
2. Do not use reranking
3. Compute:
   - Recall@K
   - Precision@K
   - Hit Rate@K
   - MRR
4. Use cosine similarity
5. Handle chunk IDs correctly
6. Add debugging logs
________________________________________
Prompt 15 — Evaluate Full Retrieval Pipeline
Generate Python code to evaluate a complete RAG retrieval pipeline.

Requirements:
1. FAISS retrieval
2. CrossEncoder reranking
3. Retrieve top-N candidates
4. Return final top-K results
5. Compute:
   - Recall@K
   - Precision@K
   - Hit Rate@K
   - MRR
6. Handle chunk_id mapping correctly
7. Use cosine similarity
8. Add debugging logs
________________________________________
PHASE 13 — FAILURE ANALYSIS
________________________________________
Prompt 16 — Analyze Retrieval Failures
Help me analyze retrieval failures in my RAG pipeline.

I will provide:
1. Query
2. Expected chunk
3. Retrieved chunks

Help me:
1. Diagnose retrieval errors
2. Identify chunking problems
3. Identify embedding limitations
4. Suggest retrieval improvements
5. Suggest reranking improvements
6. Suggest better embedding models
________________________________________
PHASE 14 — MODEL UNDERSTANDING
________________________________________
Prompt 17 — Explain Retrieval Models
Explain the architecture and working of my RAG retrieval pipeline.

Cover:
1. Embedding models
2. Bi-Encoder retrieval
3. FAISS vector search
4. Cosine similarity
5. Query tuning
6. CrossEncoder reranking
7. Evaluation metrics
8. Precision/Recall/MRR
9. Production tradeoffs

Explain in a meeting/presentation-friendly way.
________________________________________
PHASE 15 — ADVANCED OPTIMIZATION
________________________________________
Prompt 18 — Improve Retrieval Without Increasing Complexity
My retrieval pipeline currently achieves:
[CURRENT METRICS]

Help me improve Recall@K without significantly increasing:
1. Latency
2. GPU usage
3. Memory usage
4. Infrastructure complexity

Focus on:
- embedding improvements
- chunking improvements
- retrieval tuning
- reranking optimization
________________________________________
PHASE 16 — FINAL DOCUMENTATION
________________________________________
Prompt 19 — Generate Project Documentation
Generate professional documentation for my RAG retrieval project.

Include:
1. Project overview
2. Dataset description
3. Chunking strategy
4. Embedding pipeline
5. Retrieval architecture
6. FAISS indexing
7. Reranking pipeline
8. Evaluation metrics
9. Results
10. Failure analysis
11. Future improvements
12. Folder structure
13. Installation instructions
________________________________________
RECOMMENDED DEVELOPMENT FLOW
1. Understand dataset
2. Clean documents
3. Chunk documents
4. Generate QA dataset
5. Build embeddings
6. Build vector search
7. Tune retrieval
8. Add reranking
9. Evaluate retriever
10. Evaluate full pipeline
11. Analyze failures
12. Optimize recall
13. Document project
________________________________________
Recommended Reusable Folder Structure
PROJECT/
│
├── data/
│   ├── raw_docs/
│   ├── processed_docs/
│   ├── chunks.csv
│   └── qa_dataset.csv
│
├── embeddings/
│   └── chunk_embeddings.npy
│
├── retrieval/
│   ├── embed_chunks.py
│   ├── retrieve.py
│   ├── rerank.py
│   ├── evaluate_biencoder.py
│   └── evaluate_full_pipeline.py
│
├── notebooks/
│
├── reports/
│
├── requirements.txt
│
└── README.md

