import os
import re

def search_gas_url():
    dir_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
    pattern = re.compile(r"https://script\.google\.com/macros/s/[a-zA-Z0-9_-]+/exec")
    
    for root, dirs, files in os.walk(dir_path):
        # Skip pycache and hidden dirs
        if "__pycache__" in root or ".git" in root or ".agents" in root:
            continue
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in [".py", ".js", ".env", ".bat", ".txt"]:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        matches = pattern.findall(content)
                        if matches:
                            print(f"Found in {filepath}:")
                            for m in matches:
                                print(f"  {m}")
                except Exception as e:
                    pass

if __name__ == "__main__":
    search_gas_url()
