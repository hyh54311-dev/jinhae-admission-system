import os
import sys
import re

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

cleaned_lines = []
cleaned_stars_count = 0

for line in lines:
    original_line = line
    
    # 1. 리스트 항목 표기용 맨 앞 '* ' 기호는 마크다운 리스트이므로 보존하되, 문장 중간의 단일 '*' (이탈릭 강조 기호) 제거
    # 리스트 맨 앞 '* '가 아닌 문장 내부 단일 '*' 제거 (예: *문장* -> 문장)
    # 단, bold '**'는 유지하되, '** ' 및 ' **'의 불필요한 공백과 기호 정제
    
    # 문장 내부의 불필요한 단일 '*' 제거 (리스트 아이템 `* ` 제외)
    # 굵은 글씨 `**text**` 문법을 올바르게 맞추기 위해 삼중 `***`나 단일 `*` 정제
    line = re.sub(r'\*\*\*([^\*]+)\*\*\*', r'**\1**', line) # 삼중 별표 -> 굵은 글씨로 통일
    
    # 단일 별표 강조 (*단어*) 제거 -> 단순 텍스트로 치환 (단, 리스트 마커 `^\s*\* ` 제외)
    # 리스트 시작이 아닌 곳에서의 단일 별표 찾기
    parts = line.split('**') # bold 부분 보호하며 분할
    new_parts = []
    for idx, part in enumerate(parts):
        if idx % 2 == 0: # bold 밖의 텍스트
            # 리스트 아이템 마커 `* ` 인지 확인
            if part.startswith('* ') or part.startswith(' * '):
                # 맨 앞 리스트 마커 유지하고 나머지 단일 '*' 제거
                prefix = part[:part.find('* ')+2]
                rest = part[len(prefix):]
                rest = rest.replace('*', '')
                new_parts.append(prefix + rest)
            else:
                new_parts.append(part.replace('*', ''))
        else: # bold 안의 텍스트
            new_parts.append(part.replace('*', '')) # bold 내부 별표 제거
            
    line = '**'.join(new_parts)
    
    # 빈 ** ** 제거
    line = line.replace('****', '')
    line = line.replace('** **', ' ')
    
    if original_line != line:
        cleaned_stars_count += 1
        
    cleaned_lines.append(line)

new_text = ''.join(cleaned_lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_text)

print(f"SUCCESSFULLY CLEANED UNNECESSARY STARS & NORMALIZED BOLD FORMATTING IN {cleaned_stars_count} LINES!")
