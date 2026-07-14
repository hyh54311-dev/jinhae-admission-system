@echo off
setlocal
chcp 65001 >nul

echo ===================================================
echo [글로벌 올웨더 봇] 윈도우 작업 스케줄러 등록
echo ===================================================
echo.
echo 이 배치 파일은 매일 미국 주식 정규 운영 시간인 오후 11시 00분에 봇이 자동으로
echo 실행되도록 윈도우 작업 스케줄러에 등록해 줍니다.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Setup_All_Weather_Scheduler.ps1"

echo.
echo ===================================================
echo 등록이 완료되었습니다. 아무 키나 누르면 종료합니다.
echo ===================================================
pause >nul
