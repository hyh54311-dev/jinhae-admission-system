@echo off
pushd "%~dp0"
"python" "admission_news.py" run_now >> "admission_news.log" 2>&1
popd
