@echo off
setlocal
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
set "LOG_FILE=%SCRIPT_DIR%telegram_assistant.log"

echo ===================================================
echo [Antigravity] 텔레그램 봇 상태 대시보드
echo ===================================================
echo.

:: 1. 프로세스 확인
tasklist /fi "IMAGENAME eq pythonw.exe" | findstr /i "pythonw.exe" >nul
if %errorlevel% equ 0 (
    echo [상태] ✅ 봇이 현재 백그라운드에서 실행 중입니다.
) else (
    echo [상태] ❌ 봇이 중단되었습니다! (자가 치유 시스템 작동 대기 중)
)

:: 2. 잠금 포트 확인
netstat -ano | findstr :65432 >nul
if %errorlevel% equ 0 (
    echo [포트] ✅ 잠금 포트(65432)가 점유 중입니다 (정상).
) else (
    echo [포트] ⚠️ 잠금 포트가 비어 있습니다 (프로세스 부재).
)

echo.
echo ---------------------------------------------------
echo 최근 5개 로그 기록:
echo ---------------------------------------------------
powershell -command "Get-Content '%LOG_FILE%' -Tail 5"
echo.
echo ===================================================
pause
