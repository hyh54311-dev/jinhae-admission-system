import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 인위적 조어 제거 및 쉬운 문장으로 전면 치환
text = text.replace("부부 듀얼 연금저축 봇", "부부가 각각 연금저축 계좌를 만들어 함께 활용할 때")
text = text.replace("부부 듀얼 퀀트 봇", "부부가 함께 활용하는 연금저축 봇")
text = text.replace("부부 듀얼 절세 꿀팁", "부부가 함께 활용하는 2배 절세 꿀팁")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESSFULLY REMOVED INVENTED JARGON '부부 듀얼 연금저축 봇' FROM MANUSCRIPT!")
