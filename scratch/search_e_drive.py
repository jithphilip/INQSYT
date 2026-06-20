import os

search_dir = r"E:\""
search_text = "Linked Chunks for Selected Intents"

print(f"Searching E:\\ for '{search_text}'...")

found = False
# Walk through E:\ but skip system/slow dirs
for root, dirs, files in os.walk("E:\\"):
    exclude_dirs = [
        "$RECYCLE.BIN", "System Volume Information", ".git", ".gemini", 
        "node_modules", "AppData", "env", "venv", ".venv", "__pycache__"
    ]
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    
    for file in files:
        if file.endswith((".py", ".txt")):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    if search_text in f.read():
                        print(f"Found match: {path}")
                        found = True
            except Exception:
                pass

if not found:
    print("No matches found on E:\\ drive.")
