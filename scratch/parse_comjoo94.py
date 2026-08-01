import re, sys
sys.stdout.reconfigure(encoding='utf-8')

file_path = r'C:\Users\요한T\.gemini\antigravity\brain\7a82df81-3c3f-49ab-aa25-d1655b5a4e5e\.system_generated\steps\432\content.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Find repository links
repos = re.findall(r'href="(/comjoo94/[^"]+)"', text)
unique_repos = sorted(list(set(repos)))

print("Found repos:")
for r in unique_repos:
    print(r)
