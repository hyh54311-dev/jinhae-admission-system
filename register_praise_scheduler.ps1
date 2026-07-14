# register_praise_scheduler.ps1
# 이 스크립트는 매일 오후 4시 30분(16:30)에 학부모에게 칭찬 알림 문자를 일괄 전송하는 스케줄러를 윈도우 작업 스케줄러에 등록합니다.

$ScriptPath = Join-Path $PSScriptRoot "send_praise_sms.py"
if (-not (Test-Path $ScriptPath)) {
    Write-Error "send_praise_sms.py 파일을 찾을 수 없습니다."
    exit
}

# 1. 실행할 파이썬 실행 파일 설정 (Playwright 실행에 안정적인 python.exe 사용)
$PythonExe = "C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python.exe"
}

$action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ScriptPath`""

# 2. 매일 오후 4시 30분(16:30)에 작동하는 트리거 정의
$trigger = New-ScheduledTaskTrigger -Daily -At "16:30"

# 3. 세부 설정 (배터리 사용 시에도 동작, 절전 모드 해제 불필요 등)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 4. 작업 스케줄러 등록
$TaskName = "Jinhae_High_School_Praise_SMS_Scheduler"
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force

Write-Host "✅ 진해고등학교 학부모 칭찬 알림 자동 발송 스케줄러 등록 완료!"
Write-Host "💡 매일 오후 4시 30분에 백그라운드에서 자동 가동되어 미발송된 칭찬 메시지를 일괄 전송합니다."
