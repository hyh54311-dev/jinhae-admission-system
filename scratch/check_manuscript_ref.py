import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

has_openapi = "Open API 서비스 신청" in text
has_actions_enable = "enable" in text.lower() or "Actions" in text or "스케줄러" in text

print(f"Open API 서비스 신청 포함 여부: {has_openapi}")
print(f"Actions 활성화 관련 언급 포함 여부: {has_actions_enable}")

# 세부 라인 추출
lines = text.split('\n')
for i, line in enumerate(lines, 1):
    if "Open API 서비스 신청" in line or "Actions" in line or "enable" in line.lower() or "스케줄러" in line:
        if i <= 800 or (1400 <= i <= 1800): # 4장 위주 스캔
            print(f"Line {i}: {line.strip()}")
