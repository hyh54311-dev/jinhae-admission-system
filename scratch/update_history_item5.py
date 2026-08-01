import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

item5_history_entry = """

---

### 📍 항목 2.7: 1.4절 에듀테크 5번 항목 (스마트폰 PWA 음성 세특 관찰 대시보드 웹앱) 추가 수록 (2026-08-02 확정 반영)
* **원고 위치:** `1부 1.4절 에듀테크 결실 목록 5번` (Line 130 부근)
* **수정 이유:** 스마트폰 PWA 앱 기반 실시간 음성 관찰 기록 ➔ 구글 시트 자동 저장 ➔ 반별 교사 대시보드 정리 및 영역별 세특 연동 시스템 수록. 특히 **동료 교사들이 복사 단 한 번으로 무상 쉽게 공유·활용할 수 있는 현장 친화성**을 강력히 강조.

```diff
+ * 5. 스마트폰 PWA 앱 연동 '음성 실시간 관찰기록 & 반별 세특 통합 대시보드 웹앱' (동료 교사 무상 공유형)
+   * 기술 및 환경: 스마트폰 PWA(Progressive Web App) 앱 기술, 구글 앱스스크립트(GAS), 구글 시트 데이터베이스 연동
+   * 활용 및 혁신적 가치: 교사가 교실 수업이나 수행평가 중 스마트폰 PWA 앱을 켜고 말하면, 교사의 음성 관찰 기록이 실시간 텍스트로 변환되어 구글 시트에 차곡차곡 자동 저장됩니다. 교사용 모니터링 대시보드에서는 반별로 어떤 학생에게 어떤 관찰 기록이 쌓였는지 한눈에 바로바로 정돈되어 시각화되며, 이 데이터는 학기 말 영역별 세특 작성 시 그대로 안전하게 연동 반영됩니다.
+   * 동료 교사 무상 공유 및 확장의 용이성 (★ 핵심 강점): 이 웹앱은 고가의 솔루션을 구독할 필요 없이, 동료 선생님들이 구글 시트 복사(복사본 만들기) 단 한 번만으로 누구나 즉시 자신의 학급과 교과에 100% 무상으로 쉽게 적용하고 공유할 수 있도록 완벽히 템플릿화되어 있는 현장 친화적 결실입니다.
```
"""

if "1.4절 에듀테크 5번 항목 (스마트폰 PWA 음성 세특 관찰 대시보드 웹앱) 추가 수록" not in content:
    content += item5_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH ITEM 5 PWA SETEUK DASHBOARD!")
