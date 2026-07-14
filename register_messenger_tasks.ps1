# Stop Task
$actionStop = New-ScheduledTaskAction -Execute "taskkill.exe" -Argument "/f /im CoolMessenger.exe /im CoolSubProcess.exe"
$triggerStop = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "16:30"
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
Register-ScheduledTask -TaskName "CoolMessenger_AutoStop" -Action $actionStop -Trigger $triggerStop -Principal $principal -Force

# Start Task
$actionStart = New-ScheduledTaskAction -Execute "C:\Program Files (x86)\CoolMessenger Gentoo\CoolMessenger.exe"
$triggerStart = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "08:30"
Register-ScheduledTask -TaskName "CoolMessenger_AutoStart" -Action $actionStart -Trigger $triggerStart -Principal $principal -Force

Write-Host "스케줄러 등록 완료"
