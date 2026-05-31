import streamlit as st

from retrieval import retrieve
from generator_local import generate_response as generate_response_local
from generator_groq import generate_response as generate_response_groq

st.title("RAG Chatbot Demo : Model Comparison")

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

        # Retrieve the chunks once for both models
        retrieved_chunks = retrieve(
            query,
            top_k=top_k
        )

        # Call the Groq model
        response_groq = generate_response_groq(
            query,
            retrieved_chunks
        )

        # Call the local model
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
