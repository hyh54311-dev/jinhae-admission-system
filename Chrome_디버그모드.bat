@echo off
setlocal
chcp 65001 >nul

echo Starting Chrome in Debug Mode...
echo.
echo 1. Chrome will open with a dedicated debug session.
echo 2. Please log in to https://notebooklm.google.com
echo 3. Once logged in, the AI can capture the session.
echo.

set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
start "" "%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\Antigravity_Debug_Session"

echo [OK] Chrome is running.
pause