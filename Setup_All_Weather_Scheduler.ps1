# Setup_All_Weather_Scheduler.ps1
# 이 스크립트는 매일 미국 주식 정규 시장 운영 시간인 오후 11시 00분(23:00 KST)에
# 올웨더 자동 적립/리밸런싱 봇이 구동되도록 윈도우 작업 스케줄러에 예약합니다.
# 컴퓨터가 꺼져 있다가 켜지는 경우에도 누락된 작업을 즉시 보완 실행하도록 설정합니다.

$ScriptPath = Join-Path $PSScriptRoot "all_weather_quant_bot.py"
if (-not (Test-Path $ScriptPath)) {
    Write-Error "all_weather_quant_bot.py 파일을 찾을 수 없습니다."
    exit
}

# 1. 실행할 파이썬 명령어 설정
$PythonExe = "python.exe"
$action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ScriptPath`""

# 2. 매일 오후 11시 00분(23:00)으로 트리거 설정 (미국 장 중 실시간 매매 진행)
$trigger = New-ScheduledTaskTrigger -Daily -At "23:00"

# 3. 중요 설정: 컴퓨터가 꺼져있다가 켜지는 경우 즉시 누락된 작업 실행, 배터리 모드 시 차단 방지
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# 4. 작업 스케줄러 등록 (올웨더 전용 서브 계좌 타겟)
Register-ScheduledTask -TaskName "KIS_All_Weather_Quant_Bot" -Action $action -Trigger $trigger -Settings $settings -Force

Write-Host "✅ 글로벌 올웨더 자산배분 자동화 봇 매일 오후 11시 00분 구동 스케줄 등록 완료!"
Write-Host "💡 미국 주식시장 개장 시간(23:00 KST)에 작동하여 실시간으로 정확한 달러 잔액을 확인하고 즉시 매매합니다."
