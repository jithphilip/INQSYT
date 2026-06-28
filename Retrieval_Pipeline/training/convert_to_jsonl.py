import os
import json
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(CURRENT_DIR, "Chunks.csv")
JSONL_PATH = os.path.join(CURRENT_DIR, "Chunks.jsonl")

def convert_csv_to_jsonl():
    if not os.path.exists(CSV_PATH):
        print(f"Error: Chunks.csv not found at {CSV_PATH}")
        return

    print(f"Loading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    print("Converting to JSON Lines format (with NO intent labels)...")
    records_converted = 0
    
    with open(JSONL_PATH, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            chunk_id = row.get("chunk_id")
            chunk_title = row.get("chunk_title")
            source_file = row.get("source_file")
            chunk_text = row.get("chunk") if pd.notna(row.get("chunk")) else row.get("chunk_text")
            
            chunk_str = str(chunk_text) if pd.notna(chunk_text) else ""
            is_table = "|" in chunk_str and ("---" in chunk_str or "---|---" in chunk_str)
            chunk_type = "table" if is_table else "text"
            
            # Record structure with NO intent labels
            record = {
                "chunk_id": chunk_id if pd.notna(chunk_id) else None,
                "chunk_title": chunk_title if pd.notna(chunk_title) else None,
                "source_file": source_file if pd.notna(source_file) else None,
                "chunk": chunk_str,
                "metadata": {
                    "chunk_type": chunk_type,
                    "table_markdown": chunk_str if is_table else None
                }
            }
            
            # Write as serialized JSON line
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            records_converted += 1
            
    print(f"Successfully converted {records_converted} records to {JSONL_PATH}!")

if __name__ == "__main__":
    convert_csv_to_jsonl()
