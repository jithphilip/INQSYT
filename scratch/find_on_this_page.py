import os

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
                    if "on this page:" in content.lower():
                        matched_files.append(os.path.relpath(file_path, raw_data_dir))
            except Exception:
                pass

print(f"Total raw markdown files with 'On this page:' Table of Contents: {len(matched_files)}")
print("\nFiles found:")
for f in matched_files:
    print(f"- {f}")
