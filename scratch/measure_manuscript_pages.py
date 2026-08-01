import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

total_bytes = len(text.encode('utf-8'))
total_chars_with_spaces = len(text)
total_chars_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\r", ""))
total_lines = len(text.splitlines())
total_words = len(text.split())

# 출판 페이지 수 정밀 산정 (A5/신국판 기준)
# 1페이지당 평균 800자(공백 포함, 코드/표/여백 포함 시)
est_pages_a5_standard = round(total_chars_with_spaces / 850)
est_pages_a5_generous = round(total_chars_with_spaces / 750)

print(f"=== MANUSCRIPT VOLUME STATS ===")
print(f"Total Bytes: {total_bytes:,} Bytes ({total_bytes/1024:.2f} KB)")
print(f"Total Characters (with spaces): {total_chars_with_spaces:,} chars")
print(f"Total Characters (no spaces): {total_chars_no_spaces:,} chars")
print(f"Total Words: {total_words:,} words")
print(f"Total Lines: {total_lines:,} lines")
print(f"Estimated Book Pages (A5 / B6 Standard): ~{est_pages_a5_standard} - {est_pages_a5_generous} pages")
