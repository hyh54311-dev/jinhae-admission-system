import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1단계-①, ②, ③ 저자의 진솔한 고백 서사 반영 교정
target_sec11 = """과거의 저는 매일 학교 쉬는 시간은 물론, 수업 시간 사이사이에도 몰래 스마트폰 HTS/MTS를 열어보며 붉고 푸른 주가 창에 온 신경을 빼앗기곤 했습니다. 그러나 파이썬 자동화 봇과 퀀트 자산배분 법칙으로 돌아온 지금, 저는 시장의 소음에서 완전히 벗어났습니다. 비로소 교사로서 학생들에게 온 정성을 다하는 수업과 학급 경영에 몰입할 수 있게 되었고, 퇴근 후에는 사랑하는 22개월 아기와 아내의 손을 잡고 따뜻한 일상을 누리는 '마음의 평화'와 '시간의 자유'를 되찾았습니다."""

repl_sec11 = """과거 수동 투자 시절의 저는 쉬는 시간이나 점심시간마다 스마트폰 주가 창을 열어보며 주가의 상승과 하락에 온 신경을 빼앗기곤 했습니다. 특히 변동성이 작은 ETF가 아닌 개별 종목에 직접 투자했었기에 주가의 부침은 한층 더 격렬했습니다. 주식 시장을 분석하고 공부하느라 수많은 시간을 쏟아부어야 했고, 끊임없이 주가를 확인하며 마음을 졸여야 했습니다. 주식 투자라는 것은 주가가 오를 때 느끼는 기쁨보다 내릴 때 겪는 상실감이 훨씬 더 크기 때문에, 거기서 오는 심리적 불안감과 스트레스는 일상을 크게 짓누르곤 했습니다.

그러나 Antigravity AI와 함께 파이썬 자동화 봇을 구축하고 퀀트 자산배분 법칙을 적용한 지금, 저는 시장의 소음과 스트레스에서 비로소 벗어났습니다. 손절 이후 화려한 대박 수익이 찾아온 것은 아니지만, 2026년 7월 한국 증시의 엄청난 변동성 속에서도 저는 더 이상 가슴을 졸이지 않고 교직과 가정에서의 일상을 온전히 잘 유지할 수 있었습니다. 

내 손으로 직접 트레이딩을 하지 않는다는 사실 하나만으로도 주가 향방에 따른 스트레스를 크게 줄일 수 있었습니다. 주가가 많이 내릴 때는 '향후 더 저렴한 가격으로 좋은 자식을 모을 수 있는 기회'라고 마음 편히 생각하게 되었고, 주가가 급등할 때는 '현재 보유한 자산의 가치가 올랐다'는 긍정적인 마음을 가질 수 있게 되었습니다. 비로소 교사로서 수업과 학급 경영에 몰입하고, 퇴근 후에는 사랑하는 22개월 아기와 아내의 손을 잡고 따뜻한 일상을 누리는 '마음의 평화'를 되찾은 것입니다."""

if target_sec11 in text:
    text = text.replace(target_sec11, repl_sec11)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY UPDATED SECTION 1.1 WITH AUTHOR'S GENUINE NARRATIVE!")
else:
    # 유사 구절 찾기 대체
    print("TARGET STR NOT FOUND EXACTLY - SEARCHING SIMILAR TARGET")
    target_sec11_alt = """과거의 저는 매일 학교 쉬는 시간은 물론"""
    lines = text.split('\n')
    new_lines = []
    skip = False
    for line in lines:
        if "과거의 저는 매일 학교 쉬는 시간은 물론" in line:
            new_lines.append(repl_sec11)
            skip = True
        elif skip and "되찾았습니다." in line:
            skip = False
        elif not skip:
            new_lines.append(line)
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print("SUCCESSFULLY UPDATED SECTION 1.1 VIA ALT TARGET!")
