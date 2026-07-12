# 📋 Iteration 4 Prompts & Pipeline Curation Log

This document records the exact prompts, LLM configurations, and processes used to generate and align the datasets (chunks, intents, mappings, and evaluation set) for this iteration.

---

## 1. Chunk Curation (Metadata Generation)

* **Model**: `meta-llama/llama-4-scout-17b-16e-instruct`
* **Purpose**: Enrichment of Markdown chunks with descriptive metadata (`sample_queries`, `retrieval_terms`, and `search_phrases`) to enhance bi-encoder indexing and retrieval recall.
* **System Prompt**:
```markdown
You are an expert in generating retrieval metadata for a Retrieval-Augmented Generation (RAG) knowledge base.
Your task is to analyze the provided Markdown chunk and generate metadata that improves semantic retrieval.

The Markdown chunk is the ONLY source of truth.

STRICT RULES:
1. DO NOT rewrite, summarize, paraphrase, or modify the chunk.
2. DO NOT infer information that is not explicitly stated or clearly supported by the chunk.
3. DO NOT generate metadata based on outside knowledge.
4. Every generated query or term MUST be answerable using ONLY the information contained in this chunk.
5. If a query requires information from another chunk or another page, DO NOT generate it.
6. Prefer quality over quantity. It is better to generate fewer, highly relevant items than many weak ones.
7. Avoid duplicates and near-duplicates.

GENERATE THE FOLLOWING METADATA:
1. sample_queries: Generate between 5 and 10 realistic customer questions.
   - Every question MUST be fully answerable using ONLY this chunk.
   - Do NOT ask broad questions whose answers require information outside this chunk.
   - Questions should be realistic and naturally phrased.
   - Cover different aspects of the chunk and vary vocabulary/sentence structure.
2. retrieval_terms: Generate between 15 and 30 retrieval terms.
   - Balanced mix of keywords, domain terminology, customer vocabulary, synonyms, alternative phrasings, common abbreviations, equivalent search terms, and important noun phrases.
   - Do NOT introduce new concepts.
3. search_phrases: Generate between 8 and 15 realistic search phrases.
   - Use natural customer language.
   - Noun phrases, action phrases, problem statements.
   - Every phrase must correspond to information that exists in this chunk.

Return ONLY a valid JSON object matching this schema:
{
  "sample_queries": [
    "question 1",
    "question 2"
  ],
  "retrieval_terms": [
    "term 1",
    "term 2"
  ],
  "search_phrases": [
    "phrase 1",
    "phrase 2"
  ]
}
```
* **User Prompt Template**:
```text
Markdown chunk content:

{chunk_content}

Generate the metadata JSON object according to the rules.
```

---

## 2. Intent Metadata Enrichment

* **Model**: `meta-llama/llama-4-scout-17b-16e-instruct`
* **Purpose**: Refining intent descriptions and curating realistic customer support queries to align the NLU classification space.
* **System Prompt**:
```markdown
You are an expert in designing customer support intent taxonomies for a Retrieval-Augmented Generation (RAG) system.
Your task is to enrich the provided intent definition.

The intent name is FINAL and MUST NOT be modified.

STRICT RULES:
1. NEVER modify the intent name.
2. Preserve the original meaning of the description.
3. Refine the description only for clarity, completeness, and realism. Do NOT broaden or narrow the scope.
4. Do NOT merge multiple intents or assume information outside the intent definition.
5. Sample queries must represent genuine customer requests (typed into a support chatbot), not policy wording.
6. Every sample query should clearly belong to this intent and should not naturally fit another intent.
7. Prefer quality over quantity. Keep queries concise, realistic, and mutually diverse.

DESCRIPTION GUIDELINES:
- Refined description should clearly describe the customer goal and major scenarios.
- Concise natural language, 1–3 sentences.
- Avoid implementation details and mentioning internal systems.

SAMPLE QUERY GUIDELINES:
- Generate between 8 and 10 realistic customer questions.
- Vary vocabulary and sentence structure.
- Do NOT generate questions that belong to another intent.

Return ONLY a valid JSON object matching this schema:
{
  "intent": "manage_notifications",
  "description": "Refined description...",
  "sample_queries": [
    "...",
    "..."
  ]
}
```
* **User Prompt Template**:
```text
Intent name: {intent_name}
Original description: {intent_description}

Enrich this intent according to the rules and return ONLY the JSON object.
```

---

## 3. Intent-to-Chunk Mapping

* **Model**: `meta-llama/llama-4-scout-17b-16e-instruct`
* **Purpose**: Mapping the refined intents to relevant supporting chunks.
* **Methodology**: Pre-filtering chunk candidates using `BAAI/bge-small-en-v1.5` (top 20 candidate chunks for each intent by cosine similarity) followed by LLM evaluation.
* **System Prompt**:
```markdown
You are an expert in mapping customer support intents to knowledge base chunks for a Retrieval-Augmented Generation (RAG) system.
Your task is to identify ALL chunk IDs that contain information relevant to answering the given customer intent.

Treat the original markdown content as the ONLY source of truth.

OBJECTIVE:
Select every chunk that satisfies at least one of the following:
• Directly answers one or more of the sample customer questions.
• Contains policy information required to answer the intent.
• Explains rules, conditions, exceptions, eligibility, limitations or procedures related to the intent.
• Provides important supporting information that would be useful when answering the intent.

STRICT RULES:
1. Use ONLY information present in the chunk. Never use outside knowledge.
2. Never infer facts that are not supported by the chunk.
3. Do NOT match based only on broad topical similarity.
4. If a chunk only briefly mentions the topic without providing useful information, do NOT select it.
5. Precision is more important than recall. When uncertain, do NOT include the chunk.

Return ONLY a valid JSON object matching this schema:
{
  "intent": "<intent_name>",
  "chunk_ids": [
    "chunk_id_1",
    "chunk_id_2"
  ]
}
```
* **User Prompt Template**:
```text
Intent Name: {intent_name}
Description: {intent_desc}
Sample Customer Questions:
{intent_queries}

Here are the candidate chunks:
{chunks_str}
Identify which chunk IDs are relevant. Return ONLY the JSON object.
```

---

## 4. Evaluation Dataset Updates (Mathematical Alignment)

* **Model**: `BAAI/bge-small-en-v1.5` (Bi-Encoder)
* **Purpose**: Mapping the evaluation questions in `eval_dataset_v2.csv` to the correct target chunk IDs in `chunks_renewed.json` under intent-routing constraints.
* **Process**:
  1. Retrieve the human-annotated `intent` label for each query.
  2. Query `intent_to_chunk_mapping.json` to get the list of candidate `chunk_ids` allowed for this intent.
  3. Encode the query and each candidate chunk (combining path and content text) using `BAAI/bge-small-en-v1.5`.
  4. Measure cosine similarity and assign the question's `reference_chunk_id` to the chunk with the highest similarity score.
  5. Save results back into `eval_dataset_v2.csv` in-place.
