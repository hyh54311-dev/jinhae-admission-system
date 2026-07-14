import subprocess
import os

def register_tasks():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tasks = [
        {"name": "DocManager_10AM", "vbs": "run_doc_manager.vbs", "time": "10:00", "days": "MON,TUE,WED,THU,FRI"},
        {"name": "DocManager_2PM", "vbs": "run_doc_manager.vbs", "time": "14:00", "days": "MON,TUE,WED,THU,FRI"},
        {"name": "DailyNewsSummary", "vbs": "run_news_once.vbs", "time": "15:15", "days": "MON,TUE,WED,THU,FRI"},
        {"name": "OkinawaFlightAlert_10", "vbs": "run_flight_alert.vbs", "time": "10:00", "days": "MON,TUE,WED,THU,FRI"},
        {"name": "OkinawaFlightAlert_15", "vbs": "run_flight_alert.vbs", "time": "15:00", "days": "MON,TUE,WED,THU,FRI"},
        {"name": "AdmissionNews_11AM", "vbs": "run_admission_news.vbs", "time": "11:00", "days": "WED"}
    ]

    for t in tasks:
        # Delete task if exists
        subprocess.run(["schtasks", "/delete", "/tn", t["name"], "/f"], capture_output=True)
        
        vbs_path = os.path.join(script_dir, t["vbs"])
        # Command must be "wscript.exe \"path\""
        task_run = f'wscript.exe "{vbs_path}"'
        
        cmd = [
            "schtasks", "/create",
            "/tn", t["name"],
            "/tr", task_run,
            "/sc", "weekly",
            "/d", t["days"],
            "/st", t["time"],
            "/f"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"SUCCESS: Registered {t['name']}")
        else:
            print(f"FAILURE: {t['name']}\nStdout: {result.stdout}\nStderr: {result.stderr}")

if __name__ == "__main__":
    register_tasks()
