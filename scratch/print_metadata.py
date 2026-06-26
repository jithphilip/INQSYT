import json
import os

ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
chunks_path = os.path.join(ws_dir, "generator_streamlit", "Chunks.jsonl")

ids_to_check = ["late_delivery_007", "report_suspicious_activity_001"]

with open(chunks_path, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        if item.get("chunk_id") in ids_to_check:
            print(f"ID: {item['chunk_id']}")
            print(f"Title: {item['chunk_title']}")
            print(f"Metadata:")
            print(json.dumps(item.get("metadata", {}), indent=2))
            print("=" * 60)
