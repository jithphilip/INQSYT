import os
import streamlit as st
from openai import OpenAI


api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))

if not api_key:
    raise ValueError("GROQ_API_KEY is missing. Add it in Streamlit Cloud Secrets.")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)


def generate_response(query, retrieved_chunks):
    if not retrieved_chunks:
        return "I could not find relevant information."

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
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful customer support assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"LLM API call failed: {str(e)}"
