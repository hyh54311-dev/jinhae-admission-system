import os
import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 2차 정밀 스캔 맵: 3인칭 격식체 ➔ 진솔한 1인칭 현장 교사 어조
ai_tone_replacements_2 = {
    "저자는": "저는",
    "저자도": "저도",
    "저자가": "제가",
    "저자의": "저의",
    "저자에게": "저에게",
    "저자를": "저를",
    "저자로서": "저로서",
    "저자 역시": "저 역시",
    "저자 본인": "저 본인",
    "제공합니다.": "제공해 드립니다.",
    "안내합니다.": "안내해 드립니다.",
    "설명합니다.": "설명해 드립니다.",
    "소개합니다.": "소개해 드립니다.",
    "추천합니다.": "추천해 드립니다.",
    "강조합니다.": "강조하고 싶습니다.",
    "분석합니다.": "분석해 보았습니다.",
}

replaced_count_2 = 0
for old_str, new_str in ai_tone_replacements_2.items():
    if old_str in text:
        count = text.count(old_str)
        text = text.replace(old_str, new_str)
        replaced_count_2 += count
        print(f"REPLACED 2: '{old_str}' -> '{new_str}' ({count} occurrences)")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print(f"\nTOTAL 2ND PASS AI-TONE REPLACEMENTS EXECUTED: {replaced_count_2}")
