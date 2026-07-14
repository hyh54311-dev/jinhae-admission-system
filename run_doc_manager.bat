@echo off
pushd "%~dp0"
"python" "document_manager.py" >> "document_manager.log" 2>&1
popd
