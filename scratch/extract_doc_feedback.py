import re

file_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.system_generated\steps\2756\content.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# HTML 태그 제거하고 순수 한국어/텍스트 피드백 추출
clean_text = re.sub(r'<[^>]+>', ' ', text)
clean_text = re.sub(r'\s+', ' ', clean_text)

# 1.1, 1.2 등 피드백 관련 매칭 구절 검색
matches = re.findall(r'(\d+\.\d+[^1-9]+)', clean_text)
print("=== 매형 피드백 추출 요약 ===")
for m in matches[:20]:
    if len(m.strip()) > 5:
        print("-", m.strip()[:150])
