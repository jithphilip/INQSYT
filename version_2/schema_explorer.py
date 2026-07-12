import json
import os
import pandas as pd
import streamlit as st

# Set page config for a premium wide layout
st.set_page_config(
    page_title="Inqyst Schema Explorer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a sleek, premium design
st.markdown("""
<style>
    /* Main container styling */
    .reportview-container {
        background: #0f1116;
    }
    /* Card design */
    .metric-card {
        background-color: #1e222b;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #2e3440;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-val {
        font-size: 2rem;
        font-weight: 700;
        color: #88c0d0;
    }
    .metric-lbl {
        font-size: 0.9rem;
        color: #d8dee9;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    /* Details section */
    .details-box {
        background-color: #1a1c23;
        border-radius: 8px;
        padding: 24px;
        border-left: 4px solid #88c0d0;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to walk raw_data directory and build filename to relative path mapping
@st.cache_resource
def build_github_mapping():
    mapping = {}
    raw_data_dir = "raw_data"
    if os.path.exists(raw_data_dir):
        for root, dirs, files in os.walk(raw_data_dir):
            for file in files:
                if file.endswith(".md"):
                    rel_dir = os.path.relpath(root, raw_data_dir)
                    if rel_dir == ".":
                        rel_path = file
                    else:
                        rel_path = os.path.join(rel_dir, file).replace("\\", "/")
                    mapping[file] = rel_path
    return mapping

# Helper function to load chunks using robust JSON decoder
@st.cache_data
def load_data():
    # 1. Load intents schema
    with open("embeddings/intent_metadata.json", "r", encoding="utf-8") as f:
        intents = json.load(f)
        
    # 2. Load chunks metadata
    with open("embeddings/chunk_metadata.json", "r", encoding="utf-8") as f:
        raw_chunks = json.load(f)
    
    chunks = []
    for c in raw_chunks:
        path = c.get("path", "")
        parts = path.split("/")
        source_file = parts[-2] if len(parts) >= 2 else "N/A"
        cat_path = " > ".join(parts[:-2]) if len(parts) > 2 else "N/A"
        chunk_title = source_file.replace(".md", "")
        
        tc = {
            "chunk_id": int(c["chunk_id"]),
            "chunk_title": chunk_title,
            "source_file": source_file,
            "chunk": c.get("content", ""),
            "metadata": {
                "category_path": cat_path,
                "jargon_synonyms": c.get("retrieval_terms", []),
                "sample_queries": c.get("sample_queries", []),
                "search_phrases": c.get("search_phrases", [])
            }
        }
        chunks.append(tc)
        
    return intents, chunks

try:
    intents, chunks = load_data()
    github_mapping = build_github_mapping()
except Exception as e:
    st.error(f"Error loading schema files: {e}")
    st.stop()

# Header Section
st.title("🔍 Inqyst V4 Intent & Chunk Schema Explorer")
st.write("Browse and analyze your retrieval database schema, intent definitions, and corresponding document chunks.")

# Metrics row
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown('<div class="metric-card"><div class="metric-val">{}</div><div class="metric-lbl">Total Intents</div></div>'.format(len(intents)), unsafe_allow_html=True)
with m2:
    st.markdown('<div class="metric-card"><div class="metric-val">{}</div><div class="metric-lbl">Total Chunks</div></div>'.format(len(chunks)), unsafe_allow_html=True)
with m3:
    st.markdown('<div class="metric-card"><div class="metric-val">{}</div><div class="metric-lbl">Intents Chunks Mapped</div></div>'.format(
        sum(len(i.get("source_chunks", [])) for i in intents)
    ), unsafe_allow_html=True)

st.markdown("---")

# All Intents Reference Directory
st.subheader("📋 Intents Reference Directory")
intents_table_data = []
for i in intents:
    intents_table_data.append({
        "Intent Name": i["intent"],
        "Description": i["description"],
        "Associated Chunks": ", ".join(map(str, i.get("source_chunks", [])))
    })
df_intents = pd.DataFrame(intents_table_data)
st.dataframe(df_intents, use_container_width=True)

# All Chunks Reference Directory
st.subheader("📋 Chunks Reference Directory")
chunks_table_data = []
for c in chunks:
    source_file = c["source_file"]
    local_path = ""
    if source_file in github_mapping:
        local_path = f"raw_data/{github_mapping[source_file]}"
    
    meta = c.get("metadata", {}) or {}
    cat_path = meta.get("category_path", "")
    
    chunks_table_data.append({
        "Chunk ID": c["chunk_id"],
        "Title": c.get("chunk_title", "N/A"),
        "Source File": source_file,
        "Local Path": local_path,
        "Category Path": cat_path
    })
df_chunks_ref = pd.DataFrame(chunks_table_data)
st.dataframe(
    df_chunks_ref,
    column_config={
        "Local Path": st.column_config.TextColumn("Local Path", width="medium"),
        "Category Path": st.column_config.TextColumn("Category Path", width="medium")
    },
    use_container_width=True
)

st.markdown("---")

# Filters Layout
col1, col2, col3 = st.columns(3)

with col1:
    intent_list = sorted([i["intent"] for i in intents])
    selected_intents = st.multiselect(
        "🎯 Filter by Intent(s)",
        options=intent_list,
        default=[]
    )

with col2:
    chunk_list = sorted(list(set(c["chunk_id"] for c in chunks)))
    selected_chunk_ids = st.multiselect(
        "📄 Filter by Chunk ID(s)",
        options=chunk_list,
        default=[]
    )

with col3:
    source_list = sorted(list(set(c["source_file"] for c in chunks)))
    selected_source_files = st.multiselect(
        "📂 Filter by Source File(s)",
        options=source_list,
        default=[]
    )

# Helper function to convert list of chunks to formatted DataFrame
def make_df(chunk_list):
    table_data = []
    for c in chunk_list:
        meta = c.get("metadata", {}) or {}
        synonyms = ", ".join(meta.get("jargon_synonyms", []))
        queries = "; ".join(meta.get("sample_queries", []))
        cat_path = meta.get("category_path", "")
        
        source_file = c["source_file"]
        local_path = ""
        if source_file in github_mapping:
            local_path = f"raw_data/{github_mapping[source_file]}"
        
        table_data.append({
            "Chunk ID": c["chunk_id"],
            "Title": c.get("chunk_title", "N/A"),
            "Source File": c["source_file"],
            "Local Path": local_path,
            "Category Path": cat_path,
            "Jargon Synonyms": synonyms,
            "Sample Queries": queries,
            "Content": c["chunk"]
        })
    return pd.DataFrame(table_data)

# Filter Logic (Separate DataFrames for each filtering option)
filtered_by_intents = []
if selected_intents:
    allowed_ids = set()
    for i_name in selected_intents:
        intent_obj = [i for i in intents if i["intent"] == i_name][0]
        allowed_ids.update(intent_obj.get("source_chunks", []))
    filtered_by_intents = [c for c in chunks if c["chunk_id"] in allowed_ids]

filtered_by_chunks = []
if selected_chunk_ids:
    filtered_by_chunks = [c for c in chunks if c["chunk_id"] in selected_chunk_ids]

filtered_by_sources = []
if selected_source_files:
    filtered_by_sources = [c for c in chunks if c["source_file"] in selected_source_files]

# Render Results
is_any_filter_active = bool(selected_intents or selected_chunk_ids or selected_source_files)

if not is_any_filter_active:
    # Default View: Show all chunks
    st.subheader(f"📊 Results Table (All Chunks - {len(chunks)} shown)")
    df_all = make_df(chunks)
    st.dataframe(
        df_all,
        column_config={
            "Local Path": st.column_config.TextColumn("Local Path", width="medium"),
            "Content": st.column_config.TextColumn(width="large"),
            "Jargon Synonyms": st.column_config.TextColumn(width="medium"),
            "Sample Queries": st.column_config.TextColumn(width="medium")
        },
        use_container_width=True
    )
else:
    # 1. Display Intent filtering results
    if selected_intents:
        st.markdown("### 🎯 Selected Intent(s) Information")
        for i_name in selected_intents:
            intent_obj = [i for i in intents if i["intent"] == i_name][0]
            st.markdown(f"""
            <div class="details-box" style="border-left-color: #a3be8c; margin-bottom: 15px; padding: 15px 20px;">
                <h5>🎯 Intent: {i_name}</h5>
                <p style="margin-bottom: 5px;"><strong>Description:</strong> {intent_obj.get('description', 'N/A')}</p>
                <p style="margin-bottom: 0;"><strong>Associated Chunks:</strong> {len(intent_obj.get('source_chunks', []))}</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.subheader(f"🎯 Chunks Mapped to Intent(s) ({len(filtered_by_intents)} chunks)")
        if filtered_by_intents:
            st.dataframe(
                make_df(filtered_by_intents),
                column_config={
                    "Local Path": st.column_config.TextColumn("Local Path", width="medium"),
                    "Content": st.column_config.TextColumn(width="large"),
                    "Jargon Synonyms": st.column_config.TextColumn(width="medium"),
                    "Sample Queries": st.column_config.TextColumn(width="medium")
                },
                use_container_width=True
            )
        else:
            st.warning("No chunks found mapped to these intents.")
        st.markdown("---")

    # 2. Display Chunk ID filtering results
    if selected_chunk_ids:
        st.subheader(f"📄 Selected Chunk ID(s) ({len(filtered_by_chunks)} chunks)")
        if filtered_by_chunks:
            st.dataframe(
                make_df(filtered_by_chunks),
                column_config={
                    "Local Path": st.column_config.TextColumn("Local Path", width="medium"),
                    "Content": st.column_config.TextColumn(width="large"),
                    "Jargon Synonyms": st.column_config.TextColumn(width="medium"),
                    "Sample Queries": st.column_config.TextColumn(width="medium")
                },
                use_container_width=True
            )
        else:
            st.warning("No matching chunk IDs found in the database.")
        st.markdown("---")

    # 3. Display Source File filtering results
    if selected_source_files:
        st.subheader(f"📂 Chunks in Selected Source File(s) ({len(filtered_by_sources)} chunks)")
        if filtered_by_sources:
            st.dataframe(
                make_df(filtered_by_sources),
                column_config={
                    "Local Path": st.column_config.TextColumn("Local Path", width="medium"),
                    "Content": st.column_config.TextColumn(width="large"),
                    "Jargon Synonyms": st.column_config.TextColumn(width="medium"),
                    "Sample Queries": st.column_config.TextColumn(width="medium")
                },
                use_container_width=True
            )
            
            # Read and display full local documents immediately below the table
            for sf in selected_source_files:
                if sf in github_mapping:
                    local_path = os.path.join("raw_data", github_mapping[sf])
                    if os.path.exists(local_path):
                        with st.expander(f"📖 Read Full Document: {sf}"):
                            try:
                                with open(local_path, "r", encoding="utf-8") as ffile:
                                    doc_text = ffile.read()
                                st.markdown(doc_text)
                            except Exception as ex:
                                st.error(f"Could not read local file: {ex}")
        else:
            st.warning("No chunks found belonging to these source files.")
        st.markdown("---")

# Dedicated detailed chunk inspector at the end
st.markdown("### 🔍 Dedicated Detailed Chunk Inspector")

# Compile the list of all visible chunk IDs based on active filters
visible_chunks = []
if is_any_filter_active:
    seen_ids = set()
    for i_chunks in [filtered_by_intents, filtered_by_chunks, filtered_by_sources]:
        for c in i_chunks:
            if c["chunk_id"] not in seen_ids:
                seen_ids.add(c["chunk_id"])
                visible_chunks.append(c)
else:
    visible_chunks = chunks

visible_chunk_ids = sorted([c["chunk_id"] for c in visible_chunks])

if visible_chunk_ids:
    # If exactly 1 chunk is visible, default to selecting it. Otherwise, default to placeholder.
    if len(visible_chunk_ids) == 1:
        default_index = 0
        options_list = visible_chunk_ids
    else:
        default_index = 0
        options_list = ["-- Select a Chunk ID to inspect --"] + visible_chunk_ids

    selected_inspect_id = st.selectbox(
        "Select a Chunk ID from the active results to inspect its content, metadata, and full source document:",
        options=options_list,
        index=default_index
    )
    
    inspect_chunk = None
    if selected_inspect_id != "-- Select a Chunk ID to inspect --":
        inspect_chunk = [c for c in chunks if c["chunk_id"] == selected_inspect_id][0]

    if inspect_chunk:
        c = inspect_chunk
        meta = c.get("metadata", {}) or {}
        
        # Determine local file link
        source_file = c["source_file"]
        local_path = ""
        link_html = ""
        if source_file in github_mapping:
            local_path = f"raw_data/{github_mapping[source_file]}"
            link_html = f"<p><strong>Local Path:</strong> <code>{local_path}</code></p>"
        
        st.markdown(f"""
        <div class="details-box">
            <h4>📄 {c.get('chunk_title', 'N/A')} ({c['chunk_id']})</h4>
            <p><strong>Source File:</strong> {c['source_file']}</p>
            {link_html}
            <p><strong>Category Path:</strong> {meta.get('category_path', 'N/A')}</p>
            <hr style="border: 0; border-top: 1px solid #3b4252; margin: 15px 0;">
            <h5>Content</h5>
            <p style="white-space: pre-wrap; font-family: monospace; background: #2e3440; padding: 12px; border-radius: 5px;">{c['chunk']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Read and display the full local document
        if source_file in github_mapping:
            local_path = os.path.join("raw_data", github_mapping[source_file])
            if os.path.exists(local_path):
                with st.expander("📖 Read Full Local Document"):
                    try:
                        with open(local_path, "r", encoding="utf-8") as ffile:
                            doc_text = ffile.read()
                        st.markdown(doc_text)
                    except Exception as ex:
                        st.error(f"Could not read local file: {ex}")
        
        # Display lists or tables if present in metadata
        tab1, tab2, tab3 = st.tabs(["💡 Jargon Synonyms", "❓ Sample Queries", "📋 Formatted View"])
        with tab1:
            st.write(meta.get("jargon_synonyms", []))
        with tab2:
            st.write(meta.get("sample_queries", []))
        with tab3:
            if meta.get("table_markdown"):
                st.markdown("**Table Markdown:**")
                st.markdown(meta["table_markdown"])
            elif meta.get("list_markdown"):
                st.markdown("**List Markdown:**")
                st.markdown(meta["list_markdown"])
            else:
                st.info("No additional structured list or table markdown present for this chunk.")
else:
    st.info("No chunks available to inspect.")
