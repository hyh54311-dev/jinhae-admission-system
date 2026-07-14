import os
import re

def main():
    bat_path = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Antigravity_Full_Suite.bat')
    output_lines = []
    
    if not os.path.exists(bat_path):
        output_lines.append("Startup batch file not found.")
        return
        
    with open(bat_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    for line in lines:
        if "daily_news.py" in line:
            output_lines.append("Found daily_news.py line in bat:")
            output_lines.append(line.strip())
            
            # The line is: start "" "C:\...\pythonw.exe" "D:\..."
            matches = re.findall(r'"([^"]*)"', line)
            if len(matches) >= 3:
                target_path = matches[2]
                output_lines.append(f"Extracted target path: {target_path}")
                if os.path.exists(target_path):
                    output_lines.append(f"Target path exists! Size: {os.path.getsize(target_path)} bytes")
                    try:
                        with open(target_path, 'r', encoding='utf-8', errors='ignore') as tf:
                            for idx, tline in enumerate(tf, 1):
                                if "PAUSE_WEEKDAY" in tline:
                                    output_lines.append(f"Line {idx} in target: {tline.strip()}")
                    except Exception as e:
                        output_lines.append(f"Error reading target file: {e}")
                else:
                    output_lines.append("Target path does not exist on disk!")
            else:
                output_lines.append("Could not parse path from line.")
                
    with open("scratch/startup_target_info.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print("Done. Saved info to scratch/startup_target_info.txt")

if __name__ == '__main__':
    main()
