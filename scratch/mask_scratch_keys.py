import os, re

scratch_dir = r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\scratch"
pattern = re.compile(r'AIzaSy[A-Za-z0-9_\-]{33}|up_[A-Za-z0-9_]{20,}')

for root, dirs, files in os.walk(scratch_dir):
    for f in files:
        if f.endswith(('.py', '.txt', '.json')):
            filepath = os.path.join(root, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as fp:
                    content = fp.read()
                if pattern.search(content):
                    masked_content = pattern.sub('MASKED_API_KEY', content)
                    with open(filepath, 'w', encoding='utf-8') as fp:
                        fp.write(masked_content)
                    print(f"Masked API keys in: {filepath}")
            except Exception as e:
                pass
