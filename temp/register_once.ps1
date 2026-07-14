$Action = New-ScheduledTaskAction -Execute "python" -Argument "g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\monday_briefing.py" -WorkingDirectory "g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "08:30"
Register-ScheduledTask -Action $Action -Trigger $Trigger -TaskName "MondayBriefing_830AM" -User "$env:USERNAME" -Force
