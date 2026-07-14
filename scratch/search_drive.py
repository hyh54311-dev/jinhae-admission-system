import os
import sys
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=creds)
    
    output_lines = []
    
    try:
        # Search 1: All Google Apps Script projects
        output_lines.append("=== Google Apps Script Projects ===")
        query_gas = "mimeType = 'application/vnd.google-apps.script' and trashed = false"
        results_gas = service.files().list(
            q=query_gas, 
            spaces='drive', 
            fields="files(id, name, mimeType, createdTime, modifiedTime)",
            pageSize=100
        ).execute()
        files_gas = results_gas.get('files', [])
        
        for idx, f in enumerate(files_gas):
            output_lines.append(f"[{idx+1}] {f['name']} | ID: {f['id']} | Modified: {f['modifiedTime']}")
            
        # Search 2: Files containing news/economy keywords
        output_lines.append("\n=== Keyword Search (news, economy, report, telegram) ===")
        keywords = ["뉴스", "news", "경제", "economy", "macro", "거시", "리포트", "report", "텔레그램", "telegram", "daily"]
        query_kw = " or ".join([f"name contains '{kw}'" for kw in keywords])
        query_kw = f"({query_kw}) and trashed = false"
        results_kw = service.files().list(
            q=query_kw, 
            spaces='drive', 
            fields="files(id, name, mimeType, createdTime, modifiedTime)",
            pageSize=100
        ).execute()
        files_kw = results_kw.get('files', [])
        
        for idx, f in enumerate(files_kw):
            output_lines.append(f"[{idx+1}] {f['name']} | ID: {f['id']} | Mime: {f['mimeType']} | Modified: {f['modifiedTime']}")
            
    except Exception as e:
        output_lines.append(f"Error searching drive: {e}")
        
    with open("scratch/search_drive_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print("Done. Saved results to scratch/search_drive_results.txt")

if __name__ == '__main__':
    main()
