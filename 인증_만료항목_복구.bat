@echo off
pushd "%~dp0"

echo ======================================================
echo    Google Tasks and Gmail Re-authentication Helper
echo ======================================================
echo.
echo 1. A browser window will open automatically in a few seconds.
echo 2. Please log in with your Google account and click "Allow".
echo 3. Do NOT close this console window until the process finishes.
echo.
echo ------------------------------------------------------
echo [Progress] Running python script...

set PYTHONUTF8=1
python scratch\run_failed_auth.py

echo.
echo ------------------------------------------------------
echo [Finished] All procedures are complete.
echo Press any key to close.
pause >nul
popd
