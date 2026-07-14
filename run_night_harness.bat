@echo off
pushd "%~dp0"
set PYTHONUTF8=1
"C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe" run_harness_at_night.py
popd
exit
