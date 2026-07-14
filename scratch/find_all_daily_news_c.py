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
    print("Searching for daily_news.py files in C:\\Users...")
    search_root = "C:\\Users\\admin"
    
    found = []
    if os.path.exists(search_root):
        for dirpath, dirnames, filenames in os.walk(search_root):
            # Skip common package folders to keep search fast
            if any(p in dirpath for p in ["AppData\\Local\\Package Cache", "AppData\\Local\\pip", "site-packages", ".git", "__pycache__"]):
                continue
            if "daily_news.py" in filenames:
                full_path = os.path.join(dirpath, "daily_news.py")
                found.append(full_path)
                
    print(f"Found {len(found)} copies of daily_news.py in C:\\Users:")
    for path in found:
        check_file(path)

if __name__ == '__main__':
    main()
