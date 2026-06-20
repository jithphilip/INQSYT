import os

desktop = r"c:\Users\Anupam Dasgupta\Desktop"
print(f"Scanning {desktop} for directories containing app.py...")

for entry in os.listdir(desktop):
    full_path = os.path.join(desktop, entry)
    if os.path.isdir(full_path):
        app_path = os.path.join(full_path, "generator_streamlit", "app.py")
        if os.path.exists(app_path):
            print(f"Found project folder: {full_path}")
            # print git branch if possible
            try:
                import subprocess
                res = subprocess.run("git branch", cwd=full_path, shell=True, capture_output=True, text=True)
                print(f"  Git branch: {res.stdout.strip()}")
            except Exception:
                pass
