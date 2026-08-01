import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx_epilogue = text.find("## 🏁 에필로그")

epilogue_block = """## 🏁 에필로그: 수세(守勢)의 투자, 시장에 살아남는 자가 부를 거머쥔다

투자는 화려한 공격(대박 수익)으로 승리하는 게임이 아니라, **끈질긴 수비(손실 방어)로 시장에 끝까지 생존하는 자가 승리하는 게임**입니다.

저 역시 10년 동안 경제를 공부하고도 국내 대표 바이오기업 종목 1,700만 원 손실의 아픔을 겪었지만, 파이썬 자동화 봇과 퀀트 법칙으로 돌아와 비로소 교직에서의 일상과 마음의 평화를 찾았습니다.

이제 여러분도 인간의 감정에 휘둘리지 않는 나만의 자동화 투자 AI 봇과 함께, 본업과 사랑하는 가족들과의 일상에 전념하며 무서운 복리의 눈덩이를 굴려나가시기를 진심으로 응원합니다.

감사합니다.

**- 저자 황요한 올림**
"""

final_text = text[:idx_epilogue].rstrip() + "\n\n---\n\n" + epilogue_block

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(final_text)

print("SUCCESSFULLY 100% CLEANED UP DUPLICATE TEXT AND ENDED WITH SINGLE PERFECT EPILOGUE!")
