import json
import os

ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
chunks_path = os.path.join(ws_dir, "generator_streamlit", "Chunks.jsonl")

toc_chunks = []
with open(chunks_path, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        chunk_text = item.get("chunk", "")
        chunk_id = item.get("chunk_id", "")
        title = item.get("chunk_title", "")
        
        # Check if the chunk text is just a list of section headers
        # We look for bullet points that contain page-level index keywords or are very list-heavy
        lines = [l.strip() for l in chunk_text.split("\n") if l.strip()]
        
        # Criteria:
        # - Has a title or introduction
        # - Most of the lines start with a bullet point (*, -)
        # - Contains a list of subtopics or references to other sections
        bullet_lines = [l for l in lines if l.startswith(("*", "-"))]
        
        is_toc_chunk = False
        if len(lines) >= 3 and len(bullet_lines) >= len(lines) - 2:
            # Check if these bullet points match index topics or sections of the page
            if any(term in chunk_text.lower() for term in ["on this page", "following topics", "help topics", "topics in this section"]):
                is_toc_chunk = True
            elif len(bullet_lines) >= 3 and any(len(b) > 10 for b in bullet_lines):
                # If it's a short list of long bullet items, let's include it for manual check
                is_toc_chunk = True
                
        if is_toc_chunk:
            toc_chunks.append(item)

print(f"Total potential Table of Contents chunks: {len(toc_chunks)}")
for idx, item in enumerate(toc_chunks, 1):
    print(f"{idx}. ID: `{item['chunk_id']}` | Title: {item['chunk_title']}")
    print(f"   Source File: {item.get('source_file')}")
    print(f"   Content:\n{item['chunk']}")
    print("=" * 60)
