# register_jeju_reminder.ps1
# Windows Task Scheduler에 'Jeju_Air_JJIM_Reminder' 등록 스크립트

$service = New-Object -ComObject("Schedule.Service")
$service.Connect()
$root = $service.GetFolder("\")

# 1. 기존 태스크가 있다면 먼저 삭제
try {
    $root.DeleteTask("Jeju_Air_JJIM_Reminder", 0)
    Write-Host "🧹 기존에 등록된 Jeju_Air_JJIM_Reminder 작업을 삭제했습니다."
} catch {}

# 2. 신규 작업 정의 생성
$def = $service.NewTask(0)

# 3. 기본 정보 등록
$def.RegistrationInfo.Description = "제주항공 찜특가 국제선 예매 리마인더 (오전 10시 오픈)"
$def.RegistrationInfo.Author = "Antigravity AI Assistant"

# 4. 핵심 설정 (배터리 제약 해제, PC 깨우기 설정)
$def.Settings.WakeToRun = $true
$def.Settings.StartWhenAvailable = $true
$def.Settings.DisallowStartIfOnBatteries = $false
$def.Settings.StopIfGoingOnBatteries = $false
$def.Settings.Enabled = $true
$def.Settings.AllowDemandStart = $true
$def.Settings.ExecutionTimeLimit = "PT30M" # 30분 뒤 자동 타임아웃

# 5. 트리거 설정 (내일 2026-07-08 오전 09:45에 1회 실행)
# 1 = TASK_TRIGGER_TIME
$trigger = $def.Triggers.Create(1)
$trigger.Id = "OnceTrigger"
$trigger.StartBoundary = "2026-07-08T09:45:00"

# 6. 실행 액션 설정
$action = $def.Actions.Create(0) # 0 = TASK_ACTION_EXEC
$action.Path = "powershell.exe"

$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Get-Location }
$triggerAlertPath = Join-Path $scriptDir "trigger_alert.ps1"

# 전달할 인자 정의 (경로 공백 대비 큰따옴표 처리 및 인코딩 깨짐을 방지하기 위한 유니코드 문자열 처리 대신 직접 인자 전달)
$title = "제주항공 찜특가 알림"
$message = "선생님! 잠시 후 10시부터 제주항공 찜특가 국제선 예매가 시작됩니다. 미리 로그인하여 대비하세요!"

$action.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$triggerAlertPath`" -Title `"$title`" -Message `"$message`""

# 7. 태스크 등록
# 6 = TASK_CREATE_OR_UPDATE
# 3 = TASK_LOGON_INTERACTIVE_TOKEN (대화형 GUI 창 표시를 위해 반드시 현재 로그인 세션 권한으로 등록)
$root.RegisterTaskDefinition("Jeju_Air_JJIM_Reminder", $def, 6, $null, $null, 3)

Write-Host "`n✅ Jeju_Air_JJIM_Reminder 작업이 윈도우 스케줄러에 등록되었습니다!"
Write-Host "📅 스케줄: 2026-07-08 오전 09:45 1회 실행 (화면 팝업 표시)"
