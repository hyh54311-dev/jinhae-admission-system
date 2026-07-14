# -*- coding: utf-8 -*-
import os
import sys
import markdown
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Ensure output encoding is UTF-8
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

SCOPES = ['https://www.googleapis.com/auth/drive']

def auth():
    creds = None
    # Look for token.json in parent directory
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    token_path = os.path.join(parent_dir, 'token.json')
    print(f">> 로딩할 token.json 경로: {token_path}")
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("token.json이 없거나 유효하지 않습니다. 다시 인증해주세요.")
    return creds

def create_and_share_gdoc():
    md_content = """# 퀀트 투자자를 위한 단계별 독서 로드맵 10선 (V2)

## 🗺️ 독서 로드맵 추천 가이드 개요
본 로드맵은 한국투자증권 API와 Google Cloud Platform(GCP)을 활용해 **K-듀얼모멘텀 매매 자동화 시스템**을 완성하신 선생님을 위한 맞춤형 독서 가이드입니다. 

인간의 직관과 주관적 예측을 철저히 배제하고 기계적으로 규칙을 따르는 퀀트 투자자로서, 심리적 흔들림(뇌동매매의 유혹)을 원천 차단하고 시스템을 장기적으로 유지하며 고도화하기 위한 3단계 독서 로직으로 구성되었습니다.

---

## 🟢 1단계: 시스템에 대한 철저한 확신 (1~4권)
*목표: 내가 가동 중인 듀얼 모멘텀 시스템의 통계적·학술적 작동 원리를 깊이 이해하고, 단순한 규칙이 왜 복잡한 시장 예측보다 우월한지 뼈대를 다지는 단계입니다.*

### 1. 《듀얼 모멘텀 투자 전략》 - 게리 안토나치
- **핵심 교훈**: 상대 모멘텀과 절대 모멘텀의 결합을 통한 강세장 추세 추종 및 하락장 안전자산 대피의 통계적 우월성.
- **자동화 투자자 관점**: 현재 가동 중인 `kis_bot_multi.py` 알고리즘의 이론적 고향이자 교과서입니다.

### 2. 《현명한 자산배분 투자자》 - 윌리엄 번스타인
- **핵심 교훈**: 상관관계가 낮은 자산 배분을 통해 포트폴리오의 변동성(MDD)을 극적으로 줄이는 포트폴리오 이론의 기초.
- **자동화 투자자 관점**: 듀얼 모멘텀 외에 주식/채권 등 다자산 분산 포트폴리오를 설계할 때 든든한 기초 체력이 됩니다.

### 3. 《금융 시장의 기술적 분석》 - 존 머피
- **핵심 교훈**: 자본주의 시장에서 가격의 '추세(Trend)'와 '모멘텀' 현상이 영구적으로 관찰되는 통계적·기술적 근거.
- **자동화 투자자 관점**: 시장의 무작위성 속에서도 왜 추세 추종 전략이 장기적으로 승리할 수밖에 없는지 깊은 신뢰를 채워줍니다.

### 4. 《가치투자 실전 매뉴얼》 - 웨슬리 그레이, 토비아스 카을리
- **핵심 교훈**: 인간의 직관적인 종목 분석 대신 오직 '계량화된 지표(퀀트)'로만 필터링한 투자의 객관적 우월함 증명.
- **자동화 투자자 관점**: 인간의 두뇌 분석보다 컴퓨터의 정량적 규칙 필터링이 장기적으로 훨씬 나은 결실을 거둠을 통계로 납득시킵니다.

---

## 🟠 2단계: 인간의 편향과 감정의 통제 (5~7권)
*목표: 시스템은 완벽해도 계좌를 열어보며 규칙을 억지로 바꾸고 싶어 하는 '인간 진화론적 한계와 뇌의 본능'을 인지적으로 격리하는 단계입니다.*

### 5. 《생각에 관한 생각》 - 대니얼 카너먼
- **핵심 교훈**: 행동경제학의 창시자가 밝히는 시스템 1(직관적 빠른 오류)과 시스템 2(이성적 느린 판단)의 메커니즘.
- **자동화 투자자 관점**: 인간의 판단이 얼마나 왜곡되기 쉬운지 깨닫고, 왜 매매 결정을 구글 클라우드에 100% 위임해야 하는지 뼈저리게 깨닫게 됩니다.

### 6. 《투자 마켓 사이클의 법칙》 - 하워드 막스
- **핵심 교훈**: 시장의 상승과 하락 사이클 속에서 탐욕과 공포에 휩쓸리는 대중의 심리와 이를 역행하는 규칙 기반 인내심.
- **자동화 투자자 관점**: 자산 배분이 언더퍼폼하거나 횡보할 때, 사이클의 한 과정임을 이해하고 시스템 스위치를 끄지 않도록 심리를 잡아줍니다.

### 7. 《돈의 심리학》 - 모건 하우절
- **핵심 교훈**: 부를 일구는 기술보다 부를 안정적으로 '지키는 태도'와 리스크 관리의 중요성을 다루는 최고의 에세이.
- **자동화 투자자 관점**: 자산이 기계적으로 불어날 때 발생하는 '더 높은 수익률'에 대한 욕심을 잠재우고 묵묵히 시스템을 신뢰하게 만듭니다.

---

## 🔵 3단계: 리스크 관리와 시스템의 장기 생존 (8~10권)
*목표: 예측 불가능한 대공황(블랙 스완)이 오더라도 시스템을 파괴하지 않고 살아남는 철학적 대비와 자산 배분의 강건함을 기르는 단계입니다.*

### 8. 《앤티프래질》 - 나심 탈레브
- **핵심 교훈**: 무작위성과 충격을 견디는 것을 넘어, 오히려 거대한 충격(MDD) 속에서 더 강해지는(Antifragile) 시스템의 철학.
- **자동화 투자자 관점**: 클라우드 봇이 직면할 극단적 변동성 구간을 인프라적으로 수용하고 장기 생존하기 위한 거시적 방패가 됩니다.

### 9. 《주식 시장을 이기는 작은 책》 - 조엘 그린블라트
- **핵심 교훈**: 아주 단순하고 강력한 마법 공식을 흔들림 없이 반복 실행할 때 거두는 압도적 복리 효과.
- **자동화 투자자 관점**: "시스템이 단순할수록 강력하다"는 퀀트의 대원칙을 상기시키며 기계적 실행력을 강화해 줍니다.

### 10. 《터틀의 방식》 - 커티스 페이스
- **핵심 교훈**: 평범한 사람들을 모아 오직 '정해진 매매 규칙'만 따르게 하여 엄청난 성과를 낸 터틀 트레이딩 실험.
- **자동화 투자자 관점**: 규칙을 칼같이 준수하는 실행력이 투자의 성패를 결정하는 유일한 열쇠임을 증명합니다.

---

## 💡 선생님을 위한 퀀트 가동 실천 제안
1. **투자의 지루함을 다른 곳으로 분출하세요**: 퀀트 자동화가 완전히 끝나면 투자가 극도로 지루해집니다. 이 도파민 분출구를 학내 업무 자동화(GAS)나 새로운 파이썬 코딩 프로젝트로 전환하는 것이 가장 건강합니다.
2. **언더퍼폼 구간을 견디세요**: 벤치마크 지수보다 수익률이 뒤처지는 6개월~1년의 지루한 구간이 올 때마다 이 독서 가이드의 책들을 한 권씩 격파해 나가며 시스템을 신뢰해 주십시오.
"""

    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Save local markdown file
    md_path = os.path.join(parent_dir, "퀀트_투자자를_위한_단계별_독서_로드맵_10선.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✅ 로컬 마크다운 파일 저장 성공: {md_path}")
    
    # 2. Convert to HTML for Google Doc import
    html_text = markdown.markdown(md_content, extensions=['extra'])
    html_path = md_path.replace('.md', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
    print(f"✅ 임시 HTML 파일 변환 성공: {html_path}")
    
    # 3. Authenticate and upload to Google Drive
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {
        'name': '퀀트 투자자를 위한 단계별 독서 로드맵 10선 (V2)',
        'mimeType': 'application/vnd.google-apps.document'
    }
    media = MediaFileUpload(html_path, mimetype='text/html', resumable=True)
    
    print(">> 구글 드라이브 문서 생성 중...")
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    file_id = file.get('id')
    web_link = file.get('webViewLink')
    print(f"✅ 구글 문서 생성 성공! ID: {file_id}")
    
    # 4. Share file publicly (anyone with the link can view)
    print(">> 문서 링크 공유 권한 설정 중...")
    drive_service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()
    print("✅ 링크 공유 권한 설정 완료!")
    
    # 5. Clean up temporary HTML file
    if os.path.exists(html_path):
        os.remove(html_path)
        
    print(f"🎉 최종 구글 문서 주소: {web_link}")
    return web_link

if __name__ == '__main__':
    try:
        create_and_share_gdoc()
    except Exception as e:
        print(f"🚨 구글 문서 생성 실패: {e}")
