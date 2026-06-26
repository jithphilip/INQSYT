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
        metadata = item.get("metadata", {})
        list_markdown = metadata.get("list_markdown", "")
        
        # Check if the chunk text or list markdown contains list links or topic lists
        # Example indicators: "this page contains the following", "topics in this section",
        # or bullet points matching headings of other sections, or index-like structures
        content_lower = chunk_text.lower()
        metadata_str_lower = str(metadata).lower()
        
        # Look for bulleted lists that list sections or links
        lines = chunk_text.split("\n")
        bullet_count = sum(1 for l in lines if l.strip().startswith(("-", "*", "1.", "2.", "3.")))
        
        is_toc = False
        # If it's a list chunk, check if list_markdown contains Table of Contents indicators
        if metadata.get("chunk_type") == "list":
            list_lines = list_markdown.split("\n")
            list_bullet_count = sum(1 for l in list_lines if l.strip().startswith(("-", "*")))
            # Check for header/TOC terms
            if any(term in list_markdown.lower() for term in ["topics", "help topics", "in this section", "related pages", "contains the following"]):
                is_toc = True
                
        # Also check chunk text directly
        if any(term in content_lower for term in ["topics", "in this section", "contains the following", "related pages"]):
            is_toc = True
            
        if bullet_count >= 2 and any(term in content_lower for term in ["help", "page", "section", "topic"]):
            is_toc = True
            
        if is_toc:
            toc_chunks.append((chunk_id, title, chunk_text, list_markdown))

print(f"Total potential Table of Contents/Topic List chunks: {len(toc_chunks)}")
print("\nMatched chunks:")
for idx, (cid, title, text, list_md) in enumerate(toc_chunks, 1):
    print(f"{idx}. ID: `{cid}` | Title: {title}")
    print(f"   Text: \"{text[:150]}...\"")
    if list_md:
        print(f"   List MD Snippet: \"{list_md[:200]}...\"")
    print("-" * 50)
