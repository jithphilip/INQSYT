import subprocess

print("Querying all Python processes...")
try:
    cmd = 'powershell "Get-Process -Name *python* -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, Path"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(res.stdout)
except Exception as e:
    print(f"Error querying processes: {e}")
