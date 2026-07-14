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

def scan_and_hash(folder_path):
    results = {}
    if not os.path.exists(folder_path):
        return results
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, folder_path)
            size = os.path.getsize(full_path)
            md5 = get_file_hash(full_path)
            results[rel_path] = {
                "full_path": full_path,
                "size": size,
                "md5": md5,
                "name": file
            }
    return results

def main():
    print("Hashing and analyzing Folder A...")
    files_a = scan_and_hash(folder_a)
    print("Hashing and analyzing Folder B...")
    files_b = scan_and_hash(folder_b)

    # Let's check duplicates
    # Case 1: Exact relative path match
    # Case 2: Exact content hash match (but different paths)
    
    exact_path_matches = []
    hash_matches = {} # md5 -> list of (folder, rel_path)
    
    for rel_path, info in files_a.items():
        h = info["md5"]
        if h not in hash_matches:
            hash_matches[h] = []
        hash_matches[h].append(("A", rel_path))
        
    for rel_path, info in files_b.items():
        h = info["md5"]
        if h not in hash_matches:
            hash_matches[h] = []
        hash_matches[h].append(("B", rel_path))

    # Identify duplicates
    duplicates_by_hash = {md5: paths for md5, paths in hash_matches.items() if len(paths) > 1}
    
    # Check by path
    common_paths = set(files_a.keys()).intersection(set(files_b.keys()))
    
    print("\n--- RESULTS ---")
    print(f"Total in A: {len(files_a)}")
    print(f"Total in B: {len(files_b)}")
    print(f"Exact same relative paths: {len(common_paths)}")
    for cp in common_paths:
        a_info = files_a[cp]
        b_info = files_b[cp]
        is_same = (a_info["md5"] == b_info["md5"])
        print(f"  Path: {cp}")
        print(f"    Folder A: Size={a_info['size']}, MD5={a_info['md5']}")
        print(f"    Folder B: Size={b_info['size']}, MD5={b_info['md5']}")
        print(f"    Identical content: {is_same}")
        
    print(f"\nDuplicates by hash: {len(duplicates_by_hash)}")
    for md5, paths in list(duplicates_by_hash.items())[:10]: # print up to 10
        print(f"  MD5 {md5}:")
        for fld, rp in paths:
            print(f"    {fld} -> {rp}")

    # Output detailed report
    report = {
        "common_paths": list(common_paths),
        "duplicates_by_hash": duplicates_by_hash,
        "files_a": files_a,
        "files_b": files_b
    }
    
    with open(r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\overlap_analysis.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
