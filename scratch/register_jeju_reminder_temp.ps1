# Unicode-safe PowerShell script to register task
$service = New-Object -ComObject("Schedule.Service")
$service.Connect()
$root = $service.GetFolder("\")

try {
    $root.DeleteTask("Jeju_Air_JJIM_Reminder", 0)
    Write-Host "Removed existing task."
} catch {}

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
$triggerAlertPath = "D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\trigger_alert.ps1"

$action.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$triggerAlertPath`" -Title `"$title`" -Message `"$message`""

$root.RegisterTaskDefinition("Jeju_Air_JJIM_Reminder", $def, 6, $null, $null, 3)
Write-Host "Successfully registered task."
