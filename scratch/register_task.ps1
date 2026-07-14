# PowerShell script to register KOSPI Rebound Detector
$Action = New-ScheduledTaskAction -Execute "C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe" -Argument "`"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\kospi_rebound_detector.py`""
$Trigger = New-ScheduledTaskTrigger -Daily -At 14:30
Register-ScheduledTask -TaskName "KOSPI_Rebound_Detector" -Action $Action -Trigger $Trigger -Force
Write-Host "Task successfully registered in Windows Task Scheduler."
