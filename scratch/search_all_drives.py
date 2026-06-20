import os

search_dir = r"C:\Users\Anupam Dasgupta"
search_text = "Linked Chunks for Selected Intents"

print(f"Searching C:\\Users\\Anupam Dasgupta for files containing '{search_text}'...")

found = False
# Search up to depth of 4 to keep it fast, but target common folders first
target_dirs = [
    r"C:\Users\Anupam Dasgupta\Desktop",
    r"C:\Users\Anupam Dasgupta\Downloads",
    r"C:\Users\Anupam Dasgupta\Documents",
    r"C:\Users\Anupam Dasgupta\source",
    r"C:\Users\Anupam Dasgupta\repos"
]

for base_dir in target_dirs:
    if not os.path.exists(base_dir):
        continue
    for root, dirs, files in os.walk(base_dir):
        if ".git" in root or ".gemini" in root or "AppData" in root:
            continue
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
    print("No matches found in common user directories.")
