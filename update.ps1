$service = New-Object -ComObject("Schedule.Service")
$service.Connect()
$root = $service.GetFolder("\")
$task = $root.GetTask("DailyNewsSummary")
$def = $task.Definition

$def.Settings.WakeToRun = $true
$def.Settings.StartWhenAvailable = $true
$def.Settings.DisallowStartIfOnBatteries = $false
$def.Settings.StopIfGoingOnBatteries = $false

$action = $def.Actions.Item(1)
$action.Path = "wscript.exe"
$action.Arguments = "`"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\run_news_hidden.vbs`""

# 4 = TASK_CREATE_OR_UPDATE
# 3 = TASK_LOGON_INTERACTIVE_TOKEN 
# "" (empty string) is used for UserId/Password if not specified for Interactive
$root.RegisterTaskDefinition("DailyNewsSummary", $def, 4, $null, $null, 3)
Write-Host "Task Update Completed Successfully"
