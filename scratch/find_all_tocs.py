import os
import re

ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
raw_data_dir = os.path.join(ws_dir, "raw_data")

matched_files = []
for root, dirs, files in os.walk(raw_data_dir):
    for file in files:
        if file.endswith(".md"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = [line.strip() for line in content.split("\n") if line.strip()]
                    
                    # A typical TOC pattern:
                    # - Starts with page title heading (# Title)
                    # - Followed by brief description (no heading prefix)
                    # - Followed by a list of bullet points (* Topic or - Topic)
                    # - Followed by actual section headings (### or #####)
                    
                    has_bullet_list_at_top = False
                    bullets_found = []
                    heading_seen = False
                    
                    for idx, line in enumerate(lines[:12]):
                        if line.startswith("# "):
                            heading_seen = True
                        elif line.startswith(("*", "-")) and heading_seen:
                            bullets_found.append(line)
                            
                    # If we found at least 3 bullet points early in the document (the first 12 non-empty lines)
                    if len(bullets_found) >= 3:
                        matched_files.append((os.path.relpath(file_path, raw_data_dir), bullets_found))
            except Exception:
                pass

print(f"Total raw pages with a top-level bulleted index/TOC: {len(matched_files)}")
print("\nMatched files and their index contents:")
for path, bullets in matched_files:
    print(f"- {path}")
    print("  Index bullet points:")
    for b in bullets[:6]:
        print(f"    {b}")
    print("-" * 50)
