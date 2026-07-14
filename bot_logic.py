import os
import requests
import google.generativeai as genai
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Gemini API Key
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

def download_file_from_google_drive(file_url: str, output_path: str):
    """Downloads a public file from Google Drive."""
    try:
        # Extract File ID from the shared link
        if "file/d/" in file_url:
            file_id = file_url.split("file/d/")[1].split("/")[0]
        elif "id=" in file_url:
            file_id = file_url.split("id=")[1].split("&")[0]
        else:
            raise ValueError("Invalid Google Drive URL format.")

        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(download_url)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def get_answer_from_gemini(user_query: str, pdf_urls: List[str]):
    """
    Downloads PDFs, uploads them to Gemini File API, and generates a response.
    """
    model = genai.GenerativeModel("gemini-3.1-flash-lite") # ?ъ슜??吏移⑥뿉 ?곕씪 2.5 Flash 紐⑤뜽濡??듭씪
    files_to_upload = []

    try:
        for i, url in enumerate(pdf_urls):
            temp_filename = f"temp_pdf_{i}.pdf"
            if download_file_from_google_drive(url, temp_filename):
                # Upload to Gemini File API
                uploaded_file = genai.upload_file(path=temp_filename, display_name=f"PDF_{i}")
                files_to_upload.append(uploaded_file)
                # Cleanup local temp file
                os.remove(temp_filename)

        # Generate content with prompt and files
        prompt = [
            f"Please answer the user's question based on the provided PDF documents. "
            f"If the answer is not in the documents, say you don't know politely. "
            f"Answer in Korean.",
            user_query
        ]
        prompt.extend(files_to_upload)

        response = model.generate_content(prompt)

        # Cleanup Gemini Files (Optional, they expire in 48h anyway)
        # for f in files_to_upload:
        #    genai.delete_file(f.name)

        return response.text

    except Exception as e:
        return f"?ㅻ쪟媛 諛쒖깮?덉뒿?덈떎: {str(e)}"

# Example Usage:
# print(get_answer_from_gemini("???뚯씪???댁슜???붿빟?댁쨾.", ["DRIVE_LINK_HERE"]))
