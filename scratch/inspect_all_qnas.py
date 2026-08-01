# -*- coding: utf-8 -*-
import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
json_path = os.path.join(base_dir, "scratch", "drive_doc_content.txt")
output_path = os.path.join(base_dir, "scratch", "all_questions_and_short_answers.txt")

def main():
    if not os.path.exists(json_path):
        print("drive_doc_content.txt not found!")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rows = data.get('시트1', [])
    print(f"Total rows: {len(rows)}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, row in enumerate(rows):
            if len(row) < 3:
                continue
            timestamp, user_msg, bot_msg = row[0], row[1], row[2]
            # Replace newlines with spaces for clean listing
            bot_short = bot_msg.replace('\n', ' ')[:80]
            f.write(f"Row {idx+1} | Q: {user_msg} | A: {bot_short}...\n")
            
    print(f"Saved Q&A summary to {output_path}")

if __name__ == '__main__':
    main()
