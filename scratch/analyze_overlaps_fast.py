# -*- coding: utf-8 -*-
import os
import hashlib
import json

folder_a = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2021학년도"
folder_b = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더_정리완료\2021학년도"

def get_fast_hash(path):
    """Calculate hash of first 1MB and append file size to represent content uniquely and extremely fast."""
    try:
        size = os.path.getsize(path)
        hasher = hashlib.md5()
        # Only read up to 1MB
        with open(path, "rb") as f:
            chunk = f.read(1024 * 1024)
            hasher.update(chunk)
        # Add file size to the hash to distinguish files with same prefix but different sizes
        hasher.update(str(size).encode('utf-8'))
        return hasher.hexdigest(), size
    except Exception as e:
        return f"error_{str(e)}", 0

def scan_folder_fast(folder_path):
    results = {}
    if not os.path.exists(folder_path):
        return results
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, folder_path)
            fast_hash, size = get_fast_hash(full_path)
            results[rel_path] = {
                "full_path": full_path,
                "size": size,
                "fast_hash": fast_hash,
                "name": file
            }
    return results

def main():
    print("Fast scanning and hashing Folder A...")
    files_a = scan_folder_fast(folder_a)
    print(f"Folder A scan complete: {len(files_a)} files.")
    
    print("Fast scanning and hashing Folder B...")
    files_b = scan_folder_fast(folder_b)
    print(f"Folder B scan complete: {len(files_b)} files.")

    # Check for relative path overlaps
    common_paths = set(files_a.keys()).intersection(set(files_b.keys()))
    
    # Check for filename overlaps (regardless of path)
    names_a = {info["name"]: (rel_path, info) for rel_path, info in files_a.items()}
    names_b = {info["name"]: (rel_path, info) for rel_path, info in files_b.items()}
    common_names = set(names_a.keys()).intersection(set(names_b.keys()))

    overlap_results = {
        "exact_path_overlaps": [],
        "filename_overlaps_different_paths": [],
        "folder_b_unique_files": [],
        "folder_a_unique_files": []
    }

    print("\n=== EXACT PATH OVERLAPS ===")
    for path in sorted(common_paths):
        info_a = files_a[path]
        info_b = files_b[path]
        is_same = (info_a["fast_hash"] == info_b["fast_hash"])
        print(f"Path: {path}")
        print(f"  A: Size={info_a['size']}, Hash={info_a['fast_hash']}")
        print(f"  B: Size={info_b['size']}, Hash={info_b['fast_hash']}")
        print(f"  Same Content: {is_same}")
        overlap_results["exact_path_overlaps"].append({
            "rel_path": path,
            "size_a": info_a["size"],
            "size_b": info_b["size"],
            "same_content": is_same
        })

    print("\n=== FILENAME OVERLAPS (DIFFERENT PATHS) ===")
    for name in sorted(common_names):
        rel_a, info_a = names_a[name]
        rel_b, info_b = names_b[name]
        if rel_a != rel_b:
            is_same = (info_a["fast_hash"] == info_b["fast_hash"])
            print(f"Filename: {name}")
            print(f"  A Path: {rel_a} (Size={info_a['size']})")
            print(f"  B Path: {rel_b} (Size={info_b['size']})")
            print(f"  Same Content: {is_same}")
            overlap_results["filename_overlaps_different_paths"].append({
                "filename": name,
                "rel_path_a": rel_a,
                "rel_path_b": rel_b,
                "size_a": info_a["size"],
                "size_b": info_b["size"],
                "same_content": is_same
            })

    # Folder B Unique files to merge
    for rel_path, info in files_b.items():
        if rel_path not in files_a:
            overlap_results["folder_b_unique_files"].append({
                "rel_path": rel_path,
                "size": info["size"],
                "name": info["name"]
            })

    # Folder A Unique files
    for rel_path, info in files_a.items():
        if rel_path not in files_b:
            overlap_results["folder_a_unique_files"].append({
                "rel_path": rel_path,
                "size": info["size"],
                "name": info["name"]
            })

    print(f"\nSummary:")
    print(f"- Exact path overlaps: {len(overlap_results['exact_path_overlaps'])}")
    print(f"- Filename overlaps (diff paths): {len(overlap_results['filename_overlaps_different_paths'])}")
    print(f"- Folder B unique files: {len(overlap_results['folder_b_unique_files'])}")

    with open(r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\fast_overlap_report.json", "w", encoding="utf-8") as f:
        json.dump(overlap_results, f, ensure_ascii=False, indent=2)
    print("Report written successfully.")

if __name__ == "__main__":
    main()
