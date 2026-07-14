# -*- coding: utf-8 -*-
import os

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"

def search_drive_ids():
    # Old Google Drive IDs found
    old_ids = [
        '1XmFarN9a8p8iL5Kjct881WImgtaV6D96', # 2026 brochure
        '18zshfYyc1fPubP_ijxKOdiePSaSEvfcJ', # 2026 guidelines
        '1_2hb1cC3uMQH2lCyVrpZJxI71MnxUdlT', # 2026 guidelines alt
        '1st9U31FmCuJpPzuKSin3Uql2ac3gDauU', # 2026 guidelines alt2
        '1mLqZObzNhTsBZK0X6qyl7FEN-dWrDuXR'  # 2026 guidelines alt3
    ]
    
    print("Searching for old Google Drive IDs in code files...")
    for root, dirs, files in os.walk(base_dir):
        if 'node_modules' in root or '.git' in root or '.google_messages_session' in root or 'Cookies' in root:
            continue
            
        for file in files:
            if file.endswith(('.html', '.js', '.py', '.txt', '.md', '.json', '.gs')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    for old_id in old_ids:
                        if old_id in content:
                            rel_path = os.path.relpath(file_path, base_dir)
                            print(f"Found old ID {old_id} in {rel_path}")
                except Exception:
                    pass

if __name__ == '__main__':
    search_drive_ids()
