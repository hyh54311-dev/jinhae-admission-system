import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec35_github_history_entry = """

---

### 📍 항목 4.4: 3.5절 GitHub Actions 100% 무료 무인 서버리스 자동 배포 세팅 가이드 수록 (2026-08-02 확정 반영)
* **원고 위치:** `3부 3.5절` (Line 700 부근)
* **수정 이유:** 
  1. AWS/GCP의 유료/서버 구축 부담을 완전 해소하고, 신용카드 등록 없이 평생 100% 무료로 컴퓨터를 꺼두어도 자동 가동되는 **GitHub Actions 3대 무상 장점** 반영.
  2. 내 KIS API 키 및 텔레그램 토큰 유출을 100% 차단하는 **GitHub Secrets 6대 보안 키 등록 가이드표** 수록.
  3. 무인 자동 실행 파일(`.github/workflows/rebalance.yml`)의 **매달 17~31일 KST 12:30 Cron 스케줄 자동 깨어남 및 파이썬 봇 가동 3대 메커니즘** 수록.

```diff
+ #### 💡 [서버 비용 0원] GCP/AWS 대신 GitHub Actions가 초보자에게 최고인 3대 이유
+ #### 🔐 [보안 팩트] GitHub Secrets에 등록하는 6대 필수 보안 키 가이드
+ #### ⚙️ 무인 자동 실행 파일(.github/workflows/rebalance.yml) 3대 작동 원리
```
"""

if "3.5절 GitHub Actions 100% 무료 무인 서버리스 자동 배포" not in content:
    content += sec35_github_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 3.5 GITHUB ACTIONS GUIDE!")
