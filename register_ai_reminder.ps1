# register_ai_reminder.ps1
# Windows Task Scheduler에 'AI_Scholarship_Reminder' 등록 스크립트

$service = New-Object -ComObject("Schedule.Service")
$service.Connect()
$root = $service.GetFolder("\")

# 1. 기존 태스크가 있다면 먼저 깨끗하게 삭제
try {
    $root.DeleteTask("AI_Scholarship_Reminder", 0)
    Write-Host "🧹 기존에 등록된 AI_Scholarship_Reminder 작업을 삭제했습니다."
} catch {}

# 2. 신규 작업 정의 생성
$def = $service.NewTask(0)

# 3. 기본 정보 등록
$def.RegistrationInfo.Description = "2026년 교육대학원연계 AI융합교육 전문과정 선발 공문 확인 정기 리마인더"
$def.RegistrationInfo.Author = "Antigravity AI Assistant"

# 4. 핵심 설정 (배터리 제약 해제, 대기 모드 해제 시 즉시 실행, PC 깨우기 완벽 설정)
$def.Settings.WakeToRun = $true
$def.Settings.StartWhenAvailable = $true  # 컴퓨터가 꺼져 있어 실행을 못했을 경우 다음 날 켜지는 즉시 실행!
$def.Settings.DisallowStartIfOnBatteries = $false # 노트북 배터리 모드에서도 무조건 가동
$def.Settings.StopIfGoingOnBatteries = $false
$def.Settings.Enabled = $true
$def.Settings.AllowDemandStart = $true
$def.Settings.ExecutionTimeLimit = "PT1H" # 1시간 뒤 자동 타임아웃 종료로 꼬임 방지

# 5. 트리거 설정 (매월 첫 번째 월요일 12:30, 6월~12월 한정)
# 5 = TASK_TRIGGER_MONTHLYDOW (Monthly Day of Week)
$trigger = $def.Triggers.Create(5)
$trigger.Id = "MonthlyFirstMondayTrigger"
$trigger.StartBoundary = "2026-06-01T12:30:00" # 6월 1일부터 작동 시작
$trigger.DaysOfWeek = 2     # 2 = 월요일 (Sunday=1, Monday=2, Tuesday=4, Wednesday=8, Thursday=16, Friday=32, Saturday=64)
$trigger.WeeksOfMonth = 1   # 1 = 첫 번째 주
# MonthsOfYear 비트마스크: 6월(32) + 7월(64) + 8월(128) + 9월(256) + 10월(512) + 11월(1024) + 12월(2048) = 4064
$trigger.MonthsOfYear = 4064

# 6. 실행 액션 설정 (WScript를 통해 백그라운드 무점유로 배치 실행 -> 검은 창 깜빡임 제거)
$action = $def.Actions.Create(0) # 0 = TASK_ACTION_EXEC
$action.Path = "wscript.exe"
$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Get-Location }
$vbsPath = Join-Path $scriptDir "run_ai_reminder.vbs"
$action.Arguments = "`"$vbsPath`""

# 7. 태스크 등록
# 6 = TASK_CREATE_OR_UPDATE
# 3 = TASK_LOGON_INTERACTIVE_TOKEN (대화형 GUI 창 표시를 위해 반드시 현재 로그인 세션 권한으로 등록)
$root.RegisterTaskDefinition("AI_Scholarship_Reminder", $def, 6, $null, $null, 3)

Write-Host "`n✅ AI_Scholarship_Reminder 작업이 윈도우 스케줄러에 완벽히 등록되었습니다!"
Write-Host "📅 스케줄: 6월 ~ 12월 매월 첫 번째 월요일 12:30 (꺼져 있을 시 다음 날 켜지면 실행)"
Write-Host "📂 알림 클릭 시 자동 열림 폴더: D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\개인적인 일\2026년 교육대학원연계 AI융합교육 전문과정 교육대상자 선발 추진 계획"
