def generate_response(query, retrieved_chunks):

    if not retrieved_chunks:
        return "I could not find relevant information."

    context = "\n\n".join(retrieved_chunks)

    response = f"""
Based on the retrieved context, the most relevant information is:

{context}
"""

    return response
