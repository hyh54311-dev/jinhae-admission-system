import re

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 본문 문장 중간중간 단어/숫자 단위로 불필요하게 흩뿌려진 ** 제거 및 정돈
# 예: **100%** -> 100%, **`AppKey`** -> `AppKey`

# 1. **`코드`** 형태를 `코드` 형태로 정돈
text = re.sub(r'\*\*`([^`]+)`\*\*', r'`\1`', text)

# 2. 본문 문장 내 단일 단어 강조 **단어** 정돈 (목록 헤더 제외)
lines = text.split('\n')
cleaned_lines = []
in_code = False

for line in lines:
    if line.strip().startswith('```'):
        in_code = not in_code
        cleaned_lines.append(line)
        continue
    if in_code:
        cleaned_lines.append(line)
        continue
    
    # 목록 항목 헤더 (예: * **1. 제목:**) 및 테이블(|), 헤더(#)는 보존하되 문장 중간의 남발된 ** 강조 정리
    if line.strip().startswith('*') or line.strip().startswith('-') or line.strip().startswith('>'):
        # 문장 중간에 위치한 불필요한 ** 제거 (항목 첫머리 **제목:** 은 유지)
        # 1등분: 항목 첫머리, 2등분: 내용
        parts = re.split(r'(:\s*|\*\*\s*)', line, maxsplit=2)
        # 전체 라인에서 지저분한 수식어구 ** 정리
        # 단, 💡 [팁], 📸 [캡처] 등 박스 제목은 유지
        line_clean = re.sub(r'(?<!^)(?<!\*\s)(?<!-\s)\*\*([^*]+)\*\*', r'\1', line)
        cleaned_lines.append(line_clean)
    else:
        # 일반 본문 패러그래프는 문장 내부 ** 강조 전면 제거하여 종이책 가독성 극대화
        line_clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
        cleaned_lines.append(line_clean)

final_text = '\n'.join(cleaned_lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(final_text)

print("ALL EXCESSIVE ASTERISKS SUCCESSFULLY REMOVED & STREAMLINED!")
