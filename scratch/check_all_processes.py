import subprocess

print("Querying all processes containing 'streamlit' or 'app.py'...")
try:
    cmd = 'powershell "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like \'*streamlit*\' -or $_.CommandLine -like \'*app.py*\' } | Select-Object Name, CommandLine | Format-List"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(res.stdout)
except Exception as e:
    print(f"Error querying processes: {e}")
