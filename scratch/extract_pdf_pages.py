import os
import re
import PyPDF2

# Reconfigure stdout to prevent encoding errors on Windows console print
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def log(msg):
    print(msg.encode('utf-8', errors='replace').decode('utf-8'))

def find_pdf_page_offsets(pdf_path):
    log(f"Finding page offsets in {pdf_path}...")
    if not os.path.exists(pdf_path):
        log("File not found.")
        return None
        
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        total_pages = len(reader.pages)
        log(f"Total PDF pages: {total_pages}")
        
        # We will scan a few pages to find "갈래복합 05" or check page number match
        # Let's search for "갈래복합 05" in first 350 pages
        galrae_5_page = None
        galrae_9_page = None
        
        for idx in range(min(total_pages, 350)):
            text = reader.pages[idx].extract_text()
            if not text:
                continue
                
            # Look for "갈래복합" and see if 5, 9 are nearby
            if "갈래복합 05" in text or "갈래복합 5" in text or "갈래복합05" in text:
                galrae_5_page = idx
                log(f"Found '갈래복합 05' at PDF page index {idx} (1-indexed: {idx+1})")
            if "갈래복합 09" in text or "갈래복합 9" in text or "갈래복합09" in text:
                galrae_9_page = idx
                log(f"Found '갈래복합 09' at PDF page index {idx} (1-indexed: {idx+1})")
                
            # If we find both, we can break
            if galrae_5_page is not None and galrae_9_page is not None:
                break
                
        # Also try to map printed page number 267 to PDF page index
        # Usually, printed page number is at the corner.
        # Let's scan pages around index 260 to 280 to find printed "267"
        printed_267_idx = None
        for idx in range(250, min(total_pages, 300)):
            text = reader.pages[idx].extract_text()
            if not text:
                continue
            # Look for isolated "267"
            if re.search(r'\b267\b', text):
                printed_267_idx = idx
                log(f"Found printed page number '267' at PDF page index {idx} (1-indexed: {idx+1})")
                break
                
        return {
            'galrae_5_idx': galrae_5_page,
            'galrae_9_idx': galrae_9_page,
            'printed_267_idx': printed_267_idx
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

def update_exam_schedule(lit_scope_info):
    schedule_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\시험_출제_및_제출_일정.md"
    if not os.path.exists(schedule_path):
        log("Exam schedule file not found. Skipping MD update.")
        return
        
    try:
        with open(schedule_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # We will append the exam scope to 3학년 화법과 작문 section
        # Look for "### 📝 3학년 화법과 작문 (1차고사 기준)"
        target = "### 📝 3학년 화법과 작문 (1차고사 기준)"
        if target in content:
            replacement = target + f"\n*   **시험 범위 (수능특강 문학)**:\n    *   갈래복합 5, 6, 7번 (267 ~ 282페이지)\n    *   갈래복합 9번 (288 ~ 292페이지)\n    *   *추출된 PDF 파일*: [2027 수능특강 문학(267-282, 288-292).pdf](file:///d:/OneDrive%20-%20%EA%B2%BD%EC%83%81%EB%82%A8%EB%8F%84%EA%B5%90%EC%9C%A1%EC%B2%AD/%EB%B0%94%ED%83%95%20%ED%99%94%EB%A9%B4/%EC%A7%84%ED%95%B4%EA%B3%A0%EB%93%B1%ED%95%99%EA%B5%90/2026%ED%95%99%EB%85%84%EB%8F%84/antigravity_folder/2027%20%EC%88%98%EB%8A%A5%ED%8A%B9%EA%B0%95%20%EB%AC%B8%ED%95%99(267-282,%20288-292).pdf)"
            content = content.replace(target, replacement)
            
            with open(schedule_path, "w", encoding="utf-8") as f_out:
                f_out.write(content)
            log("Successfully updated 시험_출제_및_제출_일정.md with exam scope!")
    except Exception as e:
        log(f"Error updating MD file: {e}")

if __name__ == "__main__":
    src_pdf = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\2027 수능특강 문학 원본.pdf"
    dest_pdf = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\2027 수능특강 문학(267-282, 288-292).pdf"
    
    offsets = find_pdf_page_offsets(src_pdf)
    if offsets:
        # Determine the offset
        # Let's say printed page 267 is at PDF index X.
        # Then offset = X - 267.
        # Let's check printed_267_idx
        ref_idx = offsets['printed_267_idx']
        if ref_idx is None:
            # Fallback to galrae_5_idx (which corresponds to page 267)
            ref_idx = offsets['galrae_5_idx']
            
        if ref_idx is not None:
            offset = ref_idx - 267
            log(f"Calculated page offset (PDF index - printed page): {offset}")
            
            # Target pages (printed page to PDF page index)
            # 갈래복합 5~7: 267 to 282 -> PDF index: 267 + offset to 282 + offset
            # 갈래복합 9: 288 to 292 -> PDF index: 288 + offset to 292 + offset
            pages_to_extract = []
            for p in range(267, 283):
                pages_to_extract.append(p + offset)
            for p in range(288, 293):
                pages_to_extract.append(p + offset)
                
            # Perform extraction
            success = extract_pages(src_pdf, dest_pdf, pages_to_extract)
            if success:
                update_exam_schedule(dest_pdf)
        else:
            log("Could not determine page offset. Extraction aborted.")
