import os
import sys
import datetime

# Reconfigure stdout to prevent encoding errors on Windows console print
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

output_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\autosave_findings.txt"
out_f = open(output_path, "w", encoding="utf-8")

def log(msg):
    out_f.write(msg + "\n")
    print(msg.encode('utf-8', errors='replace').decode('utf-8'))

def search_autosave_files():
    log("=== Searching for HWP Auto-Save and Temporary Files ===")
    
    # Common windows directories for HWP autosave
    user_profile = os.environ.get("USERPROFILE", "")
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    appdata = os.environ.get("APPDATA", "")
    temp_dir = os.environ.get("TEMP", "")
    
    search_paths = []
    if local_appdata:
        search_paths.append(os.path.join(local_appdata, "Hnc"))
        search_paths.append(os.path.join(local_appdata, "Temp"))
    if appdata:
        search_paths.append(os.path.join(appdata, "Hnc"))
    if temp_dir:
        search_paths.append(temp_dir)
    if user_profile:
        # Fallback to search inside appdata just in case
        search_paths.append(os.path.join(user_profile, "AppData"))

    # Remove duplicates and resolve paths
    search_paths = list(set([os.path.abspath(p) for p in search_paths if os.path.exists(p)]))
    log(f"Search directories: {search_paths}")
    
    found_files = []
    
    # We are looking for .asf files or recently modified HWP-related files (today/yesterday)
    today = datetime.date.today()
    
    for base_path in search_paths:
        log(f"Scanning: {base_path}...")
        for root, dirs, files in os.walk(base_path):
            for file in files:
                file_lower = file.lower()
                # HWP auto-save files end with .asf
                # Also check for temp hwp files (often starting with ~$) or recently modified temp files
                if file_lower.endswith(".asf") or file_lower.endswith(".tmp") or (("hwp" in file_lower or "pre" in file_lower) and file_lower.endswith(".tmp")):
                    full_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(full_path)
                        mod_date = datetime.date.fromtimestamp(mtime)
                        mod_time = datetime.datetime.fromtimestamp(mtime)
                        
                        # Only show files modified today
                        if mod_date == today:
                            found_files.append((mtime, full_path, os.path.getsize(full_path), mod_time))
                    except Exception:
                        pass
                        
    # Sort files by modification time desc
    found_files.sort(key=lambda x: x[0], reverse=True)
    
    log(f"\nFound {len(found_files)} autosave/temporary files modified today:")
    for mtime, path, size, mod_time in found_files:
        log(f"[{mod_time.strftime('%Y-%m-%d %H:%M:%S')}] Size: {size:,} bytes")
        log(f"Path: {path}")
        log("-" * 50)
        
    if not found_files:
        log("\nNo recently modified HWP auto-save or temp files found for today.")
        log("Checking if there are any HWP backup files (.asf) from earlier:")
        # Check all .asf files regardless of date
        all_asf = []
        for base_path in search_paths:
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.lower().endswith(".asf"):
                        full_path = os.path.join(root, file)
                        try:
                            mtime = os.path.getmtime(full_path)
                            mod_time = datetime.datetime.fromtimestamp(mtime)
                            all_asf.append((mtime, full_path, os.path.getsize(full_path), mod_time))
                        except Exception:
                            pass
        all_asf.sort(key=lambda x: x[0], reverse=True)
        for mtime, path, size, mod_time in all_asf[:15]:
            log(f"[{mod_time.strftime('%Y-%m-%d %H:%M:%S')}] Size: {size:,} bytes")
            log(f"Path: {path}")
            log("-" * 50)

if __name__ == "__main__":
    search_autosave_files()
    out_f.close()
