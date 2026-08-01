import os

dir_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부"
with open("scratch/attendance_dir_list.txt", "w", encoding="utf-8") as f:
    f.write(f"Listing directory: {dir_path}\n")
    if os.path.exists(dir_path):
        files = os.listdir(dir_path)
        for name in files:
            full_path = os.path.join(dir_path, name)
            f.write(f"- {name} (Size: {os.path.getsize(full_path)} bytes)\n")
    else:
        f.write("Directory does not exist.\n")
print("Done. Check scratch/attendance_dir_list.txt")
