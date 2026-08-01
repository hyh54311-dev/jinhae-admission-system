import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 과도하게 남용된 ** 강조 패턴 정돈
# 단, 헤더(#), 목록(*), 표(|), 코드블록(```) 등의 구조는 보존하면서 본문 텍스트 내 지저분한 ** 제거

lines = text.split('\n')
new_lines = []

in_code_block = False

for line in lines:
    if line.strip().startswith('```'):
        in_code_block = not in_code_block
        new_lines.append(line)
        continue
    
    if in_code_block:
        new_lines.append(line)
        continue

    # 헤더(#) 또는 표(|)나 이미지(![), 캡처 인용(> 📸) 등 주요 구조 요소는 보존
    # 본문 텍스트 내에서 문장 중간중간 남발된 ** 정돈
    # 단, 항목의 제목 표기(예: * **① [1단계]**: ...)나 표 안의 볼드는 깔끔히 유지하고 문장 내부 과도한 ** 강조 제거
    
    # 문장 내부의 과도한 ** 제거 처리
    # 예: "위해 **100% 불투명 검정**으로" -> "위해 100% 불투명 검정으로"
    processed_line = line
    
    # 팁 박스나 캡처 캡션 외 일반 본문 문장에서 단어 하나하나 감싸진 ** 정리
    # 리스트 첫 항목 제목(예: * **1단계:**)은 유지
    if not (line.strip().startswith('#') or line.strip().startswith('|') or line.strip().startswith('![')):
        # 지저분하게 단어 단위로 들어간 ** 처리
        # 예: **`AppKey`** -> `AppKey`
        processed_line = processed_line.replace('**`', '`').replace('`**', '`')
        
    new_lines.append(processed_line)

cleaned_text = '\n'.join(new_lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(cleaned_text)

print("MANUSCRIPT BACKTICKS AND ASTERISKS CLEANED UP SUCCESSFULLY!")
