import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_sec11_no_bracket = """특히 2026년 7월은 글로벌 금리 향방과 지정학적 리스크, 대형 반도체주의 급등락이 얽히며 코스피 시장 전체가 거대한 폭풍우에 휩싸였던 시기였습니다. 실제 코스피 지수의 일별 변동성 데이터(표준편차)를 실측 분석해 보면, 평시 역대 평균 변동성(1.06%)의 무려 5.9배에 달하는 6.26%라는 수치를 기록했습니다. 이는 2020년 3월 코로나 펜데믹 당시의 변동성(4.11%)을 뛰어넘어 최근 12년 간 관측된 전체 147개 월 중 상위 0.7%(최고 수준)에 달하는 역대급 장중 널뛰기 장세였습니다. 매일 7% 이상 춤추는 주가 앞에서 수많은 개인 투자자들이 안절부절못하며 일상을 잃어가던 시기였습니다."""

repl_sec11_no_bracket = """특히 2026년 7월은 글로벌 금리 향방과 지정학적 리스크, 대형 반도체주의 급등락이 얽히며 코스피 시장 전체가 거대한 폭풍우에 휩싸였던 시기였습니다. 실제 코스피 지수의 일별 변동성 데이터를 표준편차 지표로 실측 분석해 보면, 평시 역대 평균 변동성인 1.06%의 무려 5.9배에 달하는 6.26%라는 수치를 기록했습니다. 이는 2020년 3월 코로나 펜데믹 당시의 변동성이었던 4.11%를 뛰어넘어 최근 12년 간 관측된 전체 147개 월 중 상위 0.7%라는 최고 수준에 달하는 역대급 장중 널뛰기 장세였습니다. 매일 7% 이상 춤추는 주가 앞에서 수많은 개인 투자자들이 안절부절못하며 일상을 잃어가던 시기였습니다."""

if target_sec11_no_bracket in text:
    text = text.replace(target_sec11_no_bracket, repl_sec11_no_bracket)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY REMOVED ALL BRACKETS IN SECTION 1.1 BACKTEST TEXT!")
else:
    print("TARGET NOT FOUND EXACTLY - DOING REPLACEMENT")
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        if "실제 코스피 지수의 일별 변동성 데이터(표준편차)를 실측 분석해 보면" in line:
            new_lines.append(repl_sec11_no_bracket)
        else:
            new_lines.append(line)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print("SUCCESSFULLY REPLACED SECTION 1.1 BACKTEST BRACKETS!")
