@echo off
pushd "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "ai_scholarship_reminder.ps1"
popd
