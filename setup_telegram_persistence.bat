@echo off
chcp 65001 >nul
set "SCRIPT_PATH=%~dp0telegram_assistant.py"
set "PYTHON_PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python312\pythonw.exe"

echo [Antigravity] 텔레그램 상시 연결 설정을 시작합니다...

:: 기존 작업 삭제 (있는 경우)
schtasks /delete /tn "Antigravity_Bot" /f >nul 2>&1

:: 새로운 작업 등록 (로그온 시 실행, 1분마다 확인하여 꺼져있으면 재실행)
:: 주의: /sc onlogon은 백그라운드 작업에 적합합니다. 
schtasks /create /tn "Antigravity_Bot" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" /sc onlogon /rl highest /f

echo ✅ 작업 스케줄러 등록 완료: 'Antigravity_Bot' (로그온 시 자동 실행)
echo.
echo 🤖 지금 즉시 봇을 실행합니다...
start "" "%PYTHON_PATH%" "%SCRIPT_PATH%"

timeout /t 3 >nul
exit
