# -*- coding: utf-8 -*-
import os

def scan_dir(path, indent=0):
    output = []
    try:
        items = os.listdir(path)
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                output.append("  " * indent + f"📁 {item}/")
                output.extend(scan_dir(item_path, indent + 1))
            else:
                size_kb = os.path.getsize(item_path) / 1024
                output.append("  " * indent + f"📄 {item} ({size_kb:.1f} KB)")
    except Exception as e:
        output.append("  " * indent + f"❌ Error reading: {e}")
    return output

target_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\0. 이전 학년도 자료"
lines = scan_dir(target_dir)

output_file = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\historical_structure_new.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Successfully wrote historical structure to {output_file}!")
