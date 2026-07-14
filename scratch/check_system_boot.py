import subprocess
import sys
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def main():
    ps_cmd = 'Get-CimInstance -ClassName win32_operatingsystem | Select-Object LastBootUpTime | Format-List'
    try:
        res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, encoding='utf-8')
        print("=== System Last Boot Up Time ===")
        print(res.stdout)
    except Exception as e:
        print("Error getting boot time:", e)

if __name__ == '__main__':
    main()
