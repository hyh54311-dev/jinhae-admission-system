import os
import sys
import datetime
import subprocess

def get_mod_time(path):
    if os.path.exists(path):
        mtime = os.path.getmtime(path)
        return datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    return "Not Found"

def main():
    print("=== File Modification Times ===")
    files_to_check = [
        "daily_news.py",
        "cloud_daily_news.py",
        "run_news_once.py",
        "run_news_once.vbs",
        "run_news_once.bat",
        "admission_news.py",
        "admission_news_gas.js",
        "weekday_news_gas.js",
        "weekend_news_gas.js"
    ]
    for f in files_to_check:
        print(f"{f}: {get_mod_time(f)}")
        
    print("\n=== Searching All Folders in Windows Task Scheduler ===")
    ps_cmd = 'Get-ScheduledTask | Where-Object {$_.State -ne "Disabled" -and ($_.TaskName -like "*news*" -or $_.TaskName -like "*daily*" -or $_.TaskName -like "*macro*")} | Select-Object TaskPath, TaskName, State | Format-List'
    try:
        res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        print(res.stdout)
    except Exception as e:
        print("Error checking scheduled tasks:", e)

if __name__ == '__main__':
    main()
