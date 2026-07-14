@echo off
setlocal
chcp 65001 >nul

:MENU
cls
echo ===================================================
echo    [NotebookLM Login / Session Recovery]
echo ===================================================
echo.
echo  1. Standard Login (nlm login)
echo  2. Auto Recovery (Chrome Session Scavenge)
echo  3. Manual Cookie Injection
echo  4. Test Connection (nlm list)
echo  5. Exit
echo.
echo ===================================================
set /p userchoice="Enter choice (1-5): "

if "%userchoice%"=="1" goto STANDARD
if "%userchoice%"=="2" goto AUTO
if "%userchoice%"=="3" goto MANUAL
if "%userchoice%"=="4" goto TEST
if "%userchoice%"=="5" goto EXIT
goto MENU

:STANDARD
echo.
echo [Standard Login] Log in when the browser opens.
python run_nlm_patched.py login
pause
goto MENU

:AUTO
echo.
echo [Auto Recovery] Extracting from Chrome...
echo (Please close Chrome first!)
python auto_scavenge_nlm_session.py
pause
goto MENU

:MANUAL
echo.
echo [Manual Recovery] Running repair script...
python repair_nlm_session.py
pause
goto MENU

:TEST
echo.
echo [Test Connection] Checking notebooks list...
python run_nlm_patched.py notebook list
echo.
pause
goto MENU

:EXIT
exit