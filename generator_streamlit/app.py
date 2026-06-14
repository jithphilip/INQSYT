import streamlit as st
from sentence_transformers import CrossEncoder

from retrieval import retrieve
from generator_local import generate_response as generate_response_local
from generator_groq import generate_response as generate_response_groq

st.title("RAG Chatbot Demo : Intent-Based Routing")

# Cache the CrossEncoder reranker loading
@st.cache_resource
def load_reranker():
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

query = st.text_input("Ask a question")

top_k = st.slider(
    "Top K Chunks",
    min_value=1,
    max_value=10,
    value=3
)

if st.button("Generate Response"):

    if not query.strip():
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("Retrieving chunks and generating responses..."):

        # 1. Retrieve candidate chunks using Intent-Guided Bi-Encoder retrieval
        initial_candidates_count = max(15, top_k * 2)
        candidate_results = retrieve(
            query,
            top_k=initial_candidates_count
        )

        # 2. Re-rank candidate chunks using Cross-Encoder directly in the app
        if candidate_results:
            reranker = load_reranker()
            pairs = [[query, res["chunk"]] for res in candidate_results]
            rerank_scores = reranker.predict(pairs)
            
            # Sort candidate results based on score descending
            reranked = sorted(
                zip(candidate_results, rerank_scores),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Apply Dynamic K Thresholding (min_k = top_k, max_k = top_k + 2, margin = 4.0)
            retrieved_chunks = []
            if reranked:
                top_score = reranked[0][1]
                min_k = top_k
                max_k = min(10, top_k + 2)
                for i, (res, rerank_score) in enumerate(reranked[:max_k]):
                    if i < min_k or (top_score - rerank_score) <= 4.0:
                        res["rerank_score"] = float(rerank_score)
                        retrieved_chunks.append(res)
        else:
            retrieved_chunks = []

        # Extract text chunks for the generators
        chunk_strings = [item["chunk"] for item in retrieved_chunks]

        # 3. Call the Groq model using the re-ranked chunks
        response_groq = generate_response_groq(
            query,
            chunk_strings
        )

        # 4. Call the local model using the same re-ranked chunks
        response_local = generate_response_local(
            query,
            chunk_strings
        )

    st.subheader("ollama-3.3-70b-versatile model generated response")
    st.write(response_groq)

    st.subheader("qwen2.5:7b generated response")
    st.write(response_local)

    st.subheader("Top Retrieved Chunks")

    for i, item in enumerate(retrieved_chunks):
        st.markdown(f"### Chunk {i+1} (ID: `{item['chunk_id']}`)")
        st.markdown(f"**Intent Classified:** `{item['intent']}`")
        st.markdown(f"**Vector Similarity (Bi-Encoder):** `{item['score']:.4f}` | **Rerank Score (Cross-Encoder):** `{item['rerank_score']:.4f}`")
        st.write(item["chunk"])
        st.markdown("---")
