# -*- coding: utf-8 -*-
import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
json_path = os.path.join(base_dir, "scratch", "drive_doc_content.txt")

def main():
    if not os.path.exists(json_path):
        print("drive_doc_content.txt not found!")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # The spreadsheet has sheet '시트1'
    rows = data.get('시트1', [])
    print(f"Total rows in 시트1: {len(rows)}")
    
    # Print the first 15 rows
    for i, row in enumerate(rows[:15]):
        print(f"Row {i+1}: {row}")

if __name__ == '__main__':
    main()
