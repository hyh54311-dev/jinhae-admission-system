import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    token_path = r'd:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\token.json'
    
    if not os.path.exists(token_path):
        print(f"Error: {token_path} not found.")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    service = build('drive', 'v3', credentials=creds)

    print("Searching Drive for loan-related documents (excluding media)...")
    keywords = ['3억', '350', '대출', '자금', '이사', '누나', '계획']
    query = " or ".join([f"name contains '{kw}'" for kw in keywords])
    
    results = service.files().list(
        q=query,
        orderBy="modifiedTime desc",
        fields="files(id, name, webViewLink, modifiedTime, mimeType)",
        pageSize=100
    ).execute()
    
    files = results.get('files', [])
    filtered_files = [f for f in files if f['mimeType'] not in ['video/3gpp', 'image/jpeg', 'audio/mp4', 'audio/mpeg', 'video/mp4']]
    
    print(f"Found {len(filtered_files)} filtered files:")
    for f in filtered_files:
        print(f"- {f['name']} | {f['mimeType']} | {f['modifiedTime']} | {f['webViewLink']}")

if __name__ == '__main__':
    main()
