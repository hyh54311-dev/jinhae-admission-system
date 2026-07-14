import http.server
import socketserver
import webbrowser
import os
import sys
import json
import base64

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Check if Google API dependencies are available
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    HAS_GOOGLE_API = True
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
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("[WARNING] Google credentials invalid or expired. Skipping Google Doc upload.")
                return None
                
        drive_service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': doc_title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        media = MediaFileUpload(html_path, mimetype='text/html', resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        file_id = file.get('id')
        link = file.get('webViewLink')
        
        # Share permission: anyone with link can view
        try:
            drive_service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
        except Exception as perm_ex:
            print(f"Warning: Failed to set permission for {doc_title}: {perm_ex}")
            
        print(f"\n[GOOGLE DRIVE SUCCESS] Created Google Doc: {doc_title}")
        print(f"  - Link: {link}\n")
        return link
    except Exception as e:
        print(f"[ERROR] Google Drive upload failed: {e}")
        return None

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve 입학등록_웹앱_화면.html for root path "/"
        if path == "/" or path == "":
            return os.path.join(DIRECTORY, "입학등록_웹앱_화면.html")
        return super().translate_path(path)

    def do_POST(self):
        if self.path == "/api/submit":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode('utf-8'))
                student_name = payload.get("studentName", "Unknown")
                student_id = payload.get("studentId", "Unknown")
                school_name = payload.get("schoolName", "Unknown")
                birth_date = payload.get("birthDate", "Unknown")
                parent_name = payload.get("parentName", "Unknown")
                parent_phone = payload.get("parentPhone", "Unknown")
                
                student_sig_b64 = payload.get("studentSignature", "")
                parent_sig_b64 = payload.get("parentSignature", "")
                
                # Setup output directories
                output_dir = os.path.join(DIRECTORY, "test_output")
                sig_dir = os.path.join(output_dir, "signatures")
                data_dir = os.path.join(output_dir, "data")
                
                os.makedirs(sig_dir, exist_ok=True)
                os.makedirs(data_dir, exist_ok=True)
                
                # Save student signature locally
                if student_sig_b64 and "," in student_sig_b64:
                    student_sig_data = base64.b64decode(student_sig_b64.split(",")[1])
                    student_sig_path = os.path.join(sig_dir, f"{student_id}_{student_name}_학생서명.png")
                    with open(student_sig_path, "wb") as f:
                        f.write(student_sig_data)
                        
                # Save parent signature locally
                if parent_sig_b64 and "," in parent_sig_b64:
                    parent_sig_data = base64.b64decode(parent_sig_b64.split(",")[1])
                    parent_sig_path = os.path.join(sig_dir, f"{student_id}_{student_name}_보호자서명.png")
                    with open(parent_sig_path, "wb") as f:
                        f.write(parent_sig_data)
                
                # Save beautiful print-ready signed HTML document locally (Strict replication of the PDF)
                html_doc_path = os.path.join(data_dir, f"{student_id}_{student_name}_입학등록확인서.html")
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
      width: 210mm; /* A4 width */
      height: 297mm; /* A4 height */
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
      font-family: 'Outfit', 'Noto Sans KR', sans-serif;
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
    .sig-img-container {{
      width: 120px;
      height: 50px;
      border-bottom: 1px solid #94a3b8;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .sig-img {{
      max-width: 100px;
      max-height: 45px;
    }}
    .sig-suffix {{
      width: 110px;
      color: #334155;
    }}
    .footer-area {{
      text-align: center;
      font-size: 26px;
      font-weight: bold;
      color: #000000;
      margin-bottom: 30px;
      letter-spacing: 0.05em;
    }}
    @media print {{
      body {{
        background-color: #ffffff;
        padding: 0;
      }}
      .page {{
        border: none;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="border-box">
      
      <!-- Title Header -->
      <div class="title-area">
        <div class="title">2027학년도 진해고등학교 입학등록확인서</div>
        <div class="title-line"></div>
      </div>
      
      <!-- Student Info Table -->
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
      
      <!-- Pledge Statement -->
      <div class="statement-area">
        본인은 2027학년도 비평준화지역 일반고 입학전형에서<br>진해고등학교에 입학을 희망합니다.
      </div>
      
      <!-- Form Submission Date -->
      <div class="date-area">
        2027년   1월   4일
      </div>
      
      <!-- Dual Signature Table -->
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
      
      <!-- Dean Seal/Name -->
      <div class="footer-area">
        진해고등학교장 귀하
      </div>
      
    </div>
  </div>
</body>
</html>"""
                with open(html_doc_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

                # Save application data summary text file
                data_path = os.path.join(data_dir, f"{student_id}_{student_name}_신청서.txt")
                with open(data_path, "w", encoding="utf-8") as f:
                    f.write("==================================================\n")
                    f.write("        2027학년도 입학등록확인서 제출 정보 (로컬 테스트)\n")
                    f.write("==================================================\n")
                    f.write(f"접수번호    : {student_id}\n")
                    f.write(f"학생 성명   : {student_name}\n")
                    f.write(f"출신중학교  : {school_name}\n")
                    f.write(f"생년월일    : {birth_date}\n")
                    f.write(f"보호자 성명 : {parent_name}\n")
                    f.write(f"보호자 연락처: {parent_phone}\n")
                    f.write("==================================================\n")
                
                print("\n[SUCCESS] Local test files saved successfully!")
                print(f"  - Signatures folder: {sig_dir}")
                print(f"  - Print-ready signed HTML doc: {html_doc_path}")
                print(f"  - Data summary file: {data_path}\n")
                
                # Attempt to upload to Google Drive as a converted Google Doc
                doc_title = f"{student_id}_{student_name}_입학등록확인서"
                doc_link = upload_to_google_drive(html_doc_path, doc_title)
                
                # Send JSON response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {
                    "success": True, 
                    "studentName": student_name,
                    "docLink": doc_link # Return the Google Doc URL if created, else None
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                print(f"\n[ERROR] Failed to save local files: {e}\n")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"success": False, "error": str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def main():
    # Change current working directory to the script's directory
    os.chdir(DIRECTORY)
    
    # Configure socket server
    Handler = CustomHTTPRequestHandler
    
    # Try different ports if 8080 is in use
    port = PORT
    for _ in range(5):
        try:
            with socketserver.TCPServer(("", port), Handler) as httpd:
                url = f"http://localhost:{port}/"
                print("==================================================")
                print("  2027 Admission Confirmation Web App Local Server")
                print(f"  Path: {DIRECTORY}")
                print(f"  URL: {url}")
                print("==================================================")
                print("Opening web browser...")
                
                # Open browser
                webbrowser.open(url)
                
                print("Server is running. Press Ctrl+C to stop.")
                httpd.serve_forever()
                break
        except OSError:
            print(f"Port {port} is in use. Trying the next port...")
            port += 1
            
if __name__ == "__main__":
    main()
