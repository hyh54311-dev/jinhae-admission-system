import os
import sys
import io
import requests

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def main():
    url = "https://script.google.com/macros/s/AKfycbx7svjAJ03_YAbvn6HD7etnqfSXmDOjJ7D2erUNnDpAi6PpGbfdgQhdY09En7wdcyy9/exec"
    token_path = 'token.json'
    
    headers = {}
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        headers["Authorization"] = f"Bearer {creds.token}"
        
    print(f"Fetching WebApp URL: {url}")
    res = requests.get(url, headers=headers, allow_redirects=True)
    print(f"Status Code: {res.status_code}")
    print(f"Final URL: {res.url}")
    
    snippet = res.text[:2000]
    print("\n--- Content Snippet ---")
    print(snippet)

if __name__ == '__main__':
    main()
