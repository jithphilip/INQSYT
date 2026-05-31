import streamlit as st
from sentence_transformers import CrossEncoder

from retrieval import retrieve
from generator_local import generate_response as generate_response_local
from generator_groq import generate_response as generate_response_groq

st.title("RAG Chatbot Demo : Metadata included")

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

        # 1. Retrieve a wider pool of candidate chunks using the Bi-Encoder in retrieval.py
        initial_candidates_count = max(15, top_k * 2)
        candidate_chunks = retrieve(
            query,
            top_k=initial_candidates_count
        )

        # 2. Re-rank candidate chunks using Cross-Encoder directly in the app
        if candidate_chunks:
            reranker = load_reranker()
            pairs = [[query, chunk] for chunk in candidate_chunks]
            rerank_scores = reranker.predict(pairs)
            
            # Sort candidate chunks based on score descending
            reranked = sorted(
                zip(candidate_chunks, rerank_scores),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Extract the top_k elements after re-ranking
            retrieved_chunks = [chunk for chunk, score in reranked[:top_k]]
        else:
            retrieved_chunks = []

        # 3. Call the Groq model using the re-ranked chunks
        response_groq = generate_response_groq(
            query,
            retrieved_chunks
        )

        # 4. Call the local model using the same re-ranked chunks
        response_local = generate_response_local(
            query,
            retrieved_chunks
        )

    st.subheader("ollama-3.3-70b-versatile model generated response")
    st.write(response_groq)

    st.subheader("qwen2.5:7b generated response")
    st.write(response_local)

    st.subheader("Top Retrieved Chunks")

    for i, chunk in enumerate(retrieved_chunks):
        st.markdown(f"### Chunk {i+1}")
        st.write(chunk)
