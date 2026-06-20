import streamlit as st
import pandas as pd
from sentence_transformers import CrossEncoder
import os
import sys

# Ensure the current directory is in the path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from retrieval import retrieve
from generator_local import generate_response as generate_response_local
from generator_groq import generate_response as generate_response_groq

st.title("RAG Chatbot Demo : Multi-Query Conversational Routing")

# Cache the CrossEncoder reranker loading
@st.cache_resource
def load_reranker():
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Initialize session state variables
if "chat_active" not in st.session_state:
    st.session_state.chat_active = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "latest_query_data" not in st.session_state:
    st.session_state.latest_query_data = None

# Control Buttons at the top
col1, col2 = st.columns(2)
with col1:
    if not st.session_state.chat_active:
        if st.button("Start Chat", use_container_width=True):
            st.session_state.chat_active = True
            st.session_state.messages = []
            st.session_state.latest_query_data = None
            st.rerun()
    else:
        st.button("Start Chat", disabled=True, use_container_width=True)

with col2:
    if st.session_state.chat_active:
        if st.button("End Chat", use_container_width=True):
            st.session_state.chat_active = False
            st.session_state.messages = []
            st.session_state.latest_query_data = None
            st.rerun()
    else:
        st.button("End Chat", disabled=True, use_container_width=True)

st.markdown("---")

if not st.session_state.chat_active:
    st.info("Click **Start Chat** to begin a multi-query conversation session.")
else:
    # Sidebar or slider for Top K
    top_k = st.slider(
        "Top K Chunks",
        min_value=1,
        max_value=10,
        value=3,
        key="top_k_slider"
    )
    
    # Display message history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Input for new query
    if query := st.chat_input("Type your question here..."):
        # Display user message in chat
        with st.chat_message("user"):
            st.markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})
        
        with st.spinner("Retrieving chunks and generating responses..."):
            # 1. Retrieve candidate chunks
            initial_candidates_count = max(15, top_k * 2)
            retrieval_output = retrieve(
                query,
                top_k=initial_candidates_count
            )
            
            candidate_results = retrieval_output["candidate_results"]
            predicted_intents = retrieval_output["predicted_intents"]
            linked_chunks = retrieval_output.get("linked_chunks", [])
            chunk_to_bi_score = retrieval_output.get("chunk_to_bi_score", {})
            all_linked_chunks = retrieval_output.get("all_linked_chunks", [])

            # 2. Re-rank candidate chunks using Cross-Encoder
            chunk_to_rerank_score = {}
            if all_linked_chunks:
                reranker = load_reranker()
                pairs = []
                for item in all_linked_chunks:
                    chunk_text = item["content"]
                    if item["chunk_type"] == "table" and item["table_markdown"]:
                        chunk_text = f"{item['content']}\n\n{item['table_markdown']}"
                    elif item["chunk_type"] == "list" and item["list_markdown"]:
                        chunk_text = item["list_markdown"]
                    formatted_chunk = f"Title: {item['chunk_title']}\nContent: {chunk_text}"
                    pairs.append([query, formatted_chunk])
                
                rerank_scores = reranker.predict(pairs)
                for item, rerank_score in zip(all_linked_chunks, rerank_scores):
                    chunk_to_rerank_score[item["chunk_id"]] = float(rerank_score)
                    
            # Populate rerank_score in candidate_results
            for res in candidate_results:
                res["rerank_score"] = chunk_to_rerank_score.get(res["chunk_id"], 0.0)
                
            # Sort candidate results based on score descending
            reranked = sorted(
                candidate_results,
                key=lambda x: x.get("rerank_score", 0.0),
                reverse=True
            )
            
            # Apply Dynamic K Thresholding (min_k = top_k, max_k = top_k + 2, margin = 4.0)
            retrieved_chunks = []
            if reranked:
                top_score = reranked[0].get("rerank_score", 0.0)
                min_k = top_k
                max_k = min(10, top_k + 2)
                for i, res in enumerate(reranked[:max_k]):
                    score = res.get("rerank_score", 0.0)
                    if i < min_k or (top_score - score) <= 4.0:
                        retrieved_chunks.append(res)

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
            
        # Format response text
        assistant_content = f"""**ollama-3.3-70b-versatile model generated response:**
{response_groq}

**qwen2.5:7b generated response:**
{response_local}"""

        # Display assistant response in chat
        with st.chat_message("assistant"):
            st.markdown(assistant_content)
        st.session_state.messages.append({"role": "assistant", "content": assistant_content})
        
        # Save observability details for the latest query
        st.session_state.latest_query_data = {
            "predicted_intents": predicted_intents,
            "all_linked_chunks": all_linked_chunks,
            "chunk_to_bi_score": chunk_to_bi_score,
            "chunk_to_rerank_score": chunk_to_rerank_score,
            "retrieved_chunks": retrieved_chunks
        }
        
        st.rerun()

    # Render Observability Tables for the latest query (if available)
    if st.session_state.latest_query_data is not None:
        data = st.session_state.latest_query_data
        
        st.markdown("---")
        st.subheader("Intent Predictions and Scores")
        
        # Build intents DataFrame
        intent_rows = []
        for item in data["predicted_intents"]:
            intent_rows.append({
                "intent_id": item["intent_id"],
                "confidence": f"{item['confidence']:.4f}",
                "description": item["description"],
                "is_selected": item["is_selected"],
                "intent_metadata": item["intent_metadata"]
            })
        df_intents = pd.DataFrame(intent_rows)
        st.dataframe(df_intents, use_container_width=True)

        st.subheader("3. chunk retriever")
        
        # Build chunks DataFrame
        selected_chunk_ids = {item["chunk_id"] for item in data["retrieved_chunks"]}
        chunk_rows = []
        for item in data["all_linked_chunks"]:
            cid = item["chunk_id"]
            bi_score = data["chunk_to_bi_score"].get(cid, 0.0)
            rerank_score = data["chunk_to_rerank_score"].get(cid, None)
            
            if rerank_score is not None:
                confidence_str = f"{bi_score:.4f}, {rerank_score:.4f}"
            else:
                confidence_str = f"{bi_score:.4f}, N/A"
                
            is_selected_str = "Yes" if cid in selected_chunk_ids else "No"
            
            # Content preview (includes title)
            content_preview = f"Title: {item['chunk_title']}\n\nContent: {item['content']}"
            if len(content_preview) > 300:
                content_preview = content_preview[:300] + "..."
                
            meta_str = ""
            if item["chunk_type"] == "table" and item["table_markdown"]:
                meta_str = item["table_markdown"]
            elif item["chunk_type"] == "list" and item["list_markdown"]:
                meta_str = item["list_markdown"]
                
            chunk_rows.append({
                "chunk_id": cid,
                "from_intent_id": item["from_intent_id"],
                "parent_page": item["parent_page"],
                "confidence (bi-enc, cross-enc)": confidence_str,
                "is_selected": is_selected_str,
                "content": content_preview,
                "chunk_metadata": meta_str
            })
        df_chunks = pd.DataFrame(chunk_rows)
        st.dataframe(df_chunks, use_container_width=True)

        st.subheader("Top Retrieved Chunks passed to LLM")
        for i, item in enumerate(data["retrieved_chunks"]):
            st.markdown(f"### Chunk {i+1} (ID: `{item['chunk_id']}`)")
            st.markdown(f"**Parent Page:** `{item['source_file']}`")
            st.markdown(f"**Intent Classified:** `{item['intent']}`")
            st.markdown(f"**Vector Similarity (Bi-Encoder):** `{item['score']:.4f}` | **Rerank Score (Cross-Encoder):** `{item['rerank_score']:.4f}`")
            st.write(item["chunk"])
            st.markdown("---")
