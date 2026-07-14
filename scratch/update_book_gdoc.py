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
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    token_path = os.path.join(parent_dir, 'token.json')
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("token.json이 없거나 유효하지 않습니다. 다시 인증해주세요.")
    return creds

def update_gdoc(file_id):
    md_content = """# 퀀트 투자자를 위한 단계별 독서 로드맵 10선 (V3 - 심리 방어 최적화 버전)

## 🗺️ 독서 로드맵 추천 가이드 개요
본 로드맵은 한국투자증권 API와 Google Cloud Platform(GCP)을 활용해 **K-듀얼모멘텀 매매 자동화 시스템**을 가동 중이신 선생님을 위해 **인지 심리학적 및 실행 관점에서 고도로 커스터마이징된 독서 가이드**입니다.

"경제 공부를 하면 결국 차트를 보거나 개별 종목 뇌동매매로 회귀하게 된다"는 선생님의 심리적 취약점을 보완하기 위해, 기존 추천 리스트 중 **차트 분석 교과서(존 머피의 기술적 분석)를 단호하게 제외**하고, 시장을 우연과 소음으로 규정하여 손매매 욕구를 완벽히 제거하는 **나심 탈레브의 명저로 대체**하였습니다. 또한, 독서의 난이도와 직관성을 고려하여 순서를 정교하게 재조정했습니다.

---

## 🟢 1단계: 시스템에 대한 철저한 신뢰와 실행력 구축 (1~4권)
*목표: 모멘텀 시스템이 작동하는 통계적 근거를 채우되, 뇌동매매를 방지하기 위해 '철저한 규칙 준수의 중요성'을 가슴 깊이 새기는 단계입니다.*

### 1. 《듀얼 모멘텀 투자 전략》 - 게리 안토나치
- **핵심 교훈**: 상대 모멘텀과 절대 모멘텀의 결합을 통한 강세장 추세 추종 및 하락장 안전자산 대피의 역사적 증명.
- **퀀트 어드바이스**: 현재 돌리고 계신 `kis_bot_multi.py` 알고리즘의 원조 설계도입니다. 시스템에 대한 믿음의 첫 삽입니다.

### 2. 《터틀의 방식》 - 커티스 페이스 (★기존 10번에서 2번으로 조기 배치)
- **핵심 교훈**: 오직 '정해진 매매 규칙'만 기계적으로 따르게 훈련받은 초보 트레이더들이 시장을 지배한 실제 역사.
- **퀀트 어드바이스**: 퀀트의 핵심은 분석력이 아니라 **"규칙을 어기지 않는 실행력"**임을 깊이 각인시켜 주어, 클라우드 시스템에 수동 개입하고 싶은 욕구를 원천 차단해 줍니다. 매우 재미있고 흡입력 있는 소설식 전개로 독서의 흥미를 돋웁니다.

### 3. 《주식 시장을 이기는 작은 책》 - 조엘 그린블라트 (★기존 9번에서 3번으로 조기 배치)
- **핵심 교훈**: 단 2가지 단순한 규칙(자본수익률, 이익수익률)의 반복만으로 시장 평균을 극적으로 초월하는 원리.
- **퀀트 어드바이스**: "단순한 규칙이 인간의 복잡한 시황 분석보다 훨씬 강력하다"는 퀀트의 진리를 가장 쉽고 얇은 책으로 증명하여 초반 자신감을 채워줍니다.

### 4. 《현명한 자산배분 투자자》 - 윌리엄 번스타인
- **핵심 교훈**: 상관관계가 낮은 자산 배분을 통해 포트폴리오의 변동성(MDD)을 통계적으로 상쇄하는 방법.
- **퀀트 어드바이스**: 왜 연금 계좌와 일반 계좌의 타겟 자산을 포트폴리오 차원에서 나누어 리밸런싱해야 하는지 수학적 뼈대를 단단하게 세워줍니다.

---

## 🟠 2단계: 인간 진화론적 인지 편향의 인지 및 통제 (5~7권)
*목표: 시스템이 완성되어도 계좌를 열어보며 뇌에서 분출하는 불안감과 탐욕을 논리적으로 격리하는 투자 심리학 단계입니다.*

### 5. 《돈의 심리학》 - 모건 하우절 (★기존 7번에서 5번으로 조기 배치)
- **핵심 교훈**: 부를 일구는 기술보다 부를 안정적으로 '지키는 태도'와 리스크 관리의 중요성을 다루는 최고의 에세이.
- **퀀트 어드바이스**: 투자 심리학 서적 중 가장 읽기 편하고 흥미진진한 스토리텔링으로 구성되어 있어, 2단계 심리 공부의 완벽한 마중물 역할을 합니다.

### 6. 《투자 마켓 사이클의 법칙》 - 하워드 막스
- **핵심 교훈**: 시장의 상승과 하락 사이클 속에서 대중이 탐욕과 공포에 휩쓸리는 원리와 이를 역행하는 규칙 기반 인내심.
- **퀀트 어드바이스**: 자동 매매 봇이 일시적 횡보나 소폭 하락(MDD) 구간을 지날 때, 이를 자연스러운 사이클의 한 현상으로 의연하게 받아들이게 도와줍니다.

### 7. 《생각에 관한 생각》 - 대니얼 카너먼 (★심리 단계의 최종 보스로 배치)
- **핵심 교훈**: 인지 심리학과 행동경제학의 창시자가 밝히는 직관적 뇌(시스템 1)의 끝없는 왜곡과 오류 해부.
- **퀀트 어드바이스**: 500페이지가 넘는 다소 묵직한 벽돌 책이지만 앞선 책들로 심리 기초를 다진 상태에서 읽으면, 인간의 감과 예측이 얼마나 보잘것없는지 전율과 함께 체감하며 손매매 욕구를 영구 퇴출하게 됩니다.

---

## 🔵 3단계: 리스크 관리와 시장의 소음 해체 (8~10권)
*목표: 예측 불가능한 대공황(블랙 스완)이 오더라도 시스템을 파괴하지 않고 살아남는 철학적 대비와 자산 배분의 강건함을 기르는 단계입니다.*

### 8. 《앤티프래질》 - 나심 탈레브
- **핵심 교훈**: 무작위성과 외부 충격을 견디는 것을 넘어, 충격 속에서 오히려 더 단단해지는(Antifragile) 시스템의 설계 철학.
- **퀀트 어드바이스**: 봇이 직면할 극단적 거시경제 붕괴 속에서도 시스템 전체가 생존하고 성장하는 데 필요한 철학적 면역력을 제공합니다.

### 9. 《행운에 속지 마라》 - 나심 탈레브 (★차트 분석 책 대신 신규 긴급 투입!)
- **핵심 교훈**: 금융 시장의 대부분의 단기적 가격 흐름과 성공은 실력이 아닌 **'순수한 행운과 임의적 소음(Noise)'**에 불과하다는 가차 없는 일침.
- **퀀트 어드바이스**: 기존의 차트 분석 교본(존 머피 저)을 읽으면 오히려 차트를 보고 종목을 사고팔고 싶은 인간의 투기 본능이 되살아납니다. 이 책은 시장 가격의 움직임을 소음으로 규정함으로써, 차트 예측을 하려는 시도 자체가 얼마나 헛된 일인지 철저하게 깨부수고 자동 매매 규칙에 더 안주하게 해줍니다.

### 10. 《가치투자 실전 매뉴얼》 - 웨슬리 그레이, 토비아스 카을리 (★V3 최종 정교화 단계 배치)
- **핵심 교훈**: 인간의 감정적 편향을 이기기 위해 가치 지표를 계량화하여 정량적으로만 투자하는 시스템의 우월성.
- **퀀트 어드바이스**: 1~9권까지의 과정을 통해 멘탈과 철학이 완성된 시점에서, 다시 한번 퀀트 공식의 통계적 우월함을 논리적으로 정리하며 장기 투자의 마침표를 찍습니다.
"""

    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Save local markdown file
    md_path = os.path.join(parent_dir, "퀀트_투자자를_위한_단계별_독서_로드맵_10선.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✅ [V3] 로컬 마크다운 파일 업데이트 성공: {md_path}")
    
    # 2. Convert to HTML for Google Doc import
    html_text = markdown.markdown(md_content, extensions=['extra'])
    html_path = md_path.replace('.md', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
    print(f"✅ [V3] 임시 HTML 파일 변환 성공: {html_path}")
    
    # 3. Authenticate and update Google Doc
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)
    
    media = MediaFileUpload(html_path, mimetype='text/html', resumable=True)
    
    print(f">> 구글 드라이브 문서 업데이트 중... ID: {file_id}")
    drive_service.files().update(fileId=file_id, media_body=media).execute()
    print("✅ [V3] 구글 문서 업데이트 성공!")
    
    return True

if __name__ == '__main__':
    file_id = "1ii7mLu_NrjQf5dWslxXC1-mzDB4Z4dx-ipeO9itKZas"
    try:
        update_gdoc(file_id)
    except Exception as e:
        print(f"🚨 구글 문서 업데이트 실패: {e}")
