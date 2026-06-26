import os

ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
raw_data_dir = os.path.join(ws_dir, "raw_data")

matches = []
for root, dirs, files in os.walk(raw_data_dir):
    for file in files:
        if file.endswith(".md"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if "topics" in line.lower() or "following" in line.lower():
                            matches.append((os.path.relpath(file_path, raw_data_dir), line.strip()))
            except Exception:
                pass

print(f"Total matching lines: {len(matches)}")
for rel_path, line in matches[:30]:
    print(f"- {rel_path}: {line}")
