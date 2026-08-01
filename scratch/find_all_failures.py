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

    rows = data.get('시트1', [])
    print(f"Analyzing {len(rows)} rows for unanswered or failed questions...")
    
    failure_indicators = [
        "죄송합니다", 
        "죄송하지만", 
        "포함되어 있지 않습니다", 
        "명시되어 있지 않습니다",
        "정보는 현재 제가",
        "공개하기 어렵습니다",
        "데이터가 포함되어 있지"
    ]
    
    unanswered_list = []
    
    for idx, row in enumerate(rows):
        if len(row) < 3:
            continue
        timestamp, question, answer = row[0], row[1], row[2]
        
        # Check if answer contains any indicator
        failed = False
        for ind in failure_indicators:
            if ind in answer:
                failed = True
                break
                
        # Also check for contextual misalignment like Row 201 "한 사람당은?"
        if question == "한 사람당은?" or "얼민야" in question:
            failed = True
            
        if failed:
            unanswered_list.append((idx + 1, timestamp, question, answer))
            
    print(f"Found {len(unanswered_list)} failed/unanswered questions:")
    for idx_num, ts, q, a in unanswered_list:
        print(f"\n[Row {idx_num}] ({ts})")
        print(f"Q: {q}")
        print(f"A: {a.strip().replace('\n', ' ')[:150]}...")
        print("-" * 50)

if __name__ == '__main__':
    main()
