import os
import markdown
import time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

def auth():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("token.json is missing or invalid. Please re-authenticate.")
    return creds

def update_gdoc(doc_id, md_content):
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)

    # Convert markdown to html
    html_text = markdown.markdown(md_content, extensions=['extra', 'nl2br'])
    html_styled = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Malgun Gothic', 'Dotum', sans-serif; line-height: 1.6; color: #333333; }}
        h1 {{ color: #1e3a8a; border-bottom: 2px solid #3b82f6; padding-bottom: 8px; font-size: 20pt; }}
        h2 {{ color: #2563eb; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; font-size: 14pt; margin-top: 20px; }}
        ul {{ margin-bottom: 15px; }}
        li {{ margin-bottom: 5px; }}
        hr {{ border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0; }}
        blockquote {{ background-color: #f3f4f6; border-left: 5px solid #3b82f6; padding: 10px 15px; margin: 15px 0; }}
        pre {{ background-color: #f9fafb; border: 1px solid #e5e7eb; padding: 15px; border-radius: 5px; font-family: 'Consolas', monospace; white-space: pre-wrap; }}
    </style>
    </head>
    <body>
    {html_text}
    </body>
    </html>
    """

    html_path = 'temp_update.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_styled)

    try:
        media = MediaFileUpload(html_path, mimetype='text/html', resumable=True)
        updated_file = drive_service.files().update(
            fileId=doc_id,
            media_body=media
        ).execute()
        print("SUCCESS_UPDATE")
    except Exception as e:
        print(f"Error during Google Doc update: {e}")
    finally:
        time.sleep(0.5)
        if os.path.exists(html_path):
            try:
                os.remove(html_path)
            except Exception as e:
                print(f"Could not remove temporary html file: {e}")

if __name__ == '__main__':
    doc_id = '1UkV1Vc_8m_vO7bzhS5JpjE4SwIZu8Ocs24rS7PPX5EE'
    md_content = """# 🤖 [AI동행-책임·안전AI분과교육] 최종 확정 신청서 및 카카오톡 회신 양식

## 🏫 학교 정보 및 과정 신청 내역
* **학교명**: 진해고등학교
* **지도교사**: 황요한 선생님
* **대상 동아리**: 대신해 AI (1, 2학년 창체 동아리)
* **학생 수**: 14명
* **수업 장소**: 컴퓨터실 (전 회차 컴퓨터실에서 실습 및 평가 진행)
* **신청 과정**: 기초 과정 (선넘지 않는 AI 크리에이터)

---

## 📅 최종 확정 일정표 (16차시 / 6회차 완결)
> 본 일정은 지필평가, 여름방학, 공휴일 및 교내 행사를 완벽히 피하여 구성되었으며, **금요일 수업 없이 100% 월요일에만 완료**되는 가장 효율적이고 합리적인 최종 일정표입니다.  
> 전 회차 컴퓨터실을 예약 및 활용하여 실습 및 CBT 평가의 안정성을 극대화하였습니다.

* 📅 **1회차 (CBT 사전평가)**: **7월 6일 (월) 14:30 ~ 16:30 (2차시)** ➡️ 컴퓨터실 진행
* 📅 **2회차 (분과교육 1)**: **7월 20일 (월) 6-7-8교시 (3차시, 14:30 ~ 17:30)** ➡️ 컴퓨터실 진행
* 📅 **3회차 (분과교육 2)**: **8월 24일 (월) 6-7-8교시 (3차시, 14:30 ~ 17:30)** ➡️ 컴퓨터실 진행
* 📅 **4회차 (분과교육 3)**: **8월 31일 (월) 6-7-8교시 (3차시, 14:30 ~ 17:30)** ➡️ 컴퓨터실 진행
* 📅 **5회차 (분과교육 4)**: **9월 7일 (월) 6-7-8교시 (3차시, 14:30 ~ 17:30)** ➡️ 컴퓨터실 진행
* 📅 **6회차 (CBT 사후평가)**: **9월 14일 (월) 6-7교시 (2차시, 14:30 ~ 16:30)** ➡️ 컴퓨터실 진행

*(※ 교내 학사일정을 엄격히 준수하여 1학기말고사 및 직전 대비기간, 교육과정박람회(7/13), 여름방학 기간(7/22~8/11), 광복절 대체공휴일(8/17)을 모두 제외한 구성입니다.)*

---

## ✍️ 카카오톡 채널 전송용 텍스트 (복사 및 전송용)
> 아래의 텍스트를 그대로 복사(Ctrl + C)한 뒤, **맘이랜서 카카오톡 채널 대화창**에 붙여넣기(Ctrl + V)하여 전송해 주세요.

```text
♤ 학교: 진해고등학교
♤ 성함: 황요한
♤ 과정: 기초 (선넘지 않는 AI 크리에이터)
♤ 일정(16차시/수업시간 포함):
  - 1회차: 7월 6일 (월) 14:30 ~ 16:30 (2시간) *CBT 사전평가 (컴퓨터실 사용)
  - 2회차: 7월 20일 (월) 14:30 ~ 17:30 (3시간) (컴퓨터실 사용)
  - 3회차: 8월 24일 (월) 14:30 ~ 17:30 (3시간) (컴퓨터실 사용)
  - 4회차: 8월 31일 (월) 14:30 ~ 17:30 (3시간) (컴퓨터실 사용)
  - 5회차: 9월 7일 (월) 14:30 ~ 17:30 (3시간) (컴퓨터실 사용)
  (※ 여름방학 기간, 대체공휴일 및 교내 행사 일정 제외)
  - 6회차: 9월 14일 (월) 14:30 ~ 16:30 (2시간) *CBT 사후평가 (컴퓨터실 사용)
♤ 학생 수: 14명 (1, 2학년 창체동아리 '대신해 AI')
♤ 수업장소: 컴퓨터실 (전 회차 컴퓨터실에서 실습 및 평가 진행 예정)
```
"""
    update_gdoc(doc_id, md_content)
