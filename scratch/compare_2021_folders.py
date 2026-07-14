# -*- coding: utf-8 -*-
import os
import hashlib
import json

folder_a = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2021학년도"
folder_b = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더_정리완료\2021학년도"

def get_file_hash(path):
    hasher = hashlib.md5()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        return f"error_{str(e)}"

def scan_folder(folder_path):
    file_list = []
    if not os.path.exists(folder_path):
        return file_list
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, folder_path)
            size = os.path.getsize(full_path)
            file_list.append({
                "rel_path": rel_path,
                "full_path": full_path,
                "size": size,
                "name": file
            })
    return file_list

def main():
    print("Scanning Folder A...")
    files_a = scan_folder(folder_a)
    print(f"Folder A has {len(files_a)} files.")

    print("Scanning Folder B...")
    files_b = scan_folder(folder_b)
    print(f"Folder B has {len(files_b)} files.")

    # Calculate hashes for comparison
    # We will identify duplicates by rel_path or by hash
    # Let's save a summary json
    summary = {
        "folder_a_count": len(files_a),
        "folder_b_count": len(files_b),
        "files_a": files_a,
        "files_b": files_b
    }

    with open(r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\compare_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("Done scanning.")

if __name__ == "__main__":
    main()
