$ScriptPath = "g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\telegram_assistant.py"
$PythonPath = "C:\Users\요한T\AppData\Local\Programs\Python\Python312\pythonw.exe"

# 1. Register Scheduled Task
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "Antigravity_Telegram_Bot" -Action $Action -Trigger $Trigger -Settings $Settings -Force

Write-Host "✅ Antigravity Telegram Bot registered in Task Scheduler."

# 2. Start the process immediately
Start-Process -FilePath $PythonPath -ArgumentList "`"$ScriptPath`""
Write-Host "🚀 Bot started in background."
