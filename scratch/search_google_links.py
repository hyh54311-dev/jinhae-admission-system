import os
import re

pattern_form = re.compile(r'docs\.google\.com/forms/[^\s"\'\)]+')
pattern_sheet = re.compile(r'docs\.google\.com/spreadsheets/[^\s"\'\)]+')
pattern_script = re.compile(r'script\.google\.com/[^\s"\'\)]+')

for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['.git', '.google_messages_session', '.agents', 'node_modules', '__pycache__', 'temp']):
        continue
    for file in files:
        if file.endswith(('.py', '.js', '.gs', '.txt', '.md', '.html')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                forms = pattern_form.findall(content)
                sheets = pattern_sheet.findall(content)
                scripts = pattern_script.findall(content)
                if forms or sheets or scripts:
                    print(f"File: {path}")
                    if forms:
                        print(f"  Forms: {forms}")
                    if sheets:
                        print(f"  Sheets: {sheets}")
                    if scripts:
                        print(f"  Scripts: {scripts}")
            except Exception:
                # Try with cp949/euc-kr if utf-8 fails
                try:
                    with open(path, 'r', encoding='cp949') as f:
                        content = f.read()
                    forms = pattern_form.findall(content)
                    sheets = pattern_sheet.findall(content)
                    scripts = pattern_script.findall(content)
                    if forms or sheets or scripts:
                        print(f"File: {path}")
                        if forms:
                            print(f"  Forms: {forms}")
                        if sheets:
                            print(f"  Sheets: {sheets}")
                        if scripts:
                            print(f"  Scripts: {scripts}")
                except Exception:
                    pass
