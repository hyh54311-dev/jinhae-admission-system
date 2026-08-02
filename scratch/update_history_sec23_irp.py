import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

irp_search_history_entry = """

---

### 📍 항목 3.5: 2.3절 미국 주식·채권 기반 채권혼합형 ETF 안전자산 30% 인정 3중 검증 및 연금저축 전용 메인 봇 선언 수록 (2026-08-02 확정 반영)
* **원고 위치:** `2부 2.3절 도입부` (Line 300 부근)
* **수정 이유:** 
  1. IRP 계좌의 30% 의무 안전자산 제약으로 인해 모멘텀 스위칭이 제약을 받는 점을 명시하고, 본 도서는 오직 **위험자산 100% 매매가 가능한 '연금저축펀드 계좌(22)'만을 100% 전용 대상 계좌로 삼는다**는 저자 선언 반영.
  2. 금융감독원 및 운용사 공시 보도자료 3중 검색을 통해, 미국 S&P500 주식이나 코스피200 주식에 미국채를 혼합한 채권혼합형 ETF(`ACE 미국S&P500채권혼합액티브 438080`, `KODEX 200미국채혼합50 284430` 등)가 주식 비중 50% 미만으로 **IRP 30% 의무 안전자산 영역에 매수 가능 🟢**함을 실증 팩트체크하여 수록.

```diff
+ > 💡 [저자의 핵심 선언: 본 도서는 오직 '연금저축펀드 계좌'만을 메인 봇 무대로 삼습니다]
+ > *"IRP 계좌는 30% 의무 안전자산 제약이 있으므로, 위험자산 100% 자유 매매가 가능한 '연금저축펀드 계좌'만을 100% 전용 메인 계좌로 삼아 자동화 투자를 진행합니다."*
+ 
+ #### 🔍 [금융감독원 공시 팩트체크] 미국 주식·채권 기반 채권혼합형 ETF의 IRP 30% 안전자산 인정 규정 (ACE 미국S&P500채권혼합액티브 438080 등 팩트 수록)
```
"""

if "2.3절 미국 주식·채권 기반 채권혼합형 ETF 안전자산 30% 인정" not in content:
    content += irp_search_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 2.3 IRP SEARCH FACTS!")
