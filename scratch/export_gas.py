import os
import sys
import io
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def export_script(service, file_id, name):
    print(f"Exporting Apps Script: {name} (ID: {file_id})")
    try:
        # Export Apps Script project as JSON
        url = f"https://script.googleapis.com/v1/projects/{file_id}/content"
        # We can use script service if script API is enabled, or use drive service export
        # Let's try drive service export first as it is simpler and uses drive scope
        request = service.files().export(fileId=file_id, mimeType='application/vnd.google-apps.script+json')
        content = request.execute()
        
        # Save JSON output
        parsed = json.loads(content)
        output_path = f"scratch/gas_{name}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        print(f"Successfully exported to {output_path}")
        
        # Also print file names and first few lines of each file
        files = parsed.get('files', [])
        print(f"Project contains {len(files)} files:")
        for idx, f in enumerate(files):
            print(f"  - File {idx+1}: {f['name']} ({f['type']})")
            
    except Exception as e:
        print(f"Error exporting {name}: {e}")
        print("Will try script API fallback...")
        try:
            # Try script API
            creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/script.projects.readonly'])
            script_service = build('script', 'v1', credentials=creds)
            content = script_service.projects().getContent(projectId=file_id).execute()
            output_path = f"scratch/gas_{name}_script_api.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            print(f"Successfully exported via Script API to {output_path}")
        except Exception as e2:
            print(f"Script API fallback failed: {e2}")

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=creds)
    
    # 1C4SmIseUA28iTVmYeYcteukRL9aXBcdcK_NvnuSILDjFwxfr4x6nrp1P - 매일 경제뉴스 생성
    export_script(service, "1C4SmIseUA28iTVmYeYcteukRL9aXBcdcK_NvnuSILDjFwxfr4x6nrp1P", "daily_news_gas")
    
    # 1kgp-qF7pwekx_VZ_1kVZ4XMbNZGYbL_FlXOJI6E8UeUeoiCRQoE7Gtes - 주말 경제 뉴스 생성
    export_script(service, "1kgp-qF7pwekx_VZ_1kVZ4XMbNZGYbL_FlXOJI6E8UeUeoiCRQoE7Gtes", "weekend_news_gas")

if __name__ == '__main__':
    main()
