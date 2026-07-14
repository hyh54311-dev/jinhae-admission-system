import os
import json
import requests
import urllib3
import httplib2
import threading
import subprocess
import pythoncom
import google_auth_httplib2
import win32com.client as win32
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 공식 구글 문서 템플릿 ID
DOC_ID = "1L7U7S__MwoRStH-vdllIit-FBn8_yoUTnHzBj6QxGWk"
TOKEN_FILE = "token.json"

def get_credentials():
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                session = requests.Session()
                session.verify = False
                creds.refresh(Request(session=session))
                return creds
        except Exception as e:
            print("Error:", e)
    return None

def run_hwp_com(hwp_path, template_text, results):
    try:
        # 서브 스레드에서 COM 객체를 다루기 위해 CoInitialize 호출
        pythoncom.CoInitialize()
        hwp = win32.gencache.EnsureDispatch('HWPFrame.HwpObject')
        # 창을 화면에 표시하여 필요 시 사용자가 확인할 수 있도록 함
        hwp.XHwpWindows.Item(0).Visible = True
        hwp.RegisterModule('FilePathCheckDLL', 'SecurityModule')
        hwp.SetMessageBoxMode(0x20000)  # 대화창 무시
        
        # 새 빈 문서 생성
        hwp.Clear(1)
        
        # 텍스트 삽입 액션 실행
        act = hwp.CreateAction("InsertText")
        pset = act.CreateSet()
        pset.SetItem("Text", template_text)
        act.Execute(pset)
        
        hwp.SaveAs(hwp_path, "HWP")
        hwp.Quit()
        results["success"] = True
    except Exception as e:
        results["error"] = str(e)
    finally:
        pythoncom.CoUninitialize()

def main():
    creds = get_credentials()
    if not creds:
        print("No credentials found.")
        return
        
    try:
        base_http = httplib2.Http(disable_ssl_certificate_validation=True)
        authorized_http = google_auth_httplib2.AuthorizedHttp(creds, http=base_http)
        drive_service = build("drive", "v3", http=authorized_http)
        
        # 1. DOCX 템플릿 다운로드 (로컬 백업 및 폴백용)
        print("Downloading docx template...")
        export_url = f"https://docs.google.com/document/d/{DOC_ID}/export?format=docx"
        headers = {"Authorization": f"Bearer {creds.token}"}
        response = requests.get(export_url, headers=headers, verify=False)
        current_dir = os.getcwd()
        docx_path = os.path.join(current_dir, "scratch", "template.docx")
        with open(docx_path, "wb") as f:
            f.write(response.content)
        print("Downloaded docx.")

        # 2. HWP 파일 생성용 템플릿 텍스트 정의
        template_text = (
            "진해고등학교 문학 심층 탐구 보고서 양식\n"
            "────────────────────────────────────────────────────────\n"
            "※ 본 양식은 구글 문서 사본을 복사하거나 다운로드하여 본인의 내용으로 채운 뒤, PDF 또는 한글 파일로 변환하여 문학 탐구 보고서 제출 웹앱을 통해 업로드해 주십시오.\n\n"
            "■ 학생 인적 사항 및 주제\n"
            " - 학년: 2학년\n"
            " - 학반 및 번호: [   ]반 [   ]번\n"
            " - 성명: [       ]\n"
            " - 희망 진로 (또는 관심 분야): [                     ]\n"
            " - 대상 문학 작품 및 저자: [                     ]\n"
            " - 탐구 주제 (제목): [                                                     ]\n"
            "────────────────────────────────────────────────────────\n\n"
            "■ 탐구 내용 서술부\n\n"
            "1. 탐구 동기 (수업 시간 배운 내용과의 연계)\n"
            "----------------------------------------------------------------------------------------\n"
            "💡 [안내문] 수업 중 어떤 대목, 개념, 시어 등에서 지적 호기심이 생겼는지 논리적으로 서술해 주세요.\n"
            "----------------------------------------------------------------------------------------\n"
            "\n"
            " 여기에 탐구 동기를 작성해 주세요.\n"
            "\n\n"
            "2. 탐구 내용 및 결과\n"
            "----------------------------------------------------------------------------------------\n"
            "💡 [안내문] 주제에 대해 스스로 탐구하고 도출해 낸 결과나 현대 사회적 비평 사례를 서술하세요. (관련 보건 통계나 공학 이론 등을 연계하면 신뢰도가 높아집니다.)\n"
            "----------------------------------------------------------------------------------------\n"
            "\n"
            " 여기에 탐구 내용 및 결과를 작성해 주세요.\n"
            "\n\n"
            "3. 탐구 과정 및 심화 노력 (도서/논문 등 독서)\n"
            "----------------------------------------------------------------------------------------\n"
            "💡 [안내문] RISS/DBpia에서 실제 검색한 키워드와 찾아본 논문명, 혹은 도서관에서 대출해 깊이 읽은 도서명(저자명)을 구체적인 학업적 장벽 극복 노력과 함께 서술하세요.\n"
            "----------------------------------------------------------------------------------------\n"
            "\n"
            " 여기에 탐구 과정 및 독서 내용을 작성해 주세요.\n"
            "\n\n"
            "4. 결론 및 느낀 점 (인식의 변화와 학업적 성장)\n"
            "----------------------------------------------------------------------------------------\n"
            "💡 [안내문] 탐구 후 나에게 일어난 문학적 관점의 변화나 진로 분야에서의 성찰적 학업 소명을 정리하세요.\n"
            "----------------------------------------------------------------------------------------\n"
            "\n"
            " 여기에 결론 및 느낀 점을 작성해 주세요.\n"
            "\n"
        )

        hwp_file_name = "문학_심층탐구보고서_양식.hwp"
        hwp_path = os.path.join(current_dir, "scratch", hwp_file_name)
        if os.path.exists(hwp_path):
            os.remove(hwp_path)

        # 3. HWP COM을 별도 스레드에서 타임아웃 5초로 실행 (먹통 현상 방지)
        print("Launching HWP COM Object in a timeout thread...")
        results = {"success": False, "error": None}
        hwp_thread = threading.Thread(target=run_hwp_com, args=(hwp_path, template_text, results))
        hwp_thread.start()
        hwp_thread.join(timeout=5.0)  # 최대 5초 대기

        success = results["success"]
        if hwp_thread.is_alive():
            print("HWP COM writing timed out (likely blocked by security dialog). Killing Hwp.exe...")
            subprocess.run("taskkill /F /IM Hwp.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if success:
            print("Successfully created native HWP file directly via HWP COM!")
        else:
            print(f"HWP generation failed (Error: {results['error']}) or timed out. Falling back to DOCX template.")
            hwp_file_name = "문학_심층탐구보고서_양식.docx"
            hwp_path = docx_path
            
        # 4. 파일 드라이브 업로드
        print("Uploading template file to Google Drive...")
        file_metadata = {
            "name": hwp_file_name,
            "mimeType": "application/x-hwp" if hwp_path.endswith(".hwp") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
        
        media = MediaFileUpload(
            hwp_path, 
            mimetype=file_metadata["mimeType"], 
            resumable=True
        )
        
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()
        
        file_id = uploaded_file.get("id")
        print(f"Uploaded File ID: {file_id}")
        
        # 5. 파일 공유 및 다운로드 주소 추출
        drive_service.permissions().create(fileId=file_id, body={"type": "anyone", "role": "reader"}).execute()
        hwp_download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        print("Upload success. Download link:", hwp_download_url)
        
        # 6. Index.html 업데이트
        html_path = "문학_탐구보고서_웹앱_Index.html"
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
            
        import re
        html = re.sub(
            r'var CONFIG_TEMPLATE_HWP = "[^"]+";',
            f'var CONFIG_TEMPLATE_HWP = "{hwp_download_url}";',
            html
        )
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
            
        print("Successfully updated Index.html with direct HWP template download link!")
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
