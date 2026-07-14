$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "`"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\notify_scholarship.py`""
$trigger = New-ScheduledTaskTrigger -Once -At 10:30am -Date "2026-05-07"
Register-ScheduledTask -TaskName "Antigravity_Scholarship_Reminder" -Action $action -Trigger $trigger -Force
