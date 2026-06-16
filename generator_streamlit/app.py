import streamlit as st
import re
from sentence_transformers import CrossEncoder

from retrieval import retrieve
from generator_local import generate_response as generate_response_local
from generator_groq import generate_response as generate_response_groq

# 1. Page Config
st.set_page_config(
    page_title="INQSYT RAG Intent Router",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: #f8fafc;
}

h1, h2, h3 {
    font-family: 'Outfit', sans-serif;
    color: #0f172a;
    font-weight: 700;
}

/* Header styling */
.header-container {
    background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
    padding: 30px;
    border-radius: 16px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.header-container h1 {
    color: white !important;
    margin: 0;
    font-size: 2.2rem;
}

.header-container p {
    color: #cbd5e1;
    margin: 5px 0 0 0;
    font-size: 1rem;
}

/* Custom Cards */
.card {
    background-color: white;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}

.response-card-groq {
    border-top: 5px solid #6366f1;
}

.response-card-local {
    border-top: 5px solid #14b8a6;
}

.chunk-card {
    border-left: 5px solid #4f46e5;
    background-color: #ffffff;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 15px;
    border-top: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.score-badge-blue {
    background-color: #e0e7ff;
    color: #4338ca;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.85rem;
    display: inline-block;
    margin-right: 10px;
    margin-top: 5px;
}

.score-badge-green {
    background-color: #d1fae5;
    color: #065f46;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.85rem;
    display: inline-block;
    margin-right: 10px;
    margin-top: 5px;
}

.meta-info {
    color: #64748b;
    font-size: 0.85rem;
    margin-top: 8px;
}

.intent-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 6px;
}

.intent-row-active {
    background-color: #ecfdf5;
    border-left: 4px solid #10b981;
}

.intent-row-inactive {
    background-color: #f1f5f9;
    color: #64748b;
}

</style>
""", unsafe_allow_html=True)

# Cache the CrossEncoder reranker loading
@st.cache_resource
def load_reranker():
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# 3. Header Block
st.markdown("""
<div class="header-container">
    <h1>🤖 INQSYT RAG Chatbot Demo</h1>
    <p>Intent-Based Metadata Routing & Dynamic K Retrieval Pipeline</p>
</div>
""", unsafe_allow_html=True)

# 4. Sidebar configuration
with st.sidebar:
    st.subheader("Config Panel")
    top_k = st.slider(
        "Top K Chunks (min_k)",
        min_value=1,
        max_value=10,
        value=3,
        help="Minimum number of chunks to retrieve. Dynamic routing will fetch up to top_k + 2 based on score margins."
    )
    st.markdown("---")
    st.info("💡 **Dynamic K Thresholding** will dynamically pull up to 2 extra chunks if they are within 4.0 points of the top reranked candidate.")

# 5. Main Layout
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("💬 Ask Your Question")
    query = st.text_area("Enter your customer support query:", height=100, placeholder="e.g. My order says delivered but it's not here.")
    btn = st.button("Run Pipeline", type="primary", use_container_width=True)

with col2:
    if btn:
        if not query.strip():
            st.warning("Please enter a valid query.")
        else:
            with st.spinner("Executing RAG Pipeline..."):
                # 1. Retrieve candidate chunks using Intent-Guided Bi-Encoder retrieval
                initial_candidates_count = max(15, top_k * 2)
                retrieval_output = retrieve(
                    query,
                    top_k=initial_candidates_count
                )
                
                candidate_results = retrieval_output["candidate_results"]
                predicted_intents = retrieval_output["predicted_intents"]
                linked_chunks = retrieval_output["linked_chunks"]

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
                    
                    # Apply Dynamic K Thresholding
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

                # 3. Call the models
                response_groq = generate_response_groq(query, chunk_strings)
                response_local = generate_response_local(query, chunk_strings)

            # 6. Display Output Tabs
            tab1, tab2, tab3 = st.tabs(["💬 Assistant Responses", "🎯 Intent Routing & Mappings", "📚 Retrieved Chunks"])
            
            with tab1:
                # Premium layout for generator models
                st.markdown("### 🚀 Generated Responses")
                
                st.markdown('<div class="card response-card-groq">', unsafe_allow_html=True)
                st.markdown("#### ⚡ ollama-3.3-70b-versatile (Groq Cloud)")
                st.write(response_groq)
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown('<div class="card response-card-local">', unsafe_allow_html=True)
                st.markdown("#### 💻 qwen2.5:7b (Local LLM)")
                st.write(response_local)
                st.markdown("</div>", unsafe_allow_html=True)
                
            with tab2:
                st.markdown("### 🎯 Intent Classifier Analysis")
                st.write("Below are the top-5 predicted intents and their classification probability scores:")
                
                for item in predicted_intents:
                    active_class = "intent-row-active" if item["selected"] else "intent-row-inactive"
                    badge_text = "🟢 Selected for Routing" if item["selected"] else "⚪ Not Selected"
                    st.markdown(f"""
                    <div class="intent-row {active_class}">
                        <div><strong>{item['intent']}</strong> (Score: {item['score']:.4f})</div>
                        <div><small>{badge_text}</small></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("### 🔗 Linked Source Chunks (from Intent Schema)")
                st.write("These chunks were unlocked in the metadata pool for BGE vector search based on the routed intent(s):")
                if linked_chunks:
                    seen_linked_cids = set()
                    for item in linked_chunks:
                        if item["chunk_id"] not in seen_linked_cids:
                            seen_linked_cids.add(item["chunk_id"])
                            st.markdown(f"- **Chunk ID:** `{item['chunk_id']}` | **Parent Page:** `{item['source_file']}` (Mapped Intent: `{item['intent']}`)")
                else:
                    st.write("No linked chunks found in the intent schema.")
                    
            with tab3:
                st.markdown("### 📚 Actually Retrieved & Reranked Chunks")
                st.write(f"The pipeline retrieved **{len(retrieved_chunks)}** chunks under the dynamic thresholding parameters:")
                
                if retrieved_chunks:
                    for i, item in enumerate(retrieved_chunks):
                        st.markdown(f"""
                        <div class="chunk-card">
                            <h4 style="margin-top:0; color:#1e1b4b;">Chunk #{i+1}: {item['chunk_title']}</h4>
                            <div>
                                <span class="score-badge-blue">📄 Parent Page: {item['source_file']}</span>
                                <span class="score-badge-blue">🆔 Chunk ID: {item['chunk_id']}</span>
                            </div>
                            <div style="margin-top:8px;">
                                <span class="score-badge-green">📈 Bi-Encoder Score: {item['score']:.4f}</span>
                                <span class="score-badge-green">🔥 Cross-Encoder Rerank: {item['rerank_score']:.4f}</span>
                            </div>
                            <div style="margin-top:15px; background-color:#f8fafc; padding:15px; border-radius:6px; border:1px solid #e2e8f0; font-family:monospace; font-size:0.9rem; white-space:pre-wrap;">{item['chunk_text']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("No chunks retrieved.")
