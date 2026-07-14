@echo off
setlocal
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
set "DOC_VBS=%SCRIPT_DIR%run_doc_manager.vbs"
set "NEWS_VBS=%SCRIPT_DIR%run_news_once.vbs"
set "FLIGHT_VBS=%SCRIPT_DIR%run_flight_alert.vbs"
set "ADMISSION_VBS=%SCRIPT_DIR%run_admission_news.vbs"

echo ===================================================
echo [통합 자동화 봇] 윈도우 작업 스케줄러 자동 등록
echo ===================================================
echo.
echo 다음 6개 자동화 작업을 재등록합니다:
echo 1. 업무 관리 (10:00)
echo 2. 업무 관리 (14:00)
echo 3. 경제 뉴스 (15:15)
echo 4. 오키나와 항공권 알림 (10:00)
echo 5. 오키나와 항공권 알림 (15:00)
echo 6. 대입 정보 (수요일 11:00)
echo.

:: 1. 업무 관리 10시
schtasks /create /tn "DocManager_10AM" /tr "wscript.exe \"%DOC_VBS%\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 10:00 /f

:: 2. 업무 관리 14시
schtasks /create /tn "DocManager_2PM" /tr "wscript.exe \"%DOC_VBS%\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 14:00 /f

:: 3. 경제 뉴스 15:15 (주말 제외)
schtasks /create /tn "DailyNewsSummary" /tr "wscript.exe \"%NEWS_VBS%\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 15:15 /f

:: 4. 항공권 알림 10시
schtasks /create /tn "OkinawaFlightAlert_10" /tr "wscript.exe \"%FLIGHT_VBS%\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 10:00 /f

:: 5. 항공권 알림 15시
schtasks /create /tn "OkinawaFlightAlert_15" /tr "wscript.exe \"%FLIGHT_VBS%\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 15:00 /f

:: 6. 대입 정보 (수요일 11:00)
schtasks /create /tn "AdmissionNews_11AM" /tr "wscript.exe \"%ADMISSION_VBS%\"" /sc weekly /d WED /st 11:00 /f

echo.
echo ===================================================
echo 모든 작업의 등록이 완료되었습니다! 
echo 스케줄러를 확인하시려면 '작업 스케줄러'를 열어 확인하세요.
echo ===================================================
