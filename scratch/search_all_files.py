# -*- coding: utf-8 -*-
import os

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"

def search_files():
    print("Searching all files in workspace for '.pdf', '홍보책자', '브로슈어', 'leaflet'...")
    keywords = ['.pdf', '홍보책자', '브로슈어', '리플렛']
    for root, dirs, files in os.walk(base_dir):
        # Skip node_modules and .git
        if 'node_modules' in root or '.git' in root or '.google_messages_session' in root or 'Cookies' in root:
            continue
            
        for file in files:
            if file.endswith(('.html', '.js', '.py', '.txt', '.md', '.json', '.gs')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    for i, line in enumerate(lines):
                        for keyword in keywords:
                            if keyword in line:
                                rel_path = os.path.relpath(file_path, base_dir)
                                print(f"Found in {rel_path} (Line {i+1}): {line.strip()}")
                except Exception:
                    pass

if __name__ == '__main__':
    search_files()
