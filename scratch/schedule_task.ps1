$action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c "d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\run_recommend.bat"'
$trigger = New-ScheduledTaskTrigger -Once -At '2026-05-13 08:30:00'
Register-ScheduledTask -TaskName 'MorningCompanyRecommendation' -Action $action -Trigger $trigger -Force
