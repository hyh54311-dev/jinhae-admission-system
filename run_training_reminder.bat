@echo off
pushd "%~dp0"
"C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe" "send_training_reminder.py" >> "training_reminder.log" 2>&1
popd
