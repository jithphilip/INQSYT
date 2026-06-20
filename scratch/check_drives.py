import subprocess

print("Querying logical drives...")
try:
    cmd = 'powershell "Get-PSDrive -PSProvider FileSystem | Select-Object Name, Root"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(res.stdout)
except Exception as e:
    print(f"Error querying drives: {e}")
