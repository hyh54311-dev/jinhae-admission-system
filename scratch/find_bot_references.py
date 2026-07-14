import os

def main():
    workspace = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
    target = "kis_bot_multi.py"
    
    print(f"Scanning for '{target}' in {workspace}...")
    for root, dirs, files in os.walk(workspace):
        # Skip directories like .git, __pycache__, etc.
        if any(x in root for x in [".git", "__pycache__", ".agents", "temp", "scratch"]):
            continue
            
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in [".py", ".ps1", ".bat", ".gs", ".js", ".json", ".md", ".txt"]:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if target in content:
                            print(f"Found in: {filepath}")
                except Exception as e:
                    pass

if __name__ == "__main__":
    main()
