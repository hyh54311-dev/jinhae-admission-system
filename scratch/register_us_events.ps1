# PowerShell script to register one-time KOSPI event briefings (optimized for boot triggers after 8:00 AM)
$Python = "C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe"
$Script = "d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\notify_us_events.py"

# Create task settings to run the task as soon as possible if a scheduled start is missed (e.g. PC was off at 8:00 AM)
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable

# 1. Register US_CPI_Briefing for June 11, 2026 at 8:00 AM
$ActionCPI = New-ScheduledTaskAction -Execute $Python -Argument "`"$Script`" --event cpi --task-name US_CPI_Briefing"
$TriggerCPI = New-ScheduledTaskTrigger -Once -At (Get-Date "2026-06-11 08:00:00")
Register-ScheduledTask -TaskName "US_CPI_Briefing" -Action $ActionCPI -Trigger $TriggerCPI -Settings $Settings -Force
Write-Host "Successfully updated 'US_CPI_Briefing' for 2026-06-11 08:00:00 KST (with StartWhenAvailable)."

# 2. Register US_FOMC_Briefing for June 18, 2026 at 8:00 AM
$ActionFOMC = New-ScheduledTaskAction -Execute $Python -Argument "`"$Script`" --event fomc --task-name US_FOMC_Briefing"
$TriggerFOMC = New-ScheduledTaskTrigger -Once -At (Get-Date "2026-06-18 08:00:00")
Register-ScheduledTask -TaskName "US_FOMC_Briefing" -Action $ActionFOMC -Trigger $TriggerFOMC -Settings $Settings -Force
Write-Host "Successfully updated 'US_FOMC_Briefing' for 2026-06-18 08:00:00 KST (with StartWhenAvailable)."
