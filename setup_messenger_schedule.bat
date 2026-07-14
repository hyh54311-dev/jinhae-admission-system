@echo off
chcp 65001 >nul
schtasks /create /tn "CoolMessenger_AutoStop" /tr "taskkill.exe /f /im CoolMessenger.exe" /sc weekly /d MON,TUE,WED,THU,FRI /st 16:30 /f
schtasks /create /tn "CoolSub_AutoStop" /tr "taskkill.exe /f /im CoolSubProcess.exe" /sc weekly /d MON,TUE,WED,THU,FRI /st 16:30 /f
schtasks /create /tn "CoolMessenger_AutoStart" /tr "\"C:\Program Files (x86)\CoolMessenger Gentoo\CoolMessenger.exe\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 08:30 /it /f
echo 메신저 스케줄 등록 완료!
