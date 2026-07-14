import os
import sys

# Configure stdout to use UTF-8
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

def search_in_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f):
                if "📊" in line or "코스피" in line or "KOSPI" in line or "개인:" in line:
                    if "warn" not in filepath.lower() and "transcript" not in filepath.lower() and "parse_log" not in filepath.lower():
                        print(f"[{filepath}:{idx}] {line.strip()[:200]}")
    except Exception as e:
        pass

def main():
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith((".log", ".txt", ".js", ".py")):
                search_in_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
