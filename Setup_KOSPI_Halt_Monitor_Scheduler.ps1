# Setup_KOSPI_Halt_Monitor_Scheduler.ps1
# 이 스크립트는 매일 오전 8시 50분부터 10분 간격으로 코스피/코스닥 서킷브레이커 및 사이드카 상태를 감시하는 봇을 등록합니다.
# 컴퓨터 사용에 전혀 방해가 되지 않도록 백그라운드 전용인 pythonw.exe를 이용하여 실행됩니다.

$ScriptPath = Join-Path $PSScriptRoot "kospi_halt_monitor.py"
if (-not (Test-Path $ScriptPath)) {
    Write-Error "kospi_halt_monitor.py 파일을 찾을 수 없습니다."
    exit
}

# 1. 실행할 파이썬 명령어 설정 (콘솔 창이 전혀 나타나지 않는 pythonw.exe 사용)
$PythonWExe = "C:\Users\admin\AppData\Local\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonWExe)) {
    # pythonw.exe가 해당 경로에 없으면 기본 경로에서 찾음
    $PythonWExe = "pythonw.exe"
}

$action = New-ScheduledTaskAction -Execute $PythonWExe -Argument "`"$ScriptPath`""

# 2. 매일 오전 8시 50분에 시작하는 기본 트리거 정의
$trigger = New-ScheduledTaskTrigger -Daily -At "08:50"

# 3. 10분 간격으로 무한 반복하도록 설정 (Duration은 약 10년으로 설정하여 사실상 무제한 실행)
$tempTrigger = New-ScheduledTaskTrigger -Once -At "08:50" -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Days 3650)
$trigger.Repetition = $tempTrigger.Repetition

# 4. 세부 설정 (배터리 사용 시에도 실행, 절전 모드 해제 불필요 등)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 5. 작업 스케줄러 등록
$TaskName = "KOSPI_Halt_Monitor_Bot"
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force

Write-Host "✅ 코스피/코스닥 사이드카 및 서킷브레이커 감시 봇 등록 완료!"
Write-Host "💡 10분 간격으로 백그라운드(pythonw.exe)에서 자동 실행되며, 특이사항 감지 시에만 텔레그램 알림을 발송합니다."
