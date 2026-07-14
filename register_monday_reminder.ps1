$TaskName = "Antigravity_Monday_Reminder"
$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c start /d `"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder`" python monday_reminder_popup.py"
$Trigger = New-ScheduledTaskTrigger -Once -At "2026-06-29 08:30:00"
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force
Write-Host "Monday reminder task registered successfully."
