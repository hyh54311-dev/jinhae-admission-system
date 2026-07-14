# -*- coding: utf-8 -*-
import os
import json

src1 = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더 (2)"
src2 = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더_정리완료"

def scan_dir(path):
    files_list = []
    if not os.path.exists(path):
        return files_list
    for root, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, path)
            size = os.path.getsize(full_path)
            files_list.append({
                "rel_path": rel_path,
                "full_path": full_path,
                "size": size,
                "name": file
            })
    return files_list

def main():
    print("Scanning Source 1 (새 폴더 (2))...")
    files_src1 = scan_dir(src1)
    print(f"Source 1 has {len(files_src1)} files.")

    print("Scanning Source 2 (새 폴더_정리완료)...")
    files_src2 = scan_dir(src2)
    print(f"Source 2 has {len(files_src2)} files.")

    scan_summary = {
        "src1_count": len(files_src1),
        "src2_count": len(files_src2),
        "src1_files": files_src1[:500], # save first 500 for inspection
        "src2_files": files_src2[:500]
    }
    
    # Save a complete stats report
    stats = {
        "src1_total": len(files_src1),
        "src2_total": len(files_src2),
        "src1_extensions": {},
        "src2_extensions": {}
    }
    
    for f in files_src1:
        ext = os.path.splitext(f["name"])[1].lower()
        stats["src1_extensions"][ext] = stats["src1_extensions"].get(ext, 0) + 1
        
    for f in files_src2:
        ext = os.path.splitext(f["name"])[1].lower()
        stats["src2_extensions"][ext] = stats["src2_extensions"].get(ext, 0) + 1
        
    print("Source 1 Extensions:")
    print(json.dumps(stats["src1_extensions"], indent=2))
    print("Source 2 Extensions:")
    print(json.dumps(stats["src2_extensions"], indent=2))

    with open(r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\scan_new_sources_summary.json", "w", encoding="utf-8") as f:
        json.dump({"summary": scan_summary, "stats": stats}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
