import os

search_dir = r"C:\Users\Anupam Dasgupta"
search_text = "Linked Chunks for Selected Intents"

print(f"Deep searching {search_dir} for '{search_text}'...")

found = False
for root, dirs, files in os.walk(search_dir):
    # Exclude directories that are slow/unrelated
    exclude_dirs = [".git", ".gemini", "AppData", "__pycache__", "node_modules", "env", "venv", ".venv", "313", "Programs"]
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
    print("No matches found anywhere in the user profile directory.")
