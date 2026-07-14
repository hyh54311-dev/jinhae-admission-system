import subprocess

task_name = "Auto Convert HWP to PDF"
vbs_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\run_hwp_convert.vbs"

args = [
    "schtasks", "/create", "/tn", task_name,
    "/tr", f"wscript.exe \"{vbs_path}\"",
    "/sc", "minute", "/mo", "60", "/f"
]

print("Registering task...")
result = subprocess.run(args, capture_output=True, text=True, encoding="cp949")
print(result.stdout)
print(result.stderr)
