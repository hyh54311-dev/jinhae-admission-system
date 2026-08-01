import re
import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

file_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.system_generated\steps\2756\content.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# og:description 및 구글문서 내부 JSON 텍스트 파싱
meta_desc = re.findall(r'content="([^"]*1\.1[^"]*)"', text)
print("=== META DESCRIPTION EXCERPT ===")
if meta_desc:
    print(meta_desc[0])

# 한글 문장 추출
korean_sentences = re.findall(r'([가-힣0-9\s\.\(\)\,\-\:\?\!]{10,})', text)
print("\n=== KOREAN SENTENCES FOUND ===")
unique_s = []
for s in korean_sentences:
    s_clean = s.strip()
    if len(s_clean) > 15 and s_clean not in unique_s and "Google Docs" not in s_clean:
        unique_s.append(s_clean)

for s in unique_s[:30]:
    print("-", s)
