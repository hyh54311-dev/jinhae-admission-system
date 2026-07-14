import os, sys, io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except:
        pass

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE_DIR = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"

def auth():
    token_path = os.path.join(BASE_DIR, 'token.json')
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

HTML = """\
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: '맑은 고딕', Arial, sans-serif; font-size: 9.5pt; color: #1a1a1a; line-height: 1.55; margin: 30px; }
  h1 { font-size: 16pt; color: #1a3a5c; border-bottom: 2.5px solid #1a3a5c; padding-bottom: 6px; margin-bottom: 4px; }
  h2 { font-size: 12pt; color: #2563eb; margin: 22px 0 8px 0; padding: 4px 0 4px 10px; border-left: 4px solid #2563eb; }
  h3 { font-size: 10.5pt; color: #374151; margin: 14px 0 6px 0; }
  hr { border: none; border-top: 1px solid #d1d5db; margin: 16px 0; }

  /* 공통 테이블 */
  table { border-collapse: collapse; width: 100%; margin: 6px 0 14px 0; font-size: 9pt; }
  th, td { border: 1px solid #c8ccd0; padding: 4px 7px; vertical-align: top; }
  th { background: #eef2f7; color: #1a3a5c; font-weight: bold; text-align: center; white-space: nowrap; }
  td { text-align: left; }

  /* 개요 테이블 - 2열 key-value */
  .overview th { width: 110px; text-align: right; background: #f0f4fa; white-space: nowrap; }
  .overview td { font-weight: normal; }
  .overview .accent { color: #dc2626; font-weight: bold; }

  /* 일정 테이블 */
  .schedule td:nth-child(1) { text-align: center; white-space: nowrap; font-weight: bold; }
  .schedule td:nth-child(2) { text-align: center; white-space: nowrap; width: 30px; }
  .schedule td:nth-child(4) { font-size: 8.5pt; color: #555; white-space: nowrap; }

  /* 상태 뱃지 */
  .done { color: #16a34a; font-weight: bold; }
  .wait { color: #d97706; }
  .pin  { color: #dc2626; font-weight: bold; }

  .note { background: #f9fafb; border-left: 3px solid #93c5fd; padding: 7px 10px; margin: 8px 0; font-size: 9pt; color: #374151; }
  .warn { background: #fef9ee; border-left: 3px solid #f59e0b; padding: 7px 10px; margin: 8px 0; font-size: 9pt; color: #92400e; }

  ul { margin: 4px 0; padding-left: 18px; }
  li { margin-bottom: 2px; }
</style>
</head>
<body>

<h1>2026. 경남대학교 마이크로디그리형 연수 종합 정리</h1>
<p style="color:#6b7280; font-size:8.5pt; margin-top:0;">출처: 진해고등학교-6362 (경상남도교육청 창의인재과) 공문 및 첨부 자료 &nbsp;|&nbsp; 정리일: 2026. 6. 26.</p>

<hr>

<h2>1. 연수 개요</h2>

<table class="overview">
<tr><th>연수명</th><td>지역 대학 연계 마이크로디그리형 연수</td></tr>
<tr><th>과정명</th><td>현장 실천형 디지털 활용 교수법과 수업디자인</td></tr>
<tr><th>연수기관</th><td>경남대학교 사범대학 부설 교육연수원</td></tr>
<tr><th>장소</th><td><b>경남대학교 월영캠퍼스 제1공학관 7층 USG첨단강의실</b></td></tr>
<tr><th>기간</th><td class="accent">2026. 7. 27.(월) ~ 8. 4.(화) &nbsp; 7일간(주말 제외)</td></tr>
<tr><th>이수시간</th><td class="accent">45시간 (3학점)</td></tr>
<tr><th>대상 / 인원</th><td>경남교육청 관내 초·중등 교사 (전 교과) &nbsp;/&nbsp; A·B반 각 15명, <b>총 30명</b></td></tr>
<tr><th>연수비</th><td><b>무료</b> (도교육청 전액 지원, 복무 = 출장·연수)</td></tr>
</table>

<table style="width:auto; margin-top:-6px;">
<tr>
  <th style="background:#eef2f7;">교시</th>
  <th style="background:#eef2f7;">1~2교시</th>
  <th style="background:#eef2f7;">3~4교시</th>
  <th style="background:#eef2f7;">5~7교시</th>
</tr>
<tr>
  <td style="text-align:center; font-weight:bold;">시간</td>
  <td style="text-align:center;">09:00~10:40</td>
  <td style="text-align:center;">10:50~12:30</td>
  <td style="text-align:center;">13:30~16:10</td>
</tr>
</table>

<hr>

<h2>2. 강의 일정</h2>

<h3>🅰 A반 (15명)</h3>
<table class="schedule">
<tr><th>일자</th><th>h</th><th>강의 내용</th><th>강사</th></tr>
<tr><td>7/27(월)</td><td>3</td><td>개원식(OT) 통합반 · 교육청 특강 · 전문가 특강</td><td>—</td></tr>
<tr><td>7/28(화)</td><td>7</td><td>패들렛 수업자료 제작 → 교실 참여 심화 → Gems·NotebookLM 업무 자동화</td><td>김광빈</td></tr>
<tr><td>7/29(수)</td><td>7</td><td>에듀테크 수업 혁신 + 생성형AI 수업자료·기록 활용 / 전문가 특강</td><td>김경규 / 석승준 교수</td></tr>
<tr><td>7/30(목)</td><td>7</td><td>망한 AI 수업 리디자인 워크숍 · ERRC → 교수평기 연계 설계 → AI 프로젝트 실전</td><td>김광빈</td></tr>
<tr><td>7/31(금)</td><td>7</td><td>AI Prompt Eng.(Gemini·Veo3.1) + 구글 도구(Extensions·Sites) / 저명인사 특강</td><td>김재현 / 김태훈 교수</td></tr>
<tr><td>8/3(월)</td><td>7</td><td>AI 업무 테크닉 + 클로드 데스크톱 자동화 + 생기부 AI 작성</td><td>김경규</td></tr>
<tr><td>8/4(화)</td><td>7</td><td>구글 워크스페이스(GCE·Brisk Teaching·대시보드·Apps Script 자동화)</td><td>이상우</td></tr>
</table>

<h3>🅱 B반 (15명)</h3>
<table class="schedule">
<tr><th>일자</th><th>h</th><th>강의 내용</th><th>강사</th></tr>
<tr><td>7/27(월)</td><td>3</td><td>개원식(OT) 통합반 · 교육청 특강 · 전문가 특강</td><td>—</td></tr>
<tr><td>7/28(화)</td><td>7</td><td>AI 업무 테크닉 + 클로드 데스크톱 자동화 + 생기부 AI 작성</td><td>김경규</td></tr>
<tr><td>7/29(수)</td><td>7</td><td>AI Prompt Eng.(Gemini·Veo3.1) + 구글 도구(Extensions·Sites) / 전문가 특강</td><td>전효진 / 석승준 교수</td></tr>
<tr><td>7/30(목)</td><td>7</td><td>구글 워크스페이스(GCE·Brisk Teaching·대시보드·Apps Script 자동화)</td><td>이상우</td></tr>
<tr><td>7/31(금)</td><td>7</td><td>에듀테크 수업 혁신 + 생성형AI 수업자료·기록 활용 / 저명인사 특강</td><td>김경규 / 김태훈 교수</td></tr>
<tr><td>8/3(월)</td><td>7</td><td>패들렛 수업자료 제작 → 교실 참여 심화 → Gems·NotebookLM 업무 자동화</td><td>김광빈</td></tr>
<tr><td>8/4(화)</td><td>7</td><td>망한 AI 수업 리디자인 워크숍 · ERRC → 교수평기 연계 설계 → AI 프로젝트 실전</td><td>김광빈</td></tr>
</table>

<div class="note">A·B반은 <b>동일 강의</b>를 순서만 교차 배치합니다. 개원식(7/27)은 통합반 운영.</div>

<hr>

<h2>3. 학점 인정 (석사 학위 연계)</h2>
<table class="overview">
<tr><th>인정 학점</th><td>45시간 → 석사 이수 학점 중 <b>3학점</b></td></tr>
<tr><th>최대 인정</th><td>2회 이수 시 <b>최대 6학점</b> (동일 과정 불가)</td></tr>
<tr><th>연계 대학원</th><td>경남대 교육대학원 재교육과정</td></tr>
<tr><th>가능 전공</th><td>평생교육 · 상담심리 · 유아교육 · 국어교육 · 영어교육 · 수학교육 · 영양교육 · 체육교육 · <b>AI창의융합교육</b></td></tr>
</table>

<div class="warn">⚠ 대학원 등록·학점 인정 시 <b>NEIS 연수 이력이 삭제</b>됩니다. 삭제된 실적은 수료 여부와 무관하게 <b>복구 불가</b>합니다.</div>

<hr>

<h2>4. 선발 기준</h2>
<table>
<tr><th style="width:60px;">순위</th><th>기준</th></tr>
<tr><td style="text-align:center;">1순위</td><td>교육경력 순 (최대 10년 인정, 임용 전 경력 제외)</td></tr>
<tr><td style="text-align:center;">2순위</td><td>2022~2026학년도 담임/보직교사 경력</td></tr>
<tr><td style="text-align:center;">3순위</td><td>신청서 평가 (참여 의지·디지털 활용도·역량 개발 필요성·교육과정 연계성)</td></tr>
</table>
<div class="note">모집 인원 이내 신청 → 별도 심사 없이 지원 제한 검증 후 선발</div>

<hr>

<h2>5. 추진 일정</h2>
<table>
<tr><th>시기</th><th>내용</th><th style="width:70px;">상태</th></tr>
<tr><td>5. 26.</td><td>세부 운영계획 안내 (공문)</td><td class="done">✅ 완료</td></tr>
<tr><td>5. 26.~6. 8.</td><td>학교 신청·서류 제출</td><td class="done">✅ 완료</td></tr>
<tr><td>6월</td><td>대상자 선정·명단 안내</td><td class="wait">⏳ 진행 중</td></tr>
<tr><td>6~7월</td><td>수강생 등록</td><td class="wait">⏳ 예정</td></tr>
<tr><td>7월</td><td>연수 사업 협약</td><td class="wait">⏳ 예정</td></tr>
<tr><td><b>7. 27.~8. 4.</b></td><td><b>마이크로디그리형 연수 실시</b></td><td class="pin">📌 D-31</td></tr>
<tr><td>12월</td><td>연수 결과보고서 제출</td><td class="wait">⏳ 예정</td></tr>
</table>

<hr>

<h2>6. 신청 현황 (황요한)</h2>
<table class="overview">
<tr><th>신청 과정</th><td>경남대 연수과정: 현장 실천형 디지털 활용 교수법과 수업디자인</td></tr>
<tr><th>소속</th><td>진해고등학교 교사</td></tr>
<tr><th>교육경력</th><td>10년 (인정) &nbsp;/&nbsp; 담임·보직 0년</td></tr>
<tr><th>제출 서류</th><td>추천자 명단 ✅ · 학교장 추천서 ✅ · 연수 신청서 ✅ · 경력사항 출력 ✅ — <b>모두 제출 완료</b></td></tr>
</table>

</body>
</html>
"""

def main():
    creds = auth()
    drive = build('drive', 'v3', credentials=creds)

    html_path = os.path.join(BASE_DIR, '_microdegree_upload.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(HTML)

    # 기존 문서 삭제 후 새로 생성
    old_id = '1XAgn8f4X_uqR1I1zWOMIbTPPTiXNM_q_MdBAbwg5P68'
    try:
        drive.files().delete(fileId=old_id).execute()
        print("기존 문서 삭제 완료")
    except:
        pass

    meta = {'name': '2026. 경남대학교 마이크로디그리형 연수 종합 정리', 'mimeType': 'application/vnd.google-apps.document'}
    media = MediaFileUpload(html_path, mimetype='text/html', resumable=True)
    f = drive.files().create(body=meta, media_body=media, fields='id,webViewLink').execute()

    try:
        drive.permissions().create(fileId=f['id'], body={'type':'anyone','role':'reader'}).execute()
    except Exception as e:
        print(f"권한 설정 실패: {e}")

    try:
        os.remove(html_path)
    except:
        pass

    print(f"SUCCESS: {f['webViewLink']}")

if __name__ == '__main__':
    main()
