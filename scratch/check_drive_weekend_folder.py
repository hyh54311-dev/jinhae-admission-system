# -*- coding: utf-8 -*-
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive'])
service = build('drive', 'v3', credentials=creds)

folder_id = '1phqLh0I4iX5QEteNV-EYfoFwzo7YYe7U'
results = service.files().list(
    q=f"'{folder_id}' in parents and trashed = false",
    pageSize=20,
    orderBy="createdTime desc",
    fields="files(id, name, createdTime, webViewLink)"
).execute()

files = results.get('files', [])
print(f"Recent files in Google Drive weekend folder ({len(files)} files):")
for f in files:
    print(f"- {f['name']} (Created: {f['createdTime']}) -> Link: {f['webViewLink']}")
