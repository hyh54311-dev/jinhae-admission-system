import os
import pypdfium2 as pdfium

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def log(msg):
    print(msg.encode('utf-8', errors='replace').decode('utf-8'))

def find_source():
    pdf_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 고사\3학년 1학기고사\중간고사\황요한 출제\2026학년도 1학기 1차고사 화법과작문 지필평가원안.pdf"
    log(f"Searching question 9 source in {pdf_path}...")
    
    if not os.path.exists(pdf_path):
        log("File not found.")
        return
        
    try:
        doc = pdfium.PdfDocument(pdf_path)
        log(f"Total Pages: {len(doc)}")
        
        full_text = ""
        for idx, page in enumerate(doc):
            textpage = page.get_textpage()
            text = textpage.get_text_range()
            log(f"\n--- Page {idx+1} ---")
            log(text[:1500]) # Log first 1500 chars of each page to see what's on it
            full_text += text
            
        # Search for "가정맹" or "9" or "서술형 9"
        log("\n--- Searching for keywords ---")
        keywords = ["가정맹", "서술형 9", "서술형9", "현관", "猛於虎"]
        for kw in keywords:
            if kw in full_text:
                pos = full_text.find(kw)
                log(f"Keyword '{kw}' found at character position {pos}")
                start = max(0, pos - 200)
                end = min(len(full_text), pos + 400)
                log(f"Context:\n{full_text[start:end]}")
                
    except Exception as e:
        log(f"Error: {e}")

if __name__ == "__main__":
    # Check check_pdf_header.py execution too (runs synchronously)
    header_script = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\check_pdf_header.py"
    if os.path.exists(header_script):
        log("\n=== Executing check_pdf_header.py synchronously ===")
        os.system(f"python {header_script}")
        
    find_source()
