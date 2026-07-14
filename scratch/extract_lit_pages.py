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

def find_textbook_page_offsets(pdf_path):
    log(f"Finding page offsets in {pdf_path}...")
    if not os.path.exists(pdf_path):
        log("File not found.")
        return None
        
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        total_pages = len(reader.pages)
        log(f"Total PDF pages: {total_pages}")
        
        # Search for "오발탄" or page number "258" to find printed page 258
        oval_page = None
        printed_258_idx = None
        
        for idx in range(total_pages):
            text = reader.pages[idx].extract_text()
            if not text:
                continue
            
            if "오발탄" in text:
                if oval_page is None:
                    oval_page = idx
                    log(f"Found '오발탄' at PDF page index {idx} (1-indexed: {idx+1})")
                    
            if re.search(r'\b258\b', text):
                printed_258_idx = idx
                log(f"Found printed page number '258' at PDF page index {idx} (1-indexed: {idx+1})")
                break # We have the starting point
                
        return {
            'oval_idx': oval_page,
            'printed_258_idx': printed_258_idx
        }
    except Exception as e:
        log(f"Error scanning PDF: {e}")
        return None

def extract_pages(src_pdf, dest_pdf, pages_to_extract):
    log(f"Extracting {len(pages_to_extract)} pages from {src_pdf} to {dest_pdf}...")
    try:
        reader = PyPDF2.PdfReader(src_pdf)
        writer = PyPDF2.PdfWriter()
        for p in pages_to_extract:
            writer.add_page(reader.pages[p])
        with open(dest_pdf, "wb") as f_out:
            writer.write(f_out)
        log("Extraction successful!")
        return True
    except Exception as e:
        log(f"Error during extraction: {e}")
        return False

def update_exam_schedule(dest_pdf_path):
    schedule_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\시험_출제_및_제출_일정.md"
    if not os.path.exists(schedule_path):
        log("Exam schedule file not found. Skipping MD update.")
        return
        
    try:
        with open(schedule_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        target = "### 🎬 2학년 문학 (1차고사 기준)"
        if target in content:
            replacement = target + f"\n*   **시험 범위 (교과서, PPT, 학습지 포함)**:\n    *   단원: 3단원 역사와 함께 흐르는, 문학\n    *   오발탄 (이범선): 교과서 258 ~ 266페이지\n    *   대설주의보 (최승호) & 새들도 세상을 뜨는구나 (황지우): 교과서 267 ~ 272페이지\n    *   *추출된 교과서 PDF*: [2학년 문학 교과서 시험범위(오발탄, 대설주의보).pdf](file:///d:/OneDrive%20-%20%EA%B2%BD%EC%83%81%EB%82%A8%EB%8F%84%EA%B5%90%EC%9C%A1%EC%B2%AD/%EB%B0%94%ED%83%95%20%ED%99%94%EB%A9%B4/%EC%A7%84%ED%95%B4%EA%B3%A0%EB%93%B1%ED%95%99%EA%B5%90/2026%ED%95%99%EB%85%84%EB%8F%84/antigravity_folder/2%ED%95%99%EB%85%84%20%EB%AC%B8%ED%95%99%20%EA%B5%90%EA%B3%BC%EC%84%9C%20%EC%8B%9C%ED%97%98%EB%B2%94%EC%9C%84(%EC%98%A4%EB%B0%9C%ED%83%84,%20%EB%8C%80%EC%84%A4%EC%A3%BC%EC%9D%98%EB%B3%B4).pdf)"
            content = content.replace(target, replacement)
            
            with open(schedule_path, "w", encoding="utf-8") as f_out:
                f_out.write(content)
            log("Successfully updated 시험_출제_및_제출_일정.md with exam scope!")
    except Exception as e:
        log(f"Error updating MD file: {e}")

if __name__ == "__main__":
    src_pdf = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 2학년 수업&수행&평가\1학기\2학년 문학\학생용 교과서\[비상교육] 고등_문학(강호영)_교과서_3. 역사와 함께 흐르는, 문학.pdf"
    dest_pdf = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\2학년 문학 교과서 시험범위(오발탄, 대설주의보).pdf"
    
    offsets = find_textbook_page_offsets(src_pdf)
    if offsets:
        # We need printed 258 to 272
        ref_idx = offsets['printed_258_idx']
        if ref_idx is None:
            # Fallback to oval_idx which is typically page 258
            ref_idx = offsets['oval_idx']
            
        if ref_idx is not None:
            # Check what page number was printed on ref_idx
            # Often the chapter starts at page 200 or 150.
            # In the 3rd chapter PDF, the first page might be printed page 140 or so.
            # Let's extract the actual printed number to find the exact offset.
            reader = PyPDF2.PdfReader(src_pdf)
            text_ref = reader.pages[ref_idx].extract_text()
            # Find the number 258 to verify
            # Let's check offset
            # Assuming printed_258_idx corresponds to page 258:
            offset = ref_idx - 258
            log(f"Calculated page offset (PDF index - printed page): {offset}")
            
            # Extract 258 to 272 (total 15 pages)
            pages_to_extract = []
            for p in range(258, 273):
                pages_to_extract.append(p + offset)
                
            success = extract_pages(src_pdf, dest_pdf, pages_to_extract)
            if success:
                update_exam_schedule(dest_pdf)
        else:
            log("Could not locate starting page index. Extraction aborted.")
