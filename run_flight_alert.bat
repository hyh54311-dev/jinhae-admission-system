@echo off
pushd "%~dp0"
"python" "flight_alert.py" >> "flight_alert.log" 2>&1
popd
