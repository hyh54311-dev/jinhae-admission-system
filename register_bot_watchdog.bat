@echo off
setlocal
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
set "MAINT_SCRIPT=%SCRIPT_DIR%bot_maintenance.py"
set "TASK_NAME=Antigravity_Bot_Watchdog"

echo ===================================================
echo [Watchdog] 텔레그램 봇 자가 복구 서비스 등록
echo ===================================================
echo.

:: 기존 작업 삭제 (재등록을 위해)
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

:: 작업 등록: 1시간마다 확인
schtasks /create /tn "%TASK_NAME%" /tr "python.exe \"%MAINT_SCRIPT%\"" /sc hourly /mo 1 /ru "%USERNAME%" /f

:: 작업 등록: 로그온 시 확인 (추가)
schtasks /create /tn "%TASK_NAME%_Logon" /tr "python.exe \"%MAINT_SCRIPT%\"" /sc onlogon /ru "%USERNAME%" /f

echo.
echo ✅ 등록 완료: 1시간 간격 및 로그온 시 봇 상태를 감시합니다.
echo.
pause
