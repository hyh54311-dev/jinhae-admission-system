@echo off
setlocal
chcp 65001 >nul

echo ===================================================
echo [모의투자 봇] 윈도우 작업 스케줄러 등록 (학교 PC용)
echo ===================================================
echo.
echo 이 배치 파일은 다음 리밸런싱 일자(6월 17일 15:15)에 봇이 자동으로 실행되도록
echo 윈도우 작업 스케줄러에 등록해 줍니다.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Setup_Quant_Scheduler_SchoolPC.ps1"

echo.
echo ===================================================
echo 등록이 완료되었습니다. 아무 키나 누르면 종료합니다.
echo ===================================================
pause >nul
