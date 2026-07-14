import os

search_dir = "d:\\OneDrive - 경상남도교육청\\바탕 화면\\진해고등학교\\2026학년도\\antigravity_folder"
target = "private_key"

print(f"Searching for '{target}' in files...")
found = False

for root, dirs, files in os.walk(search_dir):
    if any(p in root for p in ["node_modules", ".git", "__pycache__", ".agents"]):
        continue
    for file in files:
        if file.endswith(('.json', '.py', '.txt', '.js', '.env', '.sh', '.bat')):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if target in content:
                        print(f"Found in: {filepath}")
                        found = True
            except Exception as e:
                pass

if not found:
    print("Not found in local text files.")
