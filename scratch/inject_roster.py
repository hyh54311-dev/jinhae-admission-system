# scratch/roster.json의 내용을 문학_탐구보고서_웹앱_Index.html의 로컬 프리뷰 데이터로 주입하는 스크립트

import json

try:
    with open("scratch/roster.json", "r", encoding="utf-8") as f:
        roster_data = json.load(f)
    
    # roster_json을 단일 라인 문자열로 축소
    roster_str = json.dumps(roster_data, ensure_ascii=False)
    
    with open("문학_탐구보고서_웹앱_Index.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    # 정확한 공백 개수를 반영하여 타겟 탐색
    target_data = """          roster: {
            "1": [{"num": 1, "name": "홍길동"}, {"num": 2, "name": "김철수"}],
            "2": [{"num": 1, "name": "이영희"}, {"num": 2, "name": "박민수"}],
            "3": [{"num": 1, "name": "최수지"}]
          }"""
            
    replacement_data = f"          roster: {roster_str}"
    
    if target_data in html:
        html = html.replace(target_data, replacement_data)
        with open("문학_탐구보고서_웹앱_Index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Successfully injected Jinhae High School real roster into 문학_탐구보고서_웹앱_Index.html!")
    else:
        print("Target mock roster not found. Let's do a regex replacement.")
        import re
        pattern = r'roster:\s*\{\s*"1":[^}]+\}\s*\}'
        if re.search(pattern, html):
            html = re.sub(pattern, f"roster: {roster_str}", html)
            with open("문학_탐구보고서_웹앱_Index.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Successfully injected Jinhae High School real roster via regex!")
        else:
            print("Could not find mock roster with regex either.")
except Exception as e:
    print("Error:", e)
