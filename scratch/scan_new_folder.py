import os
import json

target_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더"
output_file = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\scan_result.json"

res = []

if os.path.exists(target_dir):
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, target_dir)
            size = os.path.getsize(full_path)
            res.append({
                "rel_path": rel_path,
                "full_path": full_path,
                "size_bytes": size,
                "filename": file
            })
else:
    print(f"Target directory {target_dir} does not exist!")

os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)

print(f"Scanned {len(res)} files. Output saved to {output_file}")
