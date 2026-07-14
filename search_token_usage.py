import os
import sys
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def main():
    folder = "."
    kw = "token"
    
    for root, dirs, files in os.walk(folder):
        if any(p in root for p in [".git", "__pycache__", ".agents"]):
            continue
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as file:
                        content = file.read()
                        if kw in content:
                            print(f"Found '{kw}' in file: {path}")
                            # Let's print the lines containing kw
                            lines = content.splitlines()
                            for idx, l in enumerate(lines):
                                if kw in l:
                                    print(f"  Line {idx+1}: {l.strip()}")
                except Exception:
                    pass

if __name__ == '__main__':
    main()
