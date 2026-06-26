import os

ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
raw_data_dir = os.path.join(ws_dir, "raw_data")

toc_files = []
for root, dirs, files in os.walk(raw_data_dir):
    for file in files:
        if file.endswith(".md"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                    
                    # Search for headers of subsections in the file
                    headings = [line for line in lines if line.startswith(("#", "###", "#####"))]
                    
                    # Search for bullet points at the beginning of the file (first 15 non-empty lines)
                    bullets = []
                    for line in lines[:15]:
                        if line.startswith(("*", "-")):
                            # clean bullet character
                            bullet_text = line.replace("*", "").replace("-", "").strip().lower()
                            bullets.append(bullet_text)
                            
                    # See if any of the bullet points match our section headings
                    matching_bullets = []
                    for b in bullets:
                        for h in headings:
                            clean_h = h.replace("#", "").strip().lower()
                            # Check for strong match
                            if b in clean_h or clean_h in b:
                                if b not in matching_bullets and len(b) > 5:
                                    matching_bullets.append(b)
                                    
                    if len(matching_bullets) >= 2:
                        toc_files.append((os.path.relpath(file_path, raw_data_dir), matching_bullets))
            except Exception:
                pass

print(f"Total raw files with Table of Contents (TOC) lists: {len(toc_files)}")
for path, matches in toc_files:
    print(f"- {path} (matched {len(matches)} section headers in TOC):")
    print(f"  TOC topics: {matches}")
    print("-" * 50)
