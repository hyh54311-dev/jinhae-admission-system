import os

def main():
    bat_path = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Antigravity_Full_Suite.bat')
    if not os.path.exists(bat_path):
        print("Startup batch file not found.")
        return
        
    # Read with appropriate encoding (we'll try cp949 first as it's a batch file on Korean Windows)
    encodings = ['cp949', 'utf-8']
    content = None
    used_encoding = None
    
    for enc in encodings:
        try:
            with open(bat_path, 'r', encoding=enc) as f:
                content = f.read()
            used_encoding = enc
            print(f"Successfully read file with {enc} encoding.")
            break
        except Exception:
            continue
            
    if content is None:
        print("Failed to read the file with any encoding.")
        return
        
    lines = content.splitlines()
    new_lines = []
    modified = False
    
    for line in lines:
        if "daily_news.py" in line and not line.strip().startswith("::") and not line.strip().startswith("REM"):
            print(f"Commenting out line: {line}")
            new_lines.append(f":: {line}")
            modified = True
        else:
            new_lines.append(line)
            
    if modified:
        try:
            with open(bat_path, 'w', encoding=used_encoding) as f:
                f.write("\n".join(new_lines) + "\n")
            print("Successfully updated Antigravity_Full_Suite.bat to comment out daily_news.py.")
        except Exception as e:
            print("Error writing updated file:", e)
    else:
        print("No active daily_news.py line found to modify.")

if __name__ == '__main__':
    main()
