import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive'])
    
    if not creds:
        print("Credentials not found.")
        return
        
    try:
        service = build('docs', 'v1', credentials=creds)
        doc_id = '1UkV1Vc_8m_vO7bzhS5JpjE4SwIZu8Ocs24rS7PPX5EE'
        document = service.documents().get(documentId=doc_id).execute()
        
        # Extracted text
        text = ""
        for content in document.get('body').get('content'):
            if 'paragraph' in content:
                for element in content.get('paragraph').get('elements'):
                    if 'textRun' in element:
                        text += element.get('textRun').get('content')
        
        # Save to local file to examine
        with open('temp_gdoc_content.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Successfully written to temp_gdoc_content.txt")
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == '__main__':
    main()
