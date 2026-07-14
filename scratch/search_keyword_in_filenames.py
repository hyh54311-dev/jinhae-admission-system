# -*- coding: utf-8 -*-
import os

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
all_files_txt = os.path.join(base_dir, 'all_files.txt')

def main():
    print("Searching for files with '홍보', '책자', '브로슈어', '리플렛', '요강' in all_files.txt...")
    if not os.path.exists(all_files_txt):
        print("all_files.txt not found!")
        return

    keywords = ['홍보', '책자', '브로슈어', '리플렛', '요강']
    
    with open(all_files_txt, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    found_count = 0
    for line in lines:
        line_clean = line.strip()
        if any(kw in line_clean for kw in keywords) and line_clean.endswith('.pdf'):
            print(f"- {line_clean}")
            found_count += 1
            
    print(f"Total matching PDF files: {found_count}")

if __name__ == '__main__':
    main()
