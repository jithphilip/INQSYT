import json
import faiss
import numpy as np

from sentence_transformers import (
    SentenceTransformer,
    CrossEncoder
)

# -----------------------
# LOAD
# -----------------------

embed_model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

intent_index = faiss.read_index(
    "embeddings/intent_index.faiss"
)

chunk_index = faiss.read_index(
    "embeddings/chunk_index.faiss"
)

with open(
    "embeddings/intent_metadata.json",
    "r"
) as f:
    intents = json.load(f)

with open(
    "embeddings/chunk_metadata.json",
    "r"
) as f:
    chunks = json.load(f)

# Reconstruct precomputed rich chunk embeddings
precomputed_embeddings = chunk_index.reconstruct_n(0, chunk_index.ntotal)
chunk_emb_dict = {
    chunk["chunk_id"]: precomputed_embeddings[i]
    for i, chunk in enumerate(chunks)
}
    
#-------------------- Intent Retreieval --------------------------------------------------------------
    
def retrieve_intents(
    query,
    k=2
):

    query_emb = embed_model.encode(
        [query],
        normalize_embeddings=True
    )

    # Search top 5 candidates first
    faiss_k = max(5, k)
    scores, idx = intent_index.search(
        np.array(query_emb, dtype=np.float32),
        faiss_k
    )

    candidates = [intents[i] for i in idx[0]]

    pairs = []
    for item in candidates:
        queries = item.get("sample_queries", [])
        passage = f"Intent: {item['intent']}. Description: {item['description']}."
        if queries:
            passage += f" Sample queries: {', '.join(queries)}"
        pairs.append((query, passage))

    # Score using reranker
    rerank_scores = reranker.predict(pairs)

    # Sort candidates by rerank score
    ranked = sorted(
        zip(candidates, rerank_scores),
        key=lambda x: x[1],
        reverse=True
    )

    results = []

    for item, score in ranked[:k]:
        results.append(
            {
                "intent": item,
                "score": float(score)
            }
        )

    return results


#---------------- Candidate chunks --------------------------
def get_candidate_chunks(retrieved_intents):

    candidate_ids = set()

    for item in retrieved_intents:

        for chunk_id in item["intent"]["source_chunks"]:
            candidate_ids.add(
                chunk_id
            )

    return candidate_ids

# ------------------ Chunk Retrieval ----------------------------------------------------------
def retrieve_chunks(
    query,
    candidate_ids,
    top_k=15
):

    query_emb = embed_model.encode(
        [query],
        normalize_embeddings=True
    )[0]

    candidates = []

    for chunk in chunks:

        if chunk["chunk_id"] in candidate_ids:

            candidates.append(
                chunk
            )

    if not candidates:
        return []

    # Get pre-computed rich embeddings for the candidates
    candidate_embs = np.array([
        chunk_emb_dict[c["chunk_id"]]
        for c in candidates
    ])

    scores = candidate_embs @ query_emb

    ranked = sorted(
        zip(candidates, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:top_k]


#-------------------- Cross Encoder -------------------------------------------
def rerank_chunks(
    query,
    retrieved_chunks,
    top_k=5
):
    if not retrieved_chunks:
        return []

    pairs = []
    bi_scores = []
    for chunk, bi_score in retrieved_chunks:
        content = chunk.get("content", "")
        path = chunk.get("path", "")
        sample_queries = chunk.get("sample_queries", [])
        retrieval_terms = chunk.get("retrieval_terms", [])
        search_phrases = chunk.get("search_phrases", [])

        passage = f"Content: {content}\nPath: {path}"
        if sample_queries:
            passage += f"\nSample Queries: {', '.join(sample_queries)}"
        if retrieval_terms:
            passage += f"\nRetriever Terms: {', '.join(retrieval_terms)}"
        if search_phrases:
            passage += f"\nCustomer Phrases: {', '.join(search_phrases)}"
        pairs.append((query, passage))
        bi_scores.append(bi_score)

    scores = reranker.predict(
        pairs
    )

    # Convert to numpy arrays for normalization
    bi_scores = np.array(bi_scores)
    cross_scores = np.array(scores)

    # Min-max normalization for bi_scores
    min_bi = np.min(bi_scores)
    max_bi = np.max(bi_scores)
    range_bi = max_bi - min_bi
    norm_bi = (bi_scores - min_bi) / range_bi if range_bi > 0 else np.zeros_like(bi_scores)

    # Min-max normalization for cross_scores
    min_cross = np.min(cross_scores)
    max_cross = np.max(cross_scores)
    range_cross = max_cross - min_cross
    norm_cross = (cross_scores - min_cross) / range_cross if range_cross > 0 else np.zeros_like(cross_scores)

    # Linear combination: Alpha = 0.3 balances Bi-encoder semantic dense matching & CrossEncoder precision
    alpha = 0.3
    combined_scores = alpha * norm_bi + (1 - alpha) * norm_cross

    # Sort retrieved_chunks by combined_scores
    ranked = sorted(
        zip(retrieved_chunks, combined_scores),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:top_k]


# -------------- Main Retreival -------------------------------------
def retrieve(query, top_k=5):

    intents = retrieve_intents(
        query,
        k=3
    )

    candidate_ids = get_candidate_chunks(
        intents
    )

    chunks = retrieve_chunks(
        query,
        candidate_ids,
        top_k=15
    )

    reranked = rerank_chunks(
        query,
        chunks,
        top_k=top_k
    )

    return reranked