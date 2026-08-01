import os, sys, re

sys.stdout.reconfigure(encoding='utf-8')

def find_api_key(search_dir):
    pattern = re.compile(r'AIzaSy[A-Za-z0-9_\-]{33}')
    found_keys = []
    
    for root, dirs, files in os.walk(search_dir):
        # Skip git or node_modules
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '.venv', '__pycache__')]
        for f in files:
            if f.endswith(('.json', '.env', '.py', '.txt', '.gs', '.md', '.yml', '.yaml')):
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
                        content = fp.read()
                        matches = pattern.findall(content)
                        for m in matches:
                            found_keys.append((filepath, m))
                except Exception:
                    pass
    return found_keys

print("Scanning for GEMINI API KEY...")
keys = find_api_key(r"C:\Users\요한T\.gemini")
keys += find_api_key(r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder")

print(f"Total keys found: {len(keys)}")
for path, key in keys:
    print(f"Found Key in [{path}]: {key[:10]}...{key[-4:]}")

if keys:
    with open(r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\scratch\found_key.txt", "w") as out:
        out.write(keys[0][1])
