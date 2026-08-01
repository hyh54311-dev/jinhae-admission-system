import os, sys, re, json

sys.stdout.reconfigure(encoding='utf-8')

# Check env vars first
print("1. Checking Environment Variables...")
for k, v in os.environ.items():
    if 'GEMINI' in k or 'API_KEY' in k or 'GOOGLE' in k:
        print(f"Env Var {k}: {v[:10]}...{v[-4:] if len(v)>14 else v}")

# Check specific target paths
target_paths = [
    r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder",
    r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\jinhae-bot",
    r"C:\Users\요한T\.gemini\antigravity",
    r"C:\Users\요한T\.env"
]

pattern = re.compile(r'AIzaSy[A-Za-z0-9_\-]{33}')
found_keys = []

print("\n2. Searching target project paths...")
for tpath in target_paths:
    if not os.path.exists(tpath):
        continue
    for root, dirs, files in os.walk(tpath):
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '.venv', '__pycache__', 'brain')]
        for f in files:
            if f.endswith(('.json', '.env', '.py', '.txt', '.gs', '.md', '.yml', '.js', '.ts')):
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as fp:
                        content = fp.read()
                        matches = pattern.findall(content)
                        for m in matches:
                            found_keys.append((filepath, m))
                except Exception:
                    pass

print(f"Found keys count: {len(found_keys)}")
for p, k in found_keys:
    print(f"Key in [{p}]: {k}")

if found_keys:
    valid_key = found_keys[0][1]
    with open(r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\scratch\active_gemini_key.txt", "w", encoding='utf-8') as out:
        out.write(valid_key)
