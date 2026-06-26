import json
import os

ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
chunks_path = os.path.join(ws_dir, "generator_streamlit", "Chunks.jsonl")

late_delivery_chunks = []
with open(chunks_path, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        source = item.get("source_file", "").lower()
        if "late" in source or "delivery" in source or "deliveries" in source:
            if "late_delivery" in item.get("chunk_id", "") or "late" in item.get("chunk_id", ""):
                late_delivery_chunks.append(item)

print(f"Total chunks found for late deliveries: {len(late_delivery_chunks)}")
for idx, item in enumerate(late_delivery_chunks, 1):
    print(f"{idx}. ID: `{item['chunk_id']}` | Title: {item['chunk_title']}")
    print(f"   Chunk text:\n{item['chunk']}")
    print("-" * 50)
