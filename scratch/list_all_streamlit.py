import subprocess

print("Querying all processes containing 'streamlit' in their name...")
try:
    cmd = 'powershell "Get-Process -Name *streamlit* -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, Path"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(res.stdout)
except Exception as e:
    print(f"Error querying processes: {e}")
