@echo off
cd /d "%~dp0"
echo ==================================================
echo Jinhae High School Admission SMS Automation
echo ==================================================
echo.
echo Requirements:
echo 1. Chrome must be running in debug mode (via Chrome_메인프로필_디버그.bat).
echo 2. Make sure your phone is paired/logged in on Google Messages Web.
echo.
echo Press any key to start sending...
pause

echo.
echo Starting automatic 1:1 bulk SMS delivery...
echo.
python send_bulk_sms.py

echo.
echo Batch SMS delivery completed! Press any key to exit.
pause
