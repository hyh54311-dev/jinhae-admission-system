# -*- coding: utf-8 -*-
import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
json_path = os.path.join(base_dir, "scratch", "drive_doc_content.txt")

def analyze_logs():
    if not os.path.exists(json_path):
        print("drive_doc_content.txt not found!")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rows = data.get('시트1', [])
    print(f"Analyzing {len(rows)} logs...")

    failure_keywords = [
        "죄송합니다", "죄송하지만", "포함되어 있지 않습니다", 
        "정보가 없습니다", "정보를 찾을 수", "알 수 없습니다"
    ]

    failed_chats = []
    # Skip the header if there is one (the first row is 'Row 1')
    # Row 1 is: ['2026-07-14 02:47:38', '2026학년도 대입 결과(서울대, 의예과 등 합격자 수) 알려줘.', ...]
    for idx, row in enumerate(rows):
        if len(row) < 3:
            continue
        timestamp, user_msg, bot_msg = row[0], row[1], row[2]
        
        # Check if the bot message indicates failure
        is_failed = False
        for kw in failure_keywords:
            if kw in bot_msg:
                is_failed = True
                break
                
        if is_failed:
            failed_chats.append({
                "index": idx + 1,
                "timestamp": timestamp,
                "question": user_msg,
                "answer": bot_msg
            })

    print(f"Found {len(failed_chats)} failures.")
    
    # Save the failures to a file
    out_path = os.path.join(base_dir, "scratch", "failed_questions.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(failed_chats, f, ensure_ascii=False, indent=2)
    print(f"Saved failed questions to {out_path}")
    
    # Print them in markdown style
    for item in failed_chats:
        print(f"### Q{item['index']} ({item['timestamp']}): {item['question']}")
        print(f"A: {item['answer'].strip()[:200]}...")
        print("-" * 50)

if __name__ == '__main__':
    analyze_logs()
