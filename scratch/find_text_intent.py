import os

search_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
search_text = "check_return_eligibility"

print(f"Searching for '{search_text}' in {search_dir}...")

found = False
for root, dirs, files in os.walk(search_dir):
    if ".git" in root or ".gemini" in root:
        continue
    for file in files:
        if file.endswith((".py", ".md", ".json", ".txt")):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if search_text in content:
                        print(f"Found in: {path}")
                        found = True
            except Exception:
                pass

if not found:
    print("Not found in any text files.")
