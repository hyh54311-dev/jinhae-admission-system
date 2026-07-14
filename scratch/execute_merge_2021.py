# -*- coding: utf-8 -*-
import os
import shutil
import hashlib
import json

folder_a = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2021학년도"
folder_b = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더_정리완료\2021학년도"

def get_fast_hash(path):
    try:
        size = os.path.getsize(path)
        hasher = hashlib.md5()
        with open(path, "rb") as f:
            chunk = f.read(1024 * 1024)
            hasher.update(chunk)
        hasher.update(str(size).encode('utf-8'))
        return hasher.hexdigest(), size
    except Exception as e:
        return f"error_{str(e)}", 0

def main():
    print("Starting safe migration...")
    
    # 1. Scan Folder B
    files_to_migrate = []
    for root, dirs, files in os.walk(folder_b):
        for file in files:
            src_full = os.path.join(root, file)
            rel_path = os.path.relpath(src_full, folder_b)
            dest_full = os.path.join(folder_a, rel_path)
            files_to_migrate.append({
                "src": src_full,
                "dest": dest_full,
                "rel": rel_path,
                "name": file
            })
            
    print(f"Found {len(files_to_migrate)} files to migrate.")
    
    copied_count = 0
    verified_count = 0
    deleted_count = 0
    
    # 2. Copy then Verify then Delete (atomic-like behavior per file)
    for item in files_to_migrate:
        src = item["src"]
        dest = item["dest"]
        rel = item["rel"]
        
        # Calculate source hash before copying
        src_hash, src_size = get_fast_hash(src)
        
        # Ensure destination directory exists
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
            
        print(f"Copying: {rel} ({src_size} bytes)...")
        
        # Copy
        shutil.copy2(src, dest)
        copied_count += 1
        
        # Calculate dest hash and verify
        dest_hash, dest_size = get_fast_hash(dest)
        
        if src_hash == dest_hash and src_size == dest_size:
            print(f"  Verified! Hash matches: {src_hash}")
            verified_count += 1
            
            # Safe to delete source
            os.remove(src)
            deleted_count += 1
        else:
            raise RuntimeError(f"CRITICAL ERROR: Hash mismatch for {rel}!\nSource Hash: {src_hash}, Dest Hash: {dest_hash}")

    print("\nMigration Completed successfully!")
    print(f"Copied: {copied_count}")
    print(f"Verified: {verified_count}")
    print(f"Deleted from source: {deleted_count}")

    # Check total files in Folder A
    total_a = 0
    for root, dirs, files in os.walk(folder_a):
        total_a += len(files)
        
    print(f"Total files now in Folder A (2021학년도): {total_a}")
    
    # Save merge statistics
    merge_stats = {
        "migrated_count": copied_count,
        "verified_count": verified_count,
        "deleted_count": deleted_count,
        "total_in_2021": total_a
    }
    
    stats_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\merge_stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(merge_stats, f, ensure_ascii=False, indent=2)
        
    # Clean up empty folders in Folder B's 2021 directory
    # (Since files are deleted, clean up empty subdirs)
    for root, dirs, files in os.walk(folder_b, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root, d)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"Cleaned empty dir: {os.path.relpath(dir_path, folder_b)}")
            except Exception:
                pass
                
    # Also clean up folder_b itself if empty
    try:
        if not os.listdir(folder_b):
            os.rmdir(folder_b)
            print("Cleaned empty main 2021 folder in 새 폴더_정리완료.")
    except Exception:
        pass

if __name__ == "__main__":
    main()
