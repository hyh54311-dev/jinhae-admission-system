@echo off
set "PYTHON=C:\Users\요한T\AppData\Local\Programs\Python\Python312\pythonw.exe"
set "SCRIPT=g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\school_reminder_trigger.py"
schtasks /create /tn "Antigravity_School_Reminder" /tr "\"%PYTHON%\" \"%SCRIPT%\"" /sc once /st 08:30 /sd 2026-04-14 /f
