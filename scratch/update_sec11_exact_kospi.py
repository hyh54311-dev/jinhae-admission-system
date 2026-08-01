import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 2026년 7월 아기 나이 24개월로 전면 교체
text = text.replace("22개월 아기", "24개월 아기").replace("22개월 된 어린 아기", "24개월 된 어린 아기")

# 1.1절 세부 수정 문장 교정
target_sec11_part = """그러나 Antigravity AI와 함께 파이썬 자동화 봇을 구축하고 퀀트 자산배분 법칙을 적용한 지금, 저는 시장의 소음과 스트레스에서 비로소 벗어났습니다. 손절 이후 화려한 대박 수익이 찾아온 것은 아니지만, 2026년 7월 한국 증시의 엄청난 변동성 속에서도 저는 더 이상 가슴을 졸이지 않고 교직과 가정에서의 일상을 온전히 잘 유지할 수 있었습니다. 

내 손으로 직접 트레이딩을 하지 않는다(자동화 봇에 맡긴다)는 사실 하나만으로도 주가 향방에 따른 스트레스를 크게 줄일 수 있었습니다. 주가가 많이 내릴 때는 '향후 더 저렴한 가격으로 좋은 자식을 모을 수 있는 기회'라고 마음 편히 생각하게 되었고, 주가가 급등할 때는 '현재 보유한 자산의 가치가 올랐다'는 긍정적인 마음을 가질 수 있게 되었습니다. 비로소 교사로서 수업과 학급 경영에 몰입하고, 퇴근 후에는 사랑하는 22개월 아기와 아내의 손을 잡고 따뜻한 일상을 누리는 '마음의 평화'를 되찾은 것입니다."""

repl_sec11_part = """그러나 Antigravity AI와 함께 파이썬 자동화 봇을 구축하고 퀀트 자산배분 법칙을 적용한 지금, 저는 시장의 소음과 스트레스에서 비로소 벗어났습니다. 손절 이후 화려한 대박 수익이 찾아온 것은 아니지만, 2026년 7월 한국 증시의 엄청난 변동성 속에서도 저는 더 이상 가슴을 졸이지 않고 교직과 가정에서의 일상을 온전히 잘 유지할 수 있었습니다. 특히 2026년 7월은 글로벌 금리 향방과 지정학적 리스크, 대형 반도체주의 급등락이 얽히며 코스피 일일 변동 폭이 최근 수년 내 손에 꼽힐 만큼 극심했던 폭풍우 장세였습니다. 수많은 개인 투자자들이 매일 널뛰는 주가에 안절부절못하며 일상을 잃어가던 시기였습니다.

내 손으로 직접 트레이딩을 하지 않고 자동화 봇에 맡긴다는 사실 하나만으로도 주가 향방에 따른 스트레스를 크게 줄일 수 있었습니다. 주가가 많이 내릴 때는 '향후 더 저렴한 가격으로 좋은 자산을 모을 수 있는 기회'라고 마음 편히 생각하게 되었고, 주가가 급등할 때는 '현재 보유한 자산의 가치가 올랐다'는 긍정적인 마음을 가질 수 있게 되었습니다. 비로소 교사로서 수업과 교직 업무에 필요한 다양한 에듀테크 웹앱 개발을 할 수 있는 소중한 시간적 여유를 가지게 되었고, 퇴근 후에는 사랑하는 24개월 아기와 아내의 손을 잡고 따뜻한 일상을 누리는 '마음의 평화'를 되찾은 것입니다."""

if target_sec11_part in text:
    text = text.replace(target_sec11_part, repl_sec11_part)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY UPDATED SECTION 1.1 WITH EXACT USER INSTRUCTIONS!")
else:
    print("TARGET NOT FOUND EXACTLY - SEARCHING ALT")
    # 유사 구절 찾아서 교정
    lines = text.split('\n')
    new_lines = []
    skip = False
    for line in lines:
        if "손절 이후 화려한 대박 수익이 찾아온 것은 아니지만" in line or "그러나 Antigravity AI와 함께 파이썬 자동화 봇을 구축" in line:
            new_lines.append(repl_sec11_part)
            skip = True
        elif skip and "마음의 평화'를 되찾은 것입니다." in line:
            skip = False
        elif not skip:
            new_lines.append(line)
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print("SUCCESSFULLY UPDATED SECTION 1.1 VIA ALT SEARCH!")
