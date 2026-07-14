@echo off
pushd "%~dp0"
set PYTHONUTF8=1
"python" -u "scratch\auto_convert_hwp_to_pdf.py" >> "scratch\hwp_convert_log.txt" 2>&1
popd

