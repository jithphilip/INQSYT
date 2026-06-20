import os

search_text = "Linked Chunks for Selected Intents"
print(f"Searching C:\\ for '{search_text}'...")

found = False
# Walk through C:\ but skip system/slow dirs
for entry in os.listdir("C:\\"):
    path = os.path.join("C:\\", entry)
    if os.path.isdir(path):
        if entry.lower() in [
            "windows", "program files", "program files (x86)", "programdata", 
            "$recycle.bin", "system volume information", "msocache", "documents and settings"
        ]:
            continue
        print(f"Scanning folder: {path}...")
        for root, dirs, files in os.walk(path):
            exclude_dirs = [".git", ".gemini", "node_modules", "AppData", "env", "venv", ".venv", "__pycache__"]
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith((".py", ".txt")):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            if search_text in f.read():
                                print(f"Found match: {filepath}")
                                found = True
                    except Exception:
                        pass

if not found:
    print("No matches found on C:\\ drive outside system folders.")
