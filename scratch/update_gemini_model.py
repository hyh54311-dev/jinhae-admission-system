import os
import glob

workspace = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
extensions = ["*.py", "*.js"]

replace_from = "gemini-3.1-flash-lite"
replace_to = "gemini-3.1-flash-lite"

count = 0
for ext in extensions:
    for filepath in glob.glob(os.path.join(workspace, "**", ext), recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if replace_from in content:
                content = content.replace(replace_from, replace_to)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated: {filepath}")
                count += 1
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

print(f"Total files updated: {count}")
