import subprocess
import os

ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, cwd=ws_dir, shell=True, capture_output=True, text=True)
        print(f"--- Command: {cmd} ---")
        print(res.stdout)
        print("-" * 30)
    except Exception as e:
        print(f"Error: {e}")

run_cmd("git diff generator_streamlit/app.py")
