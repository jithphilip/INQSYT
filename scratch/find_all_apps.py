import os

search_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"
print(f"Searching for python files in {search_dir}...")

for root, dirs, files in os.walk(search_dir):
    if ".git" in root or ".gemini" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "st.title" in content or "import streamlit" in content:
                        print(f"Found Streamlit app: {path}")
            except Exception:
                pass
