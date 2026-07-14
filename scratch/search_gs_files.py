import os
import sys

# Configure stdout to use UTF-8
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    for file in os.listdir("."):
        if file.endswith((".gs", ".js")):
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if "KOSPI" in content or "코스피" in content:
                        print(f"Found KOSPI in {file}")
                        # find matching lines
                        f.seek(0)
                        for idx, line in enumerate(f):
                            if "KOSPI" in line or "코스피" in line:
                                print(f"  Line {idx+1}: {line.strip()[:150]}")
            except Exception as e:
                print(f"Error reading {file}: {e}")

if __name__ == "__main__":
    main()
