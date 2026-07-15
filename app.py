import os
import json
import base64
import requests
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

# Helper to get or create a specific folder in Google Drive
def get_or_create_folder(drive_service, folder_name):
    try:
        # Search for folder with specified name
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = drive_service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        else:
            # Create folder if it doesn't exist
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = drive_service.files().create(body=file_metadata, fields='id').execute()
            print(f"[GOOGLE DRIVE FOLDER] Created Folder: {folder_name} (ID: {folder.get('id')})")
            return folder.get('id')
    except Exception as e:
        print(f"[ERROR] Failed to get or create folder {folder_name}: {e}")
        return None

# Helper to upload signature image to Drive and return direct download URL (needed for Google Doc import)
def upload_signature_image(drive_service, sig_b64, filename, folder_id):
    try:
        if not sig_b64 or "," not in sig_b64:
            return ""
            
        # Decode base64 signature image
        sig_data = base64.b64decode(sig_b64.split(",")[1])
        temp_path = f"/tmp/{filename}"
        with open(temp_path, "wb") as f:
            f.write(sig_data)
            
        # Save image inside the specified folder
        file_metadata = {
            'name': filename,
            'mimeType': 'image/png'
        }
        if folder_id:
            file_metadata['parents'] = [folder_id]
            
        media = MediaFileUpload(temp_path, mimetype='image/png', resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        
        # Share permission: anyone with link can view (reader) so Google Doc importer can fetch it
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        # Direct download link structure
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    except Exception as e:
        print(f"[ERROR] Failed to upload signature image {filename}: {e}")
        return ""

def upload_to_google_drive(html_path, doc_title, student_sig_b64, parent_sig_b64, student_id, student_name):
    if not HAS_GOOGLE_API:
        print("[WARNING] Google API libraries not installed. Skipping Google Doc upload.")
        return None
        
    token_json_str = os.environ.get("GOOGLE_TOKEN_JSON")
    creds = None
    if token_json_str:
        try:
            token_data = json.loads(token_json_str)
            creds = Credentials.from_authorized_user_info(token_data, ['https://www.googleapis.com/auth/drive'])
        except Exception as e:
            print(f"[WARNING] Failed to parse GOOGLE_TOKEN_JSON env var: {e}")
            creds = None
            
    if not creds:
        token_path = os.path.join(DIRECTORY, 'token.json')
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
            except Exception as e:
                print(f"[WARNING] Failed to load token.json file: {e}")
                
    if not creds:
        print("[WARNING] No valid Google credentials found. Skipping Google Doc upload.")
        return None
        
    try:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Get or create specific folder: "2027학년도_입학등록확인서_제출본"
        folder_name = "2027학년도_입학등록확인서_제출본"
        folder_id = get_or_create_folder(drive_service, folder_name)
        
        # 1) Upload signature images inside target folder first to get direct download links
        student_sig_url = upload_signature_image(
            drive_service, 
            student_sig_b64, 
            f"{student_id}_{student_name}_학생서명_임시.png",
            folder_id
        )
        parent_sig_url = upload_signature_image(
            drive_service, 
            parent_sig_b64, 
            f"{student_id}_{student_name}_보호자서명_임시.png",
            folder_id
        )
        
        # Read HTML file and replace placeholder URLs with direct download URLs
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        html_content = html_content.replace("PLACEHOLDER_STUDENT_SIG_URL", student_sig_url)
        html_content = html_content.replace("PLACEHOLDER_PARENT_SIG_URL", parent_sig_url)
        
        # Rewrite the resolved HTML to temp file
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Define metadata to upload and convert HTML to Google Doc format inside the folder
        file_metadata = {
            'name': doc_title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        if folder_id:
            file_metadata['parents'] = [folder_id]
            
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
        
        # Generate A4 formatted HTML using standard HTML Tables (Google Doc Import compatible)
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>2027학년도 진해고등학교 입학등록확인서</title>
  <style>
    @page {{
      size: A4;
      margin: 30pt 40pt;
    }}
  </style>
</head>
<body style="font-family: 'Malgun Gothic', 'Noto Sans KR', sans-serif; background-color: #ffffff; padding: 0; margin: 0;">
  
  <!-- Outer border box using standard table with 100% width and no min-height -->
  <table border="0" cellpadding="0" cellspacing="0" style="border: 2px solid #1c4587; width: 100%; max-width: 500pt; margin: 0 auto; border-collapse: collapse;">
    <tr>
      <td style="padding: 15px 20px; vertical-align: top;">
        
        <table border="0" cellpadding="0" cellspacing="0" style="width: 100%;">
          
          <!-- Title Header -->
          <tr>
            <td align="center" style="padding-top: 5px; padding-bottom: 10px;">
              <span style="font-size: 22px; font-weight: bold; color: #1c4587; letter-spacing: -0.01em;">2027학년도 진해고등학교 입학등록확인서</span>
              <div style="height: 2px; background-color: #1c4587; width: 90%; margin-top: 8px; overflow: hidden;"></div>
            </td>
          </tr>
          
          <!-- Info block (Right Aligned Table using 2-Column layout table) -->
          <tr>
            <td style="padding-top: 5px; padding-bottom: 10px;">
              <table border="0" cellpadding="0" cellspacing="0" style="width: 100%;">
                <tr>
                  <td style="width: 50%;"></td> <!-- Left Spacer Column -->
                  <td style="width: 50%;" align="right">
                    <table border="0" cellpadding="0" cellspacing="0" style="font-size: 14px; margin-right: 15px; text-align: left; width: 280px;">
                      <tr>
                        <td style="font-weight: bold; padding: 4px 0; width: 90px; letter-spacing: 0.1em;">접 수 번 호</td>
                        <td style="padding: 4px; font-weight: bold; width: 20px; text-align: center;">:</td>
                        <td style="border-bottom: 1px solid #94a3b8; width: 170px; padding: 4px; color: #334155;">{student_id}</td>
                      </tr>
                      <tr>
                        <td style="font-weight: bold; padding: 4px 0; width: 90px; letter-spacing: 0.2em;">성&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;명</td>
                        <td style="padding: 4px; font-weight: bold; width: 20px; text-align: center;">:</td>
                        <td style="border-bottom: 1px solid #94a3b8; width: 170px; padding: 4px; color: #334155;">{student_name}</td>
                      </tr>
                      <tr>
                        <td style="font-weight: bold; padding: 4px 0; width: 90px; letter-spacing: 0.1em;">출신중학교</td>
                        <td style="padding: 4px; font-weight: bold; width: 20px; text-align: center;">:</td>
                        <td style="border-bottom: 1px solid #94a3b8; width: 170px; padding: 4px; color: #334155;">{school_name}</td>
                      </tr>
                      <tr>
                        <td style="font-weight: bold; padding: 4px 0; width: 90px; letter-spacing: 0.1em;">생 년 월 일</td>
                        <td style="padding: 4px; font-weight: bold; width: 20px; text-align: center;">:</td>
                        <td style="border-bottom: 1px solid #94a3b8; width: 170px; padding: 4px; color: #334155;">{birth_date}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <!-- Pledge Statement -->
          <tr>
            <td align="center" style="font-size: 15px; font-weight: bold; line-height: 1.6; padding: 20px 0; color: #000000; text-align: center;">
              본인은 2027학년도 비평준화지역 일반고 입학전형에서<br>
              <span style="color: #1c4587;">진해고등학교</span>에 입학을 희망합니다.
            </td>
          </tr>
          
          <!-- Date -->
          <tr>
            <td align="center" style="font-size: 14px; font-weight: bold; padding: 10px 0; text-align: center; color: #000000;">
              2027년   1월   4일
            </td>
          </tr>
          
          <!-- Signature Block (Right Aligned Table using 2-Column layout table) -->
          <tr>
            <td style="padding-top: 10px; padding-bottom: 15px;">
              <table border="0" cellpadding="0" cellspacing="0" style="width: 100%;">
                <tr>
                  <td style="width: 45%;"></td> <!-- Left Spacer Column -->
                  <td style="width: 55%;" align="right">
                    <table border="0" cellpadding="0" cellspacing="0" style="font-size: 14px; margin-right: 15px; text-align: left; width: 300px;">
                
                <!-- Student Signature -->
                <tr>
                  <td style="font-weight: bold; padding: 6px 0; width: 70px; letter-spacing: 0.2em; font-size: 15px;">학&nbsp;&nbsp;&nbsp;생 :</td>
                  <td style="border-bottom: 1px solid #94a3b8; width: 90px; text-align: center; padding: 6px 5px; font-size: 15px;">{student_name}</td>
                  <td style="border-bottom: 1px solid #94a3b8; width: 120px; text-align: center; padding: 0 5px; vertical-align: middle;">
                    <img src="PLACEHOLDER_STUDENT_SIG_URL" width="100" height="35" style="display: block; margin: 0 auto; vertical-align: middle;">
                  </td>
                </tr>
                
                <!-- Parent Signature -->
                <tr>
                  <td style="font-weight: bold; padding: 6px 0; letter-spacing: 0.2em; font-size: 15px;">보호자 :</td>
                  <td style="border-bottom: 1px solid #94a3b8; width: 90px; text-align: center; padding: 6px 5px; font-size: 15px;">{parent_name}</td>
                  <td style="border-bottom: 1px solid #94a3b8; width: 120px; text-align: center; padding: 0 5px; vertical-align: middle;">
                    <img src="PLACEHOLDER_PARENT_SIG_URL" width="100" height="35" style="display: block; margin: 0 auto; vertical-align: middle;">
                  </td>
                </tr>
                
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <!-- Dean Seal/Name -->
          <tr>
            <td align="center" style="font-size: 20px; font-weight: bold; color: #000000; padding-top: 15px; padding-bottom: 5px; text-align: center; letter-spacing: 0.05em;">
              진해고등학교장 귀하
            </td>
          </tr>
          
        </table>
        
      </td>
    </tr>
  </table>
  
</body>
</html>"""
        
        # Write HTML temporarily to Vercel writable /tmp directory
        temp_html_path = "/tmp/temp_confirmation.html"
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        doc_title = f"{student_id}_{student_name}_입학등록확인서"
        # Call Google Drive API with signature URLs replacement flow
        doc_link = upload_to_google_drive(
            temp_html_path, 
            doc_title, 
            student_sig_b64, 
            parent_sig_b64, 
            student_id, 
            student_name
        )
        
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

@app.route("/api/chat", methods=["POST"])
def chat_proxy():
    try:
        data = request.get_json()
        api_key = data.get("apiKey")
        model = data.get("model")
        contents = data.get("contents")
        
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
            
        if not api_key:
            return jsonify({"error": "API Key is missing"}), 400
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        response = requests.post(url, json={"contents": contents}, timeout=60)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
