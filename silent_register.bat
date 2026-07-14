@echo off
set "SCRIPT_DIR=%~dp0"
schtasks /create /tn "DocManager_10AM" /tr "\"%SCRIPT_DIR%run_doc_manager.bat\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 10:00 /f
schtasks /create /tn "DocManager_2PM" /tr "\"%SCRIPT_DIR%run_doc_manager.bat\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 14:00 /f
schtasks /create /tn "DailyNewsSummary" /tr "\"%SCRIPT_DIR%run_news_once.bat\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 15:15 /f
schtasks /create /tn "OkinawaFlightAlert_10" /tr "\"%SCRIPT_DIR%run_flight_alert.bat\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 10:00 /f
schtasks /create /tn "OkinawaFlightAlert_15" /tr "\"%SCRIPT_DIR%run_flight_alert.bat\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 15:00 /f
