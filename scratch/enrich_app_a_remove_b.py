import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

idx_app_a = text.find("## 🎁 부록 A")
idx_epilogue = text.find("## 🏁 에필로그")

print(f"idx_app_a: {idx_app_a}, idx_epilogue: {idx_epilogue}")

before_app_a = text[:idx_app_a]
after_epilogue = text[idx_epilogue:]

new_appendix_a = """## 🎁 부록 A. 나만의 봇 커스터마이징 가이드 (1분 ETF 종목 교체 & KOFR 파킹 자산 전환)

본서에서 제공하는 `kis_bot_multi.py` 봇은 독자 여러분의 투자 성향에 맞춰 **ETF 종목코드를 1초 만에 자유롭게 교체**할 수 있도록 완벽히 모듈화되어 있습니다. 

---

### 1. 공격자산 및 안전자산 티커 교체 방법
`kis_bot_multi.py` 소스 코드 상단의 티커 변수를 원하는 ETF 종목코드로 수정하기만 하면 봇이 자동으로 해당 자산을 계산하여 매매합니다.

```python
# 💡 [설정 예시 1] 기본 설정 (KOSPI200 + 미국달러단기채권)
TICKER_RISKY = "069500"  # KODEX 200
TICKER_SAFE  = "329750"  # TIGER 미국달러단기채권액티브

# 💡 [설정 예시 2] 미국 주식 중심 전환 (미국 S&P500 + KOFR 원화파킹금액)
# TICKER_RISKY = "360750"  # TIGER 미국S&P500
# TICKER_SAFE  = "423160"  # KODEX KOFR금리액티브(합성) - 원화 파킹 통장 효과
```

---

### 2. 원화 금리형(KOFR / CD금리) 파킹 자산 전환의 장점
* **환율 변동성 차단:** 달러 환율 변동 위험을 피하고 한국 원화 기준 안정적인 하루 단위 이자 수익(연 3.5% 안팎)을 얻고 싶다면 안전자산 티커를 `423160` (`KODEX KOFR금리액티브`) 또는 `459580` (`TIGER CD금리투자KIS`)으로 변경하시면 됩니다.

---

"""

final_text = before_app_a + new_appendix_a + after_epilogue

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(final_text)

print("SUCCESSFULLY REMOVED APPENDIX B AND ENRICHED APPENDIX A WITH REAL PYTHON CODE!")
