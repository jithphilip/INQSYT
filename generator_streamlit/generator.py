import os
import requests
import streamlit as st


OLLAMA_BASE_URL = st.secrets.get("OLLAMA_URL", os.getenv("OLLAMA_URL"))
OLLAMA_MODEL = st.secrets.get("OLLAMA_MODEL", os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))


def generate_response(query, retrieved_chunks):
    if not retrieved_chunks:
        return "I could not find relevant information."

    if not OLLAMA_BASE_URL:
        return "OLLAMA_URL is missing. Add it in Streamlit Secrets."

    context = "\n\n---\n\n".join(retrieved_chunks)

    prompt = f"""
You are a customer support chatbot.

Answer the user's question using ONLY the provided context.

If the answer is not present in the context, say:
"I don't have enough information to answer that."

Do not make up policies.
Do not mention retrieved chunks.

Context:
{context}

User question:
{query}
"""

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 500
                }
            },
            timeout=180
        )

        response.raise_for_status()
        return response.json()["response"]

    except Exception as e:
        return f"Local Ollama call failed: {str(e)}"
