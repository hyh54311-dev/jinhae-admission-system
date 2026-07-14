$Workspace = "d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
$TelegramScript = Join-Path $Workspace "scratch\send_telegram_reminder.py"
$PopupScript = Join-Path $Workspace "scratch\show_gcp_reminder_popup.py"

# Find pythonw.exe and python.exe
$PythonExe = "C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe"
if (-not (Test-Path $PythonExe)) { $PythonExe = "python.exe" }

$PythonWExe = "C:\Users\admin\AppData\Local\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonWExe)) { $PythonWExe = "pythonw.exe" }

# Define two actions
$action1 = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$TelegramScript`""
$action2 = New-ScheduledTaskAction -Execute $PythonWExe -Argument "`"$PopupScript`""

# Trigger for tomorrow (June 18, 2026) at 10:30:00 AM KST
$TargetDate = Get-Date -Year 2026 -Month 6 -Day 18 -Hour 10 -Minute 30 -Second 0
$trigger = New-ScheduledTaskTrigger -Once -At $TargetDate

# Settings
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Register the task with multiple actions (both Telegram & Popup)
Register-ScheduledTask -TaskName "GCP_Rebalance_Reminder" -Action $action1, $action2 -Trigger $trigger -Settings $settings -Force

Write-Host "SUCCESS: GCP Rebalance Reminder task scheduled for $TargetDate."
