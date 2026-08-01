import re
import sys

file_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.system_generated\steps\2756\content.md'
out_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\scratch\brother_in_law_feedback.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# og:description 추출
desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', text)
desc_text = desc_match.group(1) if desc_match else ""

# 구글문서 JS 데이터 내 텍스트 매칭
raw_chunks = re.findall(r'\\n([^\\\n\r"]{4,})', text)

with open(out_path, 'w', encoding='utf-8') as f:
    f.write("# 매형(검토자) 원고 피드백 및 개선 제안 정리\n\n")
    f.write("## 📌 구글 문서 메타 요약 피드백\n")
    f.write(desc_text + "\n\n")
    f.write("## 📝 추출된 세부 피드백 목록\n")
    for c in raw_chunks:
        if len(c.strip()) > 3:
            f.write(f"- {c.strip()}\n")

print("SAVED BROTHER-IN-LAW FEEDBACK TO brother_in_law_feedback.md SUCCESSFULLY!")
