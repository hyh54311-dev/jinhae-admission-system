# -*- coding: utf-8 -*-
import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'
creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/script.projects.readonly', 'https://www.googleapis.com/auth/drive'])

try:
    script_service = build('script', 'v1', credentials=creds)
    script_id = "1kgp-qF7pwekx_VZ_1kVZ4XMbNZGYbL_FlXOJI6E8UeUeoiCRQoE7Gtes"
    content = script_service.projects().getContent(scriptId=script_id).execute()
    print("Successfully fetched Apps Script project:")
    files = content.get('files', [])
    for f in files:
        print(f"- {f['name']} ({f['type']})")
        lines = f.get('source', '').split('\n')
        print("  First 15 lines:")
        for line in lines[:15]:
            print("   ", line)
except Exception as e:
    print(f"Error fetching script: {e}")
