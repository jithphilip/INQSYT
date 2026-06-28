import streamlit as st

from retrieval import retrieve
from generator_groq import generate_response

st.title("RAG Chatbot Demo : Groq hosted")

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

    with st.spinner("Retrieving chunks and generating response..."):

        retrieved_chunks = retrieve(
            query,
            top_k=top_k
        )

        response = generate_response(
            query,
            retrieved_chunks
        )

    st.subheader("Generated Response")
    st.write(response)

    st.subheader("Top Retrieved Chunks")

    for i, chunk in enumerate(retrieved_chunks):
        st.markdown(f"### Chunk {i+1}")
        st.write(chunk)
