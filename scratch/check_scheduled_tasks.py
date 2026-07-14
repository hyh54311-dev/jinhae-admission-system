import subprocess
import sys
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def main():
    # Run PowerShell command to list scheduled tasks
    ps_cmd = 'Get-ScheduledTask | Where-Object {$_.TaskPath -eq "\\" -and $_.State -ne "Disabled"} | Select-Object TaskName, State, @{Name="Action";Expression={$_.Actions.Execute + " " + $_.Actions.Argument}} | Format-List'
    
    try:
        res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, encoding='utf-8')
        output = res.stdout
        
        with open("scratch/scheduled_tasks_results.txt", "w", encoding="utf-8") as f:
            f.write(output)
        print("Done. Saved task list to scratch/scheduled_tasks_results.txt")
    except Exception as e:
        print("Error checking scheduled tasks:", e)

if __name__ == '__main__':
    main()
