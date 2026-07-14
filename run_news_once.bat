@echo off
pushd "%~dp0"
set PYTHONUTF8=1
"python" "run_news_once.py" >> "daily_news.log" 2>&1
popd
