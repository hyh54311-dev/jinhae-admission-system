import os
import PyPDF2

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def log(msg):
    print(msg.encode('utf-8', errors='replace').decode('utf-8'))

def check_header():
    pdf_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 고사\3학년 1학기고사\중간고사\시험범위\54-57페이지.pdf"
    if not os.path.exists(pdf_path):
        log("File not found.")
        return
        
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        log(f"Total Pages: {len(reader.pages)}")
        first_page_text = reader.pages[0].extract_text()
        log("=== Page 1 Header text (first 800 chars) ===")
        log(first_page_text[:800])
    except Exception as e:
        log(f"Error: {e}")

if __name__ == "__main__":
    check_header()
