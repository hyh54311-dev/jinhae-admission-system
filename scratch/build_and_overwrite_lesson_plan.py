import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8')

# 1. Setup paths
PARENT_FOLDER_ID = "1L407Q7d36HrcsSPMRWtNJ5b9MufC5k1A"
DAY4_FOLDER_NAME = "2026_경남대_마이크로디그리_4일차_이상우강사_수업자료"
LOCAL_DIR = r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\scratch"
TOKEN_PATH = r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\token.json"

# 2. Advanced Lesson Plan Text
advanced_plan_text = """[제미나이 x 노트북LM: 내 교실에 바로 쓰는 심화 융합 수업 기획안 (고도화 버전)]

"AI가 정답을 주는 대신, 아이들이 스스로 삶의 지혜와 비판적 사고를 발견하게 만드는 수업"

================================================================================
1. 수업 개요 및 철학
================================================================================
* 주제: 고등학교 2학년 문학 - 소설 <오발탄>(이범선)을 활용한 시대 연계 및 해학·풍자 시(Poetry) 변용 창작
* 슬로건: "암울한 현실의 '가자!'라는 절규를, 삶에 대한 희망과 해학의 웃음으로 재해석하다."
* 융합 도구: Google Gemini 3.1 (상상력 및 페르소나 대화) x Google NotebookLM (팩트체크 및 문학 이론 분석)

================================================================================
2. 4단계 깊이 있는(Deep Learning) 수업 고도화 설계
================================================================================

[1단계] ⏳ 시대적 맥락 확장: 1950년대 철호 vs 2026년 청년의 '듀얼 페르소나 대화'
* NotebookLM 환경 구축: 1950년대 전후 한국 사회(전쟁 직후 피난민, 청계천 판자촌, 인플레이션) 실제 역사 사료와, 2026년 현대 청년들이 느끼는 삶의 역경(경쟁, 주거, 미래 불안) 뉴스 데이터를 소스로 업로드.
* Gemini 시공간 대화: 학생들이 Gemini에게 '1950년대 오발탄 주인공 철호' 페르소나를 부여하고 2026년 고등학생의 관점에서 대화를 시도.
* 핵심 질문: "철호야, 70년 전 너의 '가자!'라는 절규와, 2026년을 살아가는 우리 청소년들의 고민은 어떻게 닮아있고 어떻게 다를까?"

[2단계] ⚖️ 비판적 사고 확장: 건강한 '풍자/해학' vs 단순한 '조롱/악플' 구별하기
* NotebookLM 검증: NotebookLM에 '건강한 풍자의 조건(사회적 부조리 비판 vs 개인 비하 조롱 구별)' 비평 가이드라인 업로드.
* 비판적 리라이팅(Critique): Gemini가 추천한 시 구절 중 단순 조롱으로 흐른 문장을 발췌하여 "이 표현은 긍정적 해학인가, 단순 조롱인가?"를 스스로 검증하고, 품격 있는 해학적 표현으로 직접 교정.

[3단계] 🎙️ 멀티모달 감성 확장: 완성된 시 ➔ NotebookLM 팟캐스트 & AI 음원 낭독
* NotebookLM Audio Overview: 학생이 완성한 시와 시 해설을 NotebookLM에 넣고 [오디오 팟캐스트]로 생성하여 두 AI가 이 시의 해학적 가치를 감동적으로 평론하도록 연출.
* AI 음원화: 시의 분위기에 맞게 1950년대 블루스/재즈 풍 또는 현대 포크/힙합 풍의 시 낭독 음원(Audio) 생성 및 학급 팟캐스트 구축.

[4단계] ❤️ 삶과의 연결: 나만의 '오발탄(방향을 잃은 순간)' 극복 헌정시 창작
* 자기 성찰 질문: "내 삶에서 방향을 잃었다고 느꼈던 moments(나의 오발탄 순간)은 언제였는가? 나는 그것을 어떤 웃음과 희망으로 넘어설 것인가?"
* 최종 산출물: 소설 <오발탄>을 주제로 한 진지함 70% + 해학 30%의 자전적 변용 시 1편 완성.

================================================================================
3. 모둠 교사 피드백 & 성찰 질문
================================================================================
* 생각할 거리: 아이들이 AI 답변을 그대로 복사하지 않고, 비판적으로 재검증하는 '생각 장치'가 마련되어 있는가?
* 삶과의 연결: 1950년대 고전 문학이 2026년 아이들의 실제 일상 및 마음의 상처와 진정성 있게 연결되었는가?
"""

# Save locally
md_save_path = os.path.join(LOCAL_DIR, "01_이상우강사_제미나이x노트북LM_융합수업기획안_오발탄_심화.md")
txt_save_path = os.path.join(LOCAL_DIR, "01_이상우강사_제미나이x노트북LM_융합수업기획안_오발탄_심화.txt")

with open(md_save_path, "w", encoding="utf-8") as f:
    f.write(advanced_plan_text)

with open(txt_save_path, "w", encoding="utf-8") as f:
    f.write(advanced_plan_text)

print("Saved advanced lesson plan locally.")

# 3. Google Drive Overwrite (Update)
creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/drive'])
service = build('drive', 'v3', credentials=creds)

# Find Day 4 folder ID
query = f"'{PARENT_FOLDER_ID}' in parents and name = '{DAY4_FOLDER_NAME}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
results = service.files().list(q=query, fields='files(id, webViewLink)').execute()
folders = results.get('files', [])

if folders:
    day4_folder_id = folders[0]['id']
    folder_link = folders[0].get('webViewLink')
else:
    folder_metadata = {
        'name': DAY4_FOLDER_NAME,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [PARENT_FOLDER_ID]
    }
    new_folder = service.files().create(body=folder_metadata, fields='id, webViewLink').execute()
    day4_folder_id = new_folder.get('id')
    folder_link = new_folder.get('webViewLink')

# Search for existing file in Day 4 folder to overwrite
file_query = f"'{day4_folder_id}' in parents and trashed = false"
existing_files = service.files().list(q=file_query, fields='files(id, name)').execute().get('files', [])

target_file_id = None
for ef in existing_files:
    if "오발탄" in ef['name'] or "수업기획안" in ef['name']:
        target_file_id = ef['id']
        print(f"Found existing file to overwrite: {ef['name']} (ID: {target_file_id})")
        break

media = MediaFileUpload(txt_save_path, mimetype='text/plain', resumable=False)

if target_file_id:
    # Overwrite existing file
    updated_file = service.files().update(
        fileId=target_file_id,
        media_body=media,
        fields='id, name, webViewLink'
    ).execute()
    print(f"✅ Successfully OVERWROTE existing Google Drive file: {updated_file.get('name')} (ID: {updated_file.get('id')})")
    file_link = updated_file.get('webViewLink')
else:
    # Create new file if not found
    file_metadata = {
        'name': '01_이상우강사_제미나이x노트북LM_융합수업기획안_오발탄_심화.txt',
        'parents': [day4_folder_id]
    }
    created_file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    print(f"Created file: {created_file.get('name')} (ID: {created_file.get('id')})")
    file_link = created_file.get('webViewLink')

print("\n=========================================")
print("OVERWRITE COMPLETE!")
print(f"FOLDER LINK: {folder_link}")
print(f"FILE LINK: {file_link}")
print("=========================================")
