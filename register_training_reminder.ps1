# register_training_reminder.ps1
# Windows Task Scheduler에 'Training_Registration_Reminder' 등록 스크립트

$service = New-Object -ComObject("Schedule.Service")
$service.Connect()
$root = $service.GetFolder("\")

# 1. 기존 태스크가 있다면 삭제
try {
    $root.DeleteTask("Training_Registration_Reminder", 0)
    Write-Host "🧹 기존에 등록된 Training_Registration_Reminder 작업을 삭제했습니다."
} catch {}

# 2. 신규 작업 정의 생성
$def = $service.NewTask(0)

# 3. 기본 정보 등록
$def.RegistrationInfo.Description = "2026년 정보(AI·SW)교육 역량강화 원격 직무연수 신청 알림"
$def.RegistrationInfo.Author = "Antigravity AI Assistant"

# 4. 핵심 설정 (배터리 제약 해제, 대기 모드 해제 시 즉시 실행, PC 깨우기 설정)
$def.Settings.WakeToRun = $true
$def.Settings.StartWhenAvailable = $true  # PC가 꺼져 있었을 경우 부팅 직후 실행
$def.Settings.DisallowStartIfOnBatteries = $false # 배터리 모드에서도 무조건 가동
$def.Settings.StopIfGoingOnBatteries = $false
$def.Settings.Enabled = $true
$def.Settings.AllowDemandStart = $true
$def.Settings.ExecutionTimeLimit = "PT1H" # 1시간 뒤 자동 타임아웃

# 5. 트리거 설정 (2026년 6월 15일 월요일 오전 8시 30분 단 1회 실행)
# 1 = TASK_TRIGGER_TIME (일회성 시간 트리거)
$trigger = $def.Triggers.Create(1)
$trigger.Id = "OneTimeTrigger"
$trigger.StartBoundary = "2026-06-15T08:30:00"

# 6. 실행 액션 설정 (WScript를 통해 백그라운드 무점유로 실행)
$action = $def.Actions.Create(0) # 0 = TASK_ACTION_EXEC
$action.Path = "wscript.exe"
$vbsPath = "d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\run_training_reminder.vbs"
$action.Arguments = "`"$vbsPath`""

# 7. 태스크 등록
# 6 = TASK_CREATE_OR_UPDATE
# 3 = TASK_LOGON_INTERACTIVE_TOKEN (대화형 GUI 창 표시를 위해 반드시 현재 로그인 세션 권한으로 등록)
$root.RegisterTaskDefinition("Training_Registration_Reminder", $def, 6, $null, $null, 3)

Write-Host "`n✅ Training_Registration_Reminder 작업이 윈도우 스케줄러에 성공적으로 등록되었습니다!"
$nextRun = $root.GetTask("Training_Registration_Reminder").NextRunTime
Write-Host "📅 실행 예정 시각: 2026년 6월 15일 오전 8:30"
Write-Host "🔔 작동 방식: 텔레그램 메시지 발송 + PC 화면에 고대비 다크 테마 알림 팝업창 출력"
