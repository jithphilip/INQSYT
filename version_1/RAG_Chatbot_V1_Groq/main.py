import streamlit as st
from sentence_transformers import CrossEncoder

from retrieval import retrieve
from generator_groq import generate_response as generate_response_groq

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="RAG Chatbot Demo",
    layout="wide"
)

st.title("RAG Chatbot Version-1: Demo")

# =====================================================
# LOAD RERANKER (CACHE)
# =====================================================

@st.cache_resource
def load_reranker():
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# =====================================================
# USER INPUTS
# =====================================================

query = st.text_input("Ask a question")

top_k = st.slider(
    "Final Top K Chunks",
    min_value=1,
    max_value=10,
    value=3
)

candidate_pool = st.slider(
    "Initial Retrieval Pool Size",
    min_value=10,
    max_value=50,
    value=20
)

# =====================================================
# GENERATE RESPONSE
# =====================================================

if st.button("Generate Response"):

    if not query.strip():
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("Retrieving, reranking, and generating response..."):

        # -------------------------------------------------
        # STEP 1: RETRIEVE CANDIDATE CHUNKS
        # -------------------------------------------------

        candidate_results = retrieve(
            query,
            top_k=candidate_pool)

        if not candidate_results:
            st.warning("No relevant chunks found.")
            st.stop()

        # -------------------------------------------------
        # STEP 2: LOAD RERANKER
        # -------------------------------------------------

        try:
            reranker = load_reranker()
        except Exception as e:
            st.error(f"Failed to load reranker: {e}")
            st.stop()

        # -------------------------------------------------
        # STEP 3: RERANK
        # -------------------------------------------------

        pairs = [
            [query, item["chunk"]]
            for item in candidate_results
        ]

        rerank_scores = reranker.predict(pairs)

        reranked = sorted(
            zip(candidate_results, rerank_scores),
            key=lambda x: x[1],
            reverse=True
        )

        top_results = reranked[:top_k]

        retrieved_chunks = [
            item["chunk"] for item, score in top_results
        ]

        # -------------------------------------------------
        # STEP 4: GENERATE RESPONSE USING GROQ
        # -------------------------------------------------

        response_groq = generate_response_groq(
            query,
            retrieved_chunks
        )

    # =====================================================
    # OUTPUT
    # =====================================================

    st.subheader("Llama-3.3-70B (Groq) Generated Response")
    st.write(response_groq)

    st.divider()

    st.subheader("Top Retrieved Chunks After Reranking")

    for i, (item, cross_score) in enumerate(top_results):
        chunk = item["chunk"]
        bi_score = item["bi_score"]

        st.markdown(f"### Chunk {i+1}")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Bi-Encoder Score",
                f"{bi_score:.4f}"
            )

        with col2:
            st.metric(
                "Cross-Encoder Score",
                f"{cross_score:.4f}"
            )

        st.write(chunk)

        st.divider()