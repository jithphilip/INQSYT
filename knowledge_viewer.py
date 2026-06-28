import streamlit as st
import json
import pandas as pd
import os

# --- Configuration & Paths ---
st.set_page_config(page_title="Knowledge Base Viewer", layout="wide")
st.title("📚 Knowledge Base Viewer")

WS_DIR = r"C:\Users\Anupam Dasgupta\Desktop\INQSYT"
INTENTS_PATH = os.path.join(WS_DIR, "Main_Data", "Intents", "intents_schema_v2.json")
CHUNKS_PATH = os.path.join(WS_DIR, "Main_Data", "Chunks", "chunks_v2_completed.jsonl")

# --- Data Loading ---
@st.cache_data
def load_data():
    intents_schema = []
    if os.path.exists(INTENTS_PATH):
        with open(INTENTS_PATH, "r", encoding="utf-8") as f:
            intents_schema = json.load(f)
            
    chunks_data = {}
    if os.path.exists(CHUNKS_PATH):
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    chunk = json.loads(line)
                    chunks_data[chunk["chunk_id"]] = chunk
                    
    # Pre-compute intent mapping for fast chunk lookups
    chunk_to_intents = {}
    for intent in intents_schema:
        intent_name = intent.get("intent", "Unknown")
        for cid in intent.get("source_chunks", []):
            if cid not in chunk_to_intents:
                chunk_to_intents[cid] = []
            chunk_to_intents[cid].append(intent_name)
            
    return intents_schema, chunks_data, chunk_to_intents

intents_schema, chunks_data, chunk_to_intents = load_data()

# --- UI Layout ---
st.markdown("### Search the Knowledge Base")
tab1, tab2 = st.tabs(["🔍 Search by Intent", "📄 Search by Chunk ID"])

with tab1:
    st.subheader("Intent Lookup")
    if not intents_schema:
        st.error(f"Could not load intents schema from {INTENTS_PATH}")
    else:
        intent_names = [i["intent"] for i in intents_schema]
        selected_intent = st.selectbox("Select an Intent:", ["-- Select --"] + intent_names)
        
        if selected_intent != "-- Select --":
            intent_data = next((i for i in intents_schema if i["intent"] == selected_intent), None)
            if intent_data:
                # Format for DataFrame
                df_data = {
                    "Intent Name": [intent_data.get("intent", "")],
                    "Description": [intent_data.get("description", "")],
                    "Linked Chunks": [", ".join(intent_data.get("source_chunks", []))]
                }
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
with tab2:
    st.subheader("Chunk Lookup")
    if not chunks_data:
        st.error(f"Could not load chunks from {CHUNKS_PATH}")
    else:
        chunk_id_input = st.text_input("Enter Chunk ID:")
        
        if chunk_id_input:
            chunk = chunks_data.get(chunk_id_input.strip())
            if chunk:
                # Find mapped intents
                mapped_intents = chunk_to_intents.get(chunk_id_input.strip(), [])
                
                # Format structure for DataFrame
                df_data = {
                    "Field": [],
                    "Value": []
                }
                
                # Top level fields
                df_data["Field"].extend(["chunk_id", "chunk_title", "source_file", "chunk_text", "mapped_intents"])
                df_data["Value"].extend([
                    chunk.get("chunk_id", ""),
                    chunk.get("chunk_title", ""),
                    chunk.get("source_file", ""),
                    chunk.get("chunk", ""),
                    ", ".join(mapped_intents) if mapped_intents else "None"
                ])
                
                # Metadata fields
                metadata = chunk.get("metadata", {})
                for k, v in metadata.items():
                    df_data["Field"].append(f"metadata.{k}")
                    if isinstance(v, list):
                        # Truncate very long lists for dataframe view, or join them
                        if k in ["sample_queries", "jargon_synonyms"]:
                            val_str = f"[{len(v)} items] " + ", ".join(v)
                            df_data["Value"].append(val_str)
                        else:
                            df_data["Value"].append(", ".join(map(str, v)))
                    else:
                        df_data["Value"].append(str(v))
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning(f"Chunk ID '{chunk_id_input}' not found in the database.")
