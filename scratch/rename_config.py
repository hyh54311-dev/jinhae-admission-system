import os

def rename_in_file(file_path, old_name, new_name):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to replace whole word matches of CONFIG
    # In Javascript, CONFIG.RESPONSE_SHEET_NAME, CONFIG = {, etc.
    # We can do a simple replacement, but let's be careful.
    # Since CONFIG is a unique token used for settings, replacing 'CONFIG' with 'WEBAPP_CONFIG' / 'AUTO_CONFIG' is safe.
    import re
    # Match CONFIG as a word boundary
    pattern = r'\b' + old_name + r'\b'
    new_content = re.sub(pattern, new_name, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Renamed {old_name} to {new_name} in {file_path}")

def main():
    # Rename CONFIG to WEBAPP_CONFIG in 문학_탐구보고서_웹앱_Code.gs
    rename_in_file("문학_탐구보고서_웹앱_Code.gs", "CONFIG", "WEBAPP_CONFIG")
    # Rename CONFIG to AUTO_CONFIG in Code_Literature_Auto.gs
    rename_in_file("Code_Literature_Auto.gs", "CONFIG", "AUTO_CONFIG")

if __name__ == '__main__':
    main()
