import os

def check_file(path):
    try:
        size = os.path.getsize(path)
        mtime = os.path.getmtime(path)
        import datetime
        mtime_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        pause_val = "Not found"
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if "PAUSE_WEEKDAY =" in line:
                    pause_val = line.strip()
                    break
        print(f"Path: {path}")
        print(f"  Size: {size} bytes | Modified: {mtime_str}")
        print(f"  Setting: {pause_val}")
    except Exception as e:
        print(f"Error checking {path}: {e}")

def main():
    print("Searching for daily_news.py files in D:\\...")
    # Walk D:\ to find daily_news.py
    # To keep it fast, we can restrict search to OneDrive directories or scan folders
    search_roots = ["D:\\OneDrive - 경상남도교육청", "D:\\OneDrive"]
    
    found = []
    for root in search_roots:
        if not os.path.exists(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # Skip hidden folders and pycache
            if any(p in dirpath for p in [".git", "__pycache__", ".agents", "temp"]):
                continue
            if "daily_news.py" in filenames:
                full_path = os.path.join(dirpath, "daily_news.py")
                found.append(full_path)
                
    print(f"Found {len(found)} copies of daily_news.py:")
    for path in found:
        check_file(path)

if __name__ == '__main__':
    main()
