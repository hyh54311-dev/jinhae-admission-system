import re, sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'C:\Users\요한T\.gemini\antigravity\brain\7a82df81-3c3f-49ab-aa25-d1655b5a4e5e\.system_generated\steps\440\content.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Find file links inside the repo
files = re.findall(r'href="(/comjoo94/Share/blob/[^"]+)"', text)
unique_files = sorted(list(set(files)))

print("Found files in comjoo94/Share repo:")
for f in unique_files:
    print(f)
