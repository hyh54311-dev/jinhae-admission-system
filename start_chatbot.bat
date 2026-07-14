@echo off
chcp 65001 >nul
title Jinhae High School Chatbot Launcher
cd /d "%~dp0"

echo --------------------------------------------------
echo [1/2] Checking dependencies...
echo --------------------------------------------------
python -m pip install fastapi uvicorn requests --quiet

echo.
echo --------------------------------------------------
echo [2/2] Starting Chatbot Server...
echo --------------------------------------------------
echo ※ If the browser doesn't open automatically, 
echo   please enter http://localhost:8000 in your browser.
echo --------------------------------------------------

python start_chat.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ⚠️ An error occurred. Please check the message above.
    pause
)
