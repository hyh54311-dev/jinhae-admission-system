@echo off
REM ==========================================
REM 텔레그램 AI 어시스턴트(커맨드 센터) 시작 스크립트
REM ==========================================

cd /d "%~dp0"

echo 텔레그램 감시 봇을 백그라운드에서 실행합니다...
REM pythonw.exe를 사용하여 콘솔 창이 뜨지 않음 (백그라운드 실행)
start "" pythonw telegram_assistant.py

echo 실행이 완료되었습니다. 창이 곧 닫힙니다.
timeout /t 3 >nul
exit
