import os
import sys
import io
import pdfplumber
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

def download_file(service, file_id, dest_path):
    print(f"Downloading {file_id} to {dest_path}...")
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    with open(dest_path, 'wb') as f:
        f.write(fh.read())
    print("Download complete.")

def extract_pdf_text(pdf_path):
    print(f"Extracting text from {pdf_path}...")
    text_content = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                text_content.append(f"--- Page {page_idx+1} ---\n{text}")
    return "\n".join(text_content)

def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json not found")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=creds)
    
    files_to_download = {
        "evaluation_plan.pdf": "1pAGuj7heP2rBxgYdZge9ONbYpe6V-k60",
        "date_expectations.pdf": "1zaJwur4UMMhwuk8lOdTwCYZG0mdwi0l0"
    }
    
    for filename, file_id in files_to_download.items():
        dest_path = os.path.join("scratch", filename)
        try:
            download_file(service, file_id, dest_path)
            extracted_text = extract_pdf_text(dest_path)
            
            output_txt_path = os.path.join("scratch", filename.replace(".pdf", "_extracted.txt"))
            with open(output_txt_path, "w", encoding="utf-8") as f:
                f.write(extracted_text)
            print(f"Saved extracted text to {output_txt_path}")
            
            # Print the first 1000 characters
            print(f"Preview of {filename}:")
            print(extracted_text[:2000])
            print("="*40)
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == '__main__':
    main()
