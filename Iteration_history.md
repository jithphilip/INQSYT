# 📈 Iteration History & Experiment Log

> [!NOTE]
> **Nomenclature Legend:**
> - **`ret_v1`**: The base retriever architecture using BGE + Logistic Regression.
> - **`ret_v2`**: The optimized hybrid architecture that uses the BGE + Logistic Regression + Guided LLM Fallback + Cumulative probability routing (Soft-N).

> [!NOTE]
> - Cross-encoder is assumed active by default in all the versions of the retriever architecture except ret_v2_noreranker . The reranker is disabled there, but the underlying structure of BGE + LR + Soft-N + Guided LLM Fallback remains unchanged

---

## ITERATION 1

*Goal: Establish the baseline pipeline with raw chunks and the unaugmented Bitext training data.*

### Data State

- **Chunks Database**: `chunks_v1.jsonl` (Original raw markdown chunks, 188 chunks)
- **Classifier Training Data**: `classifier_training_dataset_v1.csv` (A collection of 4,830 e-commerce customer support queries, primarily derived from the Bitext dataset, used to train the RAG system's Logistic Regression intent classifier.)
- **Evaluation Dataset**: `eval_dataset_v1.csv` (340 queries, 10 per intent)
- **Intent Taxonomy**: intent_schema_v1 , intent_descriptions_v1

### Experiments & Configurations

- **iteration_01_ret_v1_report**: Evaluates the initial hybrid router implementation using basic confidence margins (margin <= 0.35) and the Cross-Encoder to establish the baseline performance.
- **iteration_01_ret_v2_noreranker_report**: Assesses the optimized hybrid routing logic while explicitly disabling the Cross-Encoder reranker to isolate and measure the pure Bi-Encoder vector search accuracy.
- **iteration_01_ret_v2_report**: Evaluates the ultimate optimized pipeline configuration on the Iteration 1 data, which introduced Cumulative Probability Mass Routing (Soft-N) and Classifier-Guided LLM Fallback alongside the Cross-Encoder.

---

## ITERATION 2

*Goal: Try and break the semantic overlap problem by adding more variety to the queries.*

### Data State

- **Chunks Database**: `chunks_v1.jsonl` 
- **Classifier Training Data**: `classifier_training_dataset_v2.csv` (An expanded dataset of 5,145 training queries. Extra 315 queries scraped from Twitter, and labelled using ollama-3.3-70b-versatile model)
- **Evaluation Dataset**: `eval_dataset_v1.csv` (340 queries, 10 per intent)
- **Intent Taxonomy**: intent_schema_v1 , intent_descriptions_v1

### Experiments & Configurations

- **iteration_02_ret_v2_report**: Evaluates the fully optimized end-to-end hybrid retrieval pipeline against the Iteration 2 data state, specifically measuring the impact of the augmented classifier_training_dataset_v2 on overall intent routing accuracy.

### Conclusion

The baseline hybrid retrieval pipeline was firmly established with a ceiling of **90.88%** Hit Rate @ 3. The addition of the Twitter-augmented classifier dataset (`v2`) significantly improved NLU stability across varied linguistic phrasing, proving that the semantic overlap issue was primarily an intent routing bottleneck rather than a vector database problem.
---

## ITERATION 3

*Goal: Optimize the chunk database by compressing noisy boilerplate into clean semantic summaries, merging overlapping topics, and linearizing markdown data to boost Bi-Encoder and Reranker retrieval accuracy.*

### Data State

- **Chunks Database**: `chunks_v1_cleaned.jsonl` (Optimized database: 58 boilerplate table/list chunks rewritten by an LLM subagent into 1-3 sentence keyword-rich semantic summaries. Total chunks: 188)
- **Classifier Training Data**: classifier_training_dataset_v2.csv
- **Evaluation Dataset**: eval_dataset_v1.csv (340 queries, 10 per intent)
- **Intent Taxonomy**: intents_schema_v1 , intent_descriptions_v1

### Experiments & Configurations

- **iteration_03_ret_v2_lin_report.md**: Evaluates the chunks_v1.jsonl (Boilerplate) database using a modified uild_index script that mathematically flattened/linearized the raw markdown into dense text. Maintained 90.88% Hit Rate, proving that adding linearized table data fixed 8 queries but diluted exact FAQ match power for 10 others.
- **iteration_03_ret_v2_final_report.md**: Evaluates the chunks_v1_cleaned.jsonl (Semantic Summaries) database alongside the linearized markdown logic. Hit Rate regressed to 89.41%, proving that combining dense factual tables with high-level generalized semantic summaries artificially dilutes the vector space, dragging down hard keyword-matching accuracy.

### Conclusion

This iteration revealed a critical architectural insight into **vector dilution**. Adding mathematically dense, raw factual tables (via linearization) successfully retrieves keyword-heavy data, but simultaneously dilutes the power of exact-match FAQs within the same chunk due to increased token length. Furthermore, attempting to "help" the embedding model by passing it human-readable semantic summaries (`chunks_v1_cleaned`) backfired, as the generalized language pulled the vector away from exact keyword matches, dropping performance to **89.41%**. The optimal strategy remains `Boilerplate + Linearized Markdown` or discovering a way to isolate FAQ text from Table text.
