import subprocess

print("Querying running Python processes...")
try:
    cmd = 'powershell "Get-CimInstance Win32_Process -Filter \\"name=\'python.exe\'\\" | Select-Object CommandLine | Format-List"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(res.stdout)
except Exception as e:
    print(f"Error querying processes: {e}")
