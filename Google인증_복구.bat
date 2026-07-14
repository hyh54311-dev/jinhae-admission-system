@echo off
pushd "%~dp0"

echo ======================================================
echo    Antigravity Google Auth Recovery Helper
echo ======================================================
echo.
echo 1. A browser window will open automatically in a few seconds.
echo 2. Please log in with your Google account and click "Allow".
echo 3. Do NOT close this console window until the process finishes.
echo.
echo ------------------------------------------------------
echo [Progress] Running python script...

set PYTHONUTF8=1
python auth_recovery.py

echo.
echo ------------------------------------------------------
echo [Finished] All procedures are complete.
echo If you saw the success message, press any key to close.
pause >nul
popd
