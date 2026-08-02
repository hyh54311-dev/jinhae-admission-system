@echo off
chcp 65001 >nul
echo 1시간 단위 HWP-PDF 자동 변환 작업을 스케줄러에 등록합니다...

set TASK_NAME="Auto Convert HWP to PDF"
set VBS_PATH="D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\run_hwp_convert.vbs"

:: 기존 작업이 있으면 삭제
schtasks /delete /tn %TASK_NAME% /f >nul 2>&1

:: 작업 등록 (매 60분마다 실행 - VBS 숨김 모드로 실행)
schtasks /create /tn %TASK_NAME% /tr "wscript.exe %VBS_PATH%" /sc minute /mo 60 /f

echo.
echo 등록이 완료되었습니다. 작업 상태를 확인합니다:
schtasks /query /tn %TASK_NAME%
echo.
echo 스크립트를 즉시 1회 백그라운드 테스트 실행하려면 아무 키나 누르세요.
pause
wscript.exe %VBS_PATH%

