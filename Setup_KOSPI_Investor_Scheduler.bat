@echo off
rem Setup_KOSPI_Investor_Scheduler.bat
chcp 65001 > nul
echo ==========================================================
echo 📊 KOSPI 시황 및 수급 트래커 작업 스케줄러 등록기
echo ==========================================================
echo.

SET PYTHON_PATH=C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe
SET SCRIPT_PATH=d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\kospi_investor_tracker.py

echo [설정 정보]
echo - Python 경로: %PYTHON_PATH%
echo - 스크립트 경로: %SCRIPT_PATH%
echo - 오전 브리핑 시간: 매주 월~금 오전 10:30
echo - 오후 마감 브리핑 시간: 매주 월~금 오후 03:30 (15:30)
echo.

echo 1. 오전 장중 브리핑 등록 중...
schtasks /create /tn "KOSPI_Investor_Tracker_AM" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" --am" /sc weekly /d MON,TUE,WED,THU,FRI /st 10:30 /f

echo.
echo 2. 오후 마감 브리핑 등록 중...
schtasks /create /tn "KOSPI_Investor_Tracker_PM" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" --pm" /sc weekly /d MON,TUE,WED,THU,FRI /st 15:30 /f

echo.
echo ==========================================================
echo ✅ 등록이 완료되었습니다.
echo - 매주 월요일부터 금요일까지 오전 10시 30분, 오후 3시 30분에
echo   자동으로 실행되어 텔레그램으로 시황 보고서를 발송합니다.
echo - 작동하지 않거나 수정이 필요한 경우 작업 스케줄러에서 
echo   "KOSPI_Investor_Tracker_AM / PM" 작업을 관리하세요.
echo ==========================================================
echo.
pause
