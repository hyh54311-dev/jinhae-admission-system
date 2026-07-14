import subprocess
import os
import sys

def register_task(task_name, script_path, trigger_type):
    python_path = sys.executable
    tr_command = f'"{python_path}" "{script_path}"'
    
    cmd = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", tr_command,
        "/sc", trigger_type,
        "/f"
    ]
    
    if trigger_type.lower() == "hourly":
        cmd.extend(["/mo", "1"])
    
    print(f"[{task_name}] ?깅줉 以?..")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"SUCCESS: {task_name} registered")
    else:
        print(f"FAILED: {task_name}")
        print(result.stderr)

if __name__ == "__main__":
    base_dir = r"d:\OneDrive - 寃쎌긽?⑤룄援먯쑁泥?諛뷀깢 ?붾㈃\吏꾪빐怨좊벑?숆탳\2026?숇뀈??antigravity_folder"
    script = os.path.join(base_dir, "bot_maintenance.py")
    
    register_task("Antigravity_Bot_Watchdog", script, "hourly")
    register_task("Antigravity_Bot_Watchdog_Logon", script, "onlogon")
