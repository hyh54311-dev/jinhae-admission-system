# Setup_Quant_Scheduler_SchoolPC.ps1
# 이 스크립트는 다음 주 화요일(2026-05-26) 장 마감 직전(15:15)에 봇이 자동 구동되도록 예약합니다.
# 컴퓨터가 꺼져 있다가 켜지는 경우에도 누락된 작업을 즉시 보완 실행하도록 설정합니다.

$ScriptPath = Join-Path $PSScriptRoot "kis_bot_multi.py"
if (-not (Test-Path $ScriptPath)) {
    Write-Error "kis_bot_multi.py 파일을 찾을 수 없습니다."
    exit
}

# 1. 실행할 파이썬 명령어 설정
$PythonExe = "python.exe"
$action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ScriptPath`""

# 2. 다음 리밸런싱 일자 (2026-06-17) 오후 3시 15분으로 트리거 설정
# Get-Date를 사용하여 리밸런싱 날짜와 시간을 명시적으로 지정
$TargetDate = Get-Date -Year 2026 -Month 6 -Day 17 -Hour 15 -Minute 15 -Second 0
$trigger = New-ScheduledTaskTrigger -Once -At $TargetDate

# 3. 중요 설정: 스케줄 시점에 컴퓨터가 꺼져있다가 켜지는 경우 즉시 누락된 작업 실행 (StartWhenAvailable)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# 4. 작업 스케줄러 등록
Register-ScheduledTask -TaskName "KIS_K-DualMomentum_Bot" -Action $action -Trigger $trigger -Settings $settings -Force

Write-Host "✅ 다음 리밸런싱 일자(6월 17일 15:15) 자동매매 봇 예약 완료!"
Write-Host "💡 팁: 컴퓨터가 해당 시간에 꺼져 있더라도, 전원이 켜지는 즉시 자동으로 밀린 작업이 수행됩니다."
