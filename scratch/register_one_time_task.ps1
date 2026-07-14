$ScriptPath = "d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\kis_bot_multi.py"
$PythonExe = "python.exe"

# Create scheduled task action with --force flag to bypass the date check
$action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ScriptPath`" --force"

# Trigger for tomorrow (June 18, 2026) at 09:30:00 AM KST
$TargetDate = Get-Date -Year 2026 -Month 6 -Day 18 -Hour 9 -Minute 30 -Second 0
$trigger = New-ScheduledTaskTrigger -Once -At $TargetDate

# Settings: run immediately if PC was off at 9:30 AM
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Register the task
Register-ScheduledTask -TaskName "KIS_K-DualMomentum_Bot_OneTime" -Action $action -Trigger $trigger -Settings $settings -Force

Write-Host "SUCCESS: One-time task scheduled successfully for $TargetDate."
