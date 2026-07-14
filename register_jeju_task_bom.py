import os
import subprocess

def main():
    script_dir = os.path.abspath(os.path.dirname(__file__))
    trigger_alert_path = os.path.join(script_dir, "trigger_alert.ps1")
    temp_ps1_path = os.path.join(script_dir, "scratch", "register_jeju_reminder_temp.ps1")
    
    # Ensure scratch directory exists
    os.makedirs(os.path.dirname(temp_ps1_path), exist_ok=True)
    
    ps_code = f"""# Unicode-safe PowerShell script to register task
$service = New-Object -ComObject("Schedule.Service")
$service.Connect()
$root = $service.GetFolder("\\")

try {{
    $root.DeleteTask("Jeju_Air_JJIM_Reminder", 0)
    Write-Host "Removed existing task."
}} catch {{}}

$def = $service.NewTask(0)
$def.RegistrationInfo.Description = "제주항공 찜특가 국제선 대만(타이베이/가오슝) 2월 항공권 예매 알림"
$def.RegistrationInfo.Author = "Antigravity AI Assistant"

$def.Settings.WakeToRun = $true
$def.Settings.StartWhenAvailable = $true
$def.Settings.DisallowStartIfOnBatteries = $false
$def.Settings.StopIfGoingOnBatteries = $false
$def.Settings.Enabled = $true
$def.Settings.AllowDemandStart = $true
$def.Settings.ExecutionTimeLimit = "PT30M"

# Trigger for 2026-07-08 at 09:45:00
$trigger = $def.Triggers.Create(1) # 1 = TASK_TRIGGER_TIME
$trigger.Id = "OnceTrigger"
$trigger.StartBoundary = "2026-07-08T09:45:00"

$action = $def.Actions.Create(0) # 0 = TASK_ACTION_EXEC
$action.Path = "powershell.exe"

$title = "제주항공 찜특가 알림"
$message = "선생님! 잠시 후 10시부터 제주항공 찜특가 국제선 예매가 시작됩니다. 부산-타이베이/가오슝 2월 항공권 예매를 위해 미리 로그인하여 대비하세요!"

# Absolute path to trigger_alert.ps1
$triggerAlertPath = "{trigger_alert_path}"

$action.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$triggerAlertPath`" -Title `"$title`" -Message `"$message`""

$root.RegisterTaskDefinition("Jeju_Air_JJIM_Reminder", $def, 6, $null, $null, 3)
Write-Host "Successfully registered task."
"""

    # Write as UTF-8 with BOM (utf-8-sig) to ensure Windows PowerShell parses it correctly
    with open(temp_ps1_path, "w", encoding="utf-8-sig") as f:
        f.write(ps_code)
        
    print(f"Created temp script: {temp_ps1_path}")
    
    # Run the script using PowerShell
    p = subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", temp_ps1_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = p.communicate()
    
    # Decode using cp949 for Korean system
    try:
        decoded_out = stdout.decode('cp949')
    except Exception:
        decoded_out = stdout.decode('utf-8', errors='ignore')
        
    print("STDOUT:")
    print(decoded_out)
    
    if stderr:
        try:
            decoded_err = stderr.decode('cp949')
        except Exception:
            decoded_err = stderr.decode('utf-8', errors='ignore')
        print("STDERR:")
        print(decoded_err)

if __name__ == "__main__":
    main()
