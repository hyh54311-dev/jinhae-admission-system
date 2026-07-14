@echo off
setlocal
chcp 65001 >nul

echo ===================================================
echo 📊 코스피/코스닥 시장조치 실시간 감시 봇 등록 (10분 간격)
echo ===================================================
echo.
echo 이 배치 파일은 10분마다 백그라운드에서 지수와 시황을 모니터링하고
echo 사이드카/서킷브레이커 발동 시 텔레그램 알림을 보내주는 봇을
echo 윈도우 작업 스케줄러에 등록합니다.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Setup_KOSPI_Halt_Monitor_Scheduler.ps1"

echo.
echo ===================================================
echo 등록이 완료되었습니다. 아무 키나 누르면 종료합니다.
echo ===================================================
pause >nul
