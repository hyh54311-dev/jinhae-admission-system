import os
import sys

# Configure stdout to use UTF-8
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

log_path = "telegram_assistant.log"

def main():
    if not os.path.exists(log_path):
        print(f"{log_path} does not exist.")
        return
        
    print(f"Reading {log_path}...")
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        
    print(f"Total lines: {len(lines)}")
    # Find matching lines containing KOSPI or 코스피
    count = 0
    for idx, line in enumerate(lines):
        if "코스피" in line or "KOSPI" in line or "수급" in line:
            print(f"[{idx}] {line.strip()}")
            count += 1
            if count > 100:
                print("Too many results, truncating...")
                break

if __name__ == "__main__":
    main()
