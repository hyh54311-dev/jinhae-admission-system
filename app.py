import os
import json
import base64
from flask import Flask, request, jsonify
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Configure Google API Client libraries
HAS_GOOGLE_API = True
try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except ImportError:
    HAS_GOOGLE_API = False

def upload_to_google_drive(html_path, doc_title):
    if not HAS_GOOGLE_API:
        print("[WARNING] Google API libraries not installed. Skipping Google Doc upload.")
        return None
        
    token_path = os.path.join(DIRECTORY, 'token.json')
    if not os.path.exists(token_path):
        print("[WARNING] token.json not found. Skipping Google Doc upload.")
        return None
        
    try:
        # Load credentials from token.json
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("[WARNING] Google credentials invalid or expired. Skipping Google Doc upload.")
                return None
                
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Define metadata to upload and convert HTML to Google Doc format
        file_metadata = {
            'name': doc_title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        media = MediaFileUpload(html_path, mimetype='text/html', resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        file_id = file.get('id')
        link = file.get('webViewLink')
        
        # Share permission: anyone with link can view (standard viewer role)
        try:
            drive_service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
        except Exception as perm_ex:
            print(f"Warning: Failed to set permission for {doc_title}: {perm_ex}")
            
        print(f"[GOOGLE DRIVE SUCCESS] Created Google Doc: {doc_title} -> {link}")
        return link
    except Exception as e:
        print(f"[ERROR] Google Drive upload failed: {e}")
        return None

@app.route("/")
def index():
    # Serve the Admission Registration HTML file directly at the root URL
    html_path = os.path.join(DIRECTORY, "입학등록_웹앱_화면.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content

@app.route("/api/submit", methods=["POST"])
def submit():
    try:
        payload = request.get_json()
        student_name = payload.get("studentName", "Unknown")
        student_id = payload.get("studentId", "Unknown")
        school_name = payload.get("schoolName", "Unknown")
        birth_date = payload.get("birthDate", "Unknown")
        parent_name = payload.get("parentName", "Unknown")
        parent_phone = payload.get("parentPhone", "Unknown")
        
        student_sig_b64 = payload.get("studentSignature", "")
        parent_sig_b64 = payload.get("parentSignature", "")
        
        # Generate A4 formatted HTML with embedded base64 signature images (mix-blend overlay)
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>2027학년도 진해고등학교 입학등록확인서</title>
  <style>
    body {{
      font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
      display: flex;
      justify-content: center;
      padding: 40px 0;
      background-color: #f1f5f9;
    }}
    .page {{
      background-color: #ffffff;
      width: 210mm;
      height: 297mm;
      padding: 20mm;
      box-sizing: border-box;
      border: 1px solid #cbd5e1;
      position: relative;
    }}
    .border-box {{
      border: 2px solid #1c4587;
      width: 100%;
      height: 100%;
      box-sizing: border-box;
      padding: 50px 40px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .title-area {{
      text-align: center;
      margin-top: 20px;
    }}
    .title {{
      font-size: 26px;
      font-weight: bold;
      color: #1c4587;
      margin-bottom: 12px;
      font-family: sans-serif;
    }}
    .title-line {{
      height: 2.5px;
      background-color: #1c4587;
      width: 80%;
      margin: 0 auto;
    }}
    .info-table {{
      margin-left: auto;
      margin-right: 50px;
      margin-top: 60px;
      border-collapse: collapse;
      font-size: 16px;
    }}
    .info-table td {{
      padding: 10px 12px;
      vertical-align: middle;
    }}
    .info-label {{
      font-weight: bold;
      width: 130px;
      letter-spacing: 0.1em;
    }}
    .info-colon {{
      width: 15px;
      text-align: center;
      font-weight: bold;
    }}
    .info-value {{
      width: 200px;
      border-bottom: 1px solid #94a3b8;
      padding-left: 10px;
      font-size: 16px;
    }}
    .statement-area {{
      text-align: center;
      font-size: 17px;
      font-weight: bold;
      line-height: 1.8;
      margin: 60px 0;
      color: #000000;
    }}
    .date-area {{
      text-align: center;
      font-size: 16px;
      margin: 40px 0;
      font-weight: 500;
    }}
    .signature-area {{
      margin-left: auto;
      margin-right: 50px;
      margin-bottom: 50px;
      font-size: 16px;
    }}
    .sig-row {{
      display: flex;
      align-items: center;
      justify-content: flex-end;
      margin-bottom: 20px;
      gap: 15px;
    }}
    .sig-label {{
      width: 80px;
      font-weight: bold;
      letter-spacing: 0.2em;
    }}
    .footer-area {{
      text-align: center;
      font-size: 26px;
      font-weight: bold;
      color: #000000;
      margin-bottom: 30px;
      letter-spacing: 0.05em;
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="border-box">
      <div class="title-area">
        <div class="title">2027학년도 진해고등학교 입학등록확인서</div>
        <div class="title-line"></div>
      </div>
      
      <table class="info-table" border="0">
        <tr>
          <td class="info-label">접 수 번 호</td>
          <td class="info-colon">:</td>
          <td class="info-value">{student_id}</td>
        </tr>
        <tr>
          <td class="info-label">성&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;명</td>
          <td class="info-colon">:</td>
          <td class="info-value">{student_name}</td>
        </tr>
        <tr>
          <td class="info-label">출 신 중 학 교</td>
          <td class="info-colon">:</td>
          <td class="info-value">{school_name}</td>
        </tr>
        <tr>
          <td class="info-label">생 년 월 일</td>
          <td class="info-colon">:</td>
          <td class="info-value">{birth_date}</td>
        </tr>
      </table>
      
      <div class="statement-area">
        본인은 2027학년도 비평준화지역 일반고 입학전형에서<br>진해고등학교에 입학을 희망합니다.
      </div>
      
      <div class="date-area">
        2027년   1월   4일
      </div>
      
      <div class="signature-area">
        <div class="sig-row">
          <div class="sig-label">학  생 :</div>
          <div style="font-weight: 500; font-size: 16px; width: 100px; text-align: center; border-bottom: 1px solid #94a3b8; padding-bottom: 5px;">{student_name}</div>
          <div style="position: relative; width: 130px; height: 40px; display: inline-block; vertical-align: middle; border-bottom: 1px solid #94a3b8; padding-bottom: 5px; margin-left: 10px;">
            <span style="position: absolute; left: 10px; top: 10px; color: #64748b; font-size: 15px; z-index: 1;">(서명 또는 인)</span>
            <img src="{student_sig_b64}" style="position: absolute; left: 10px; top: -10px; width: 100px; height: 50px; z-index: 2; mix-blend-mode: multiply; opacity: 0.9;">
          </div>
        </div>
        
        <div class="sig-row" style="margin-top: 15px;">
          <div class="sig-label">보호자 :</div>
          <div style="font-weight: 500; font-size: 16px; width: 100px; text-align: center; border-bottom: 1px solid #94a3b8; padding-bottom: 5px;">{parent_name}</div>
          <div style="position: relative; width: 130px; height: 40px; display: inline-block; vertical-align: middle; border-bottom: 1px solid #94a3b8; padding-bottom: 5px; margin-left: 10px;">
            <span style="position: absolute; left: 10px; top: 10px; color: #64748b; font-size: 15px; z-index: 1;">(서명 또는 인)</span>
            <img src="{parent_sig_b64}" style="position: absolute; left: 10px; top: -10px; width: 100px; height: 50px; z-index: 2; mix-blend-mode: multiply; opacity: 0.9;">
          </div>
        </div>
      </div>
      
      <div class="footer-area">
        진해고등학교장 귀하
      </div>
    </div>
  </div>
</body>
</html>"""
        
        # Write HTML temporarily to Vercel writable /tmp directory
        temp_html_path = "/tmp/temp_confirmation.html"
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        doc_title = f"{student_id}_{student_name}_입학등록확인서"
        doc_link = upload_to_google_drive(temp_html_path, doc_title)
        
        # Cleanup temporary file
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
            
        return jsonify({
            "success": True, 
            "studentName": student_name,
            "docLink": doc_link
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
