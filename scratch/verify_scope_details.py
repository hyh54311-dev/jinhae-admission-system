import os
import re
import PyPDF2

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def log(msg):
    print(msg.encode('utf-8', errors='replace').decode('utf-8'))

def verify_file_for_keywords(pdf_path, keywords):
    log(f"\n--- Searching in: {pdf_path} ---")
    if not os.path.exists(pdf_path):
        log("File not found.")
        return
        
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        total_pages = len(reader.pages)
        log(f"Total Pages: {total_pages}")
        
        found = False
        for idx in range(total_pages):
            text = reader.pages[idx].extract_text()
            if not text:
                continue
            for kw in keywords:
                if kw in text:
                    log(f"Found '{kw}' at Page {idx+1} (index {idx})")
                    # Log snippet around keyword
                    pos = text.find(kw)
                    start = max(0, pos - 150)
                    end = min(len(text), pos + 150)
                    log("Snippet: " + text[start:end].replace('\n', ' '))
                    found = True
                    
        if not found:
            log("No keywords found in this file.")
    except Exception as e:
        log(f"Error reading {pdf_path}: {e}")

if __name__ == "__main__":
    keywords = ["가정맹어호", "苛政", "맹어호", "현관", "縣官"]
    
    # Files to search
    file_reading = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 고사\3학년 1학기고사\중간고사\시험범위\2027 수능특강 독서.pdf"
    file_short = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 고사\3학년 1학기고사\중간고사\시험범위\54-57페이지.pdf"
    
    verify_file_for_keywords(file_reading, keywords)
    verify_file_for_keywords(file_short, keywords)
