$ScriptPath = "d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\send_custom_telegram.py"
$PythonExe = "python.exe"

# Action
$action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ScriptPath`""

# Trigger for today (July 16, 2026) at 13:30:00 KST
$TargetDate = Get-Date -Year 2026 -Month 7 -Day 16 -Hour 13 -Minute 30 -Second 0
$trigger = New-ScheduledTaskTrigger -Once -At $TargetDate

# Settings
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Register the task
Register-ScheduledTask -TaskName "Seteuk_Reminder_1330" -Action $action -Trigger $trigger -Settings $settings -Force

Write-Host "SUCCESS: One-time Seteuk reminder task scheduled successfully for $TargetDate."
