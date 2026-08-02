import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_sec26_end = """#### 📊 [월 50만 원 / 연 600만 원 기준] 20년 과세이연 복리 자본 격차 실측 비교표"""

repl_sec26_loan_warning = """> ⚠️ **[저자의 금융 팩트 경고] 목돈 필요 시 '연금저축 담보대출'을 함부로 쓰면 안 되는 이유**  
> *"갑작스러운 목돈(전세금, 의료비 등)이 필요할 때 일부에서 '연금저축 담보대출(50~60%)'을 권유하기도 하지만, 퀀트 봇을 가동하는 독자께서는 대단히 신중해야 합니다.  
> 1. **ETF 담보대출 불가:** 증권사 규정상 연금저축 계좌 내의 **ETF(상장지수펀드)는 대부분 담보대출 대상에서 제외**되므로 봇을 중단하고 ETF를 매도해야 하는 문제가 발생합니다.  
> 2. **반대매매와 16.5% 세금 폭탄:** 주가 하락으로 담보유지비율(140%) 미달 시 증권사가 자산을 강제로 처분(반대매매)하며, 이 과정에서 **중도 인출로 간주되어 16.5% 기타소득세 세금 폭탄**을 맞게 됩니다.  
> 3. **DSR(총부채원리금상환비율) 산정 포함:** 담보대출 원리금도 DSR 산정에 포함되어 은행 주택담보대출이나 신용대출 한도를 줄이게 됩니다.  
> **결론:** 연금저축 퀀트 봇 계좌는 담보대출 없이 온전히 노후 과세이연 복리 엔진으로 보존하시고, 긴급 비상금은 별도의 CMA나 파킹통장에 나누어 유연하게 관리하시는 것이 가장 안전합니다."*

---

#### 📊 [월 50만 원 / 연 600만 원 기준] 20년 과세이연 복리 자본 격차 실측 비교표"""

if target_sec26_end in text:
    text = text.replace(target_sec26_end, repl_sec26_loan_warning)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY APPLIED LOAN WARNING TO SECTION 2.6!")
else:
    print("TARGET SECTION 2.6 HEADER NOT FOUND EXACTLY - CHECKING TEXT")
