import subprocess

def main():
    ps_cmd = (
        'Get-ScheduledTask | '
        'Where-Object {$_.TaskPath -eq "\\" -and $_.State -ne "Disabled"} | '
        'ForEach-Object { '
        '  Write-Output "======================================="; '
        '  Write-Output ("TaskName: " + $_.TaskName); '
        '  Write-Output "--- Actions ---"; '
        '  $_.Actions | Format-List | Out-String; '
        '  Write-Output "--- Triggers ---"; '
        '  $_.Triggers | Format-List | Out-String '
        '} | Out-File -FilePath "scratch/task_details_raw.txt" -Encoding utf8'
    )
    
    try:
        # Run without capture_output so Python doesn't try to decode CP949 stdout
        subprocess.run(["powershell", "-Command", ps_cmd], check=True)
        print("Successfully wrote details to scratch/task_details_raw.txt")
    except Exception as e:
        print("Error executing PowerShell:", e)

if __name__ == '__main__':
    main()
