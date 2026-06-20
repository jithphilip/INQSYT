import subprocess
import os

ws_dir = r"c:\Users\Anupam Dasgupta\Desktop\INQSYT"

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, cwd=ws_dir, shell=True, capture_output=True, text=True)
        print(f"--- Command: {cmd} ---")
        print("STDOUT:")
        print(res.stdout)
        print("STDERR:")
        print(res.stderr)
        print("-" * 30)
    except Exception as e:
        print(f"Error running command {cmd}: {e}")

run_cmd("git status")
run_cmd("git log -n 3 --oneline")
