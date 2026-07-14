import subprocess
import sys
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def main():
    # Use wmic or PowerShell to get running processes with command lines
    ps_cmd = 'Get-CimInstance Win32_Process -Filter "name LIKE \'%python%\'" | Select-Object ProcessId, Name, CommandLine | Format-List'
    
    try:
        res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        print("=== Running Python Processes ===")
        print(res.stdout)
    except Exception as e:
        print("Error getting processes:", e)

if __name__ == '__main__':
    main()
