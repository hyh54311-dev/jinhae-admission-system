# -*- coding: utf-8 -*-
import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
json_path = os.path.join(base_dir, "scratch", "drive_doc_content.txt")

def main():
    if not os.path.exists(json_path):
        return
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    rows = data.get('시트1', [])
    
    target_rows = [43, 44, 46]
    for r in target_rows:
        if r <= len(rows):
            row = rows[r-1]
            print(f"\n==================== ROW {r} ====================")
            print(f"Question: {row[1]}")
            print(f"Answer:\n{row[2]}")

if __name__ == '__main__':
    main()
