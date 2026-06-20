import subprocess

print("Checking WSL status...")
try:
    res = subprocess.run("wsl -l -v", shell=True, capture_output=True, text=True)
    print("STDOUT:")
    print(res.stdout)
    print("STDERR:")
    print(res.stderr)
except Exception as e:
    print(f"Error checking WSL: {e}")
