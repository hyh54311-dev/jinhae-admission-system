import pdfplumber
import os
import glob
import re
import json

def extract_plan_info(pdf_path):
    info = {
        "teacher": "", "datetime": "", "location": "",
        "target": "", "subject": "", "topic": ""
    }
    
    # Extract teacher name from filename
    filename = os.path.basename(pdf_path)
    match = re.search(r'\(([^)]+)\)\.pdf', filename)
    if not match: match = re.search(r'([가-힣]{2,4})\.pdf', filename)
    info['teacher'] = match.group(1) if match else "미상"

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Usually the info is on the first page
            page = pdf.pages[0]
            
            # Try extracting tables first
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Filter None
                    row_text = [str(cell).strip().replace('\n', '') for cell in row if cell]
                    row_joined = "".join(row_text)
                    
                    if "일시" in row_joined:
                        for text in row_text:
                            if "일시" not in text and text: info['datetime'] = text; break
                    if "장소" in row_joined:
                        for text in row_text:
                            if "장소" not in text and text: info['location'] = text; break
                    if "대상" in row_joined:
                        for text in row_text:
                            if "대상" not in text and text: info['target'] = text; break
                    if "과목" in row_joined:
                        for text in row_text:
                            if "과목" not in text and text: info['subject'] = text; break
                    if "단원" in row_joined or "주제" in row_joined:
                        for text in row_text:
                            if "단원" not in text and "주제" not in text and text: info['topic'] = text; break
            
            # If any info is still missing, try raw text parsing
            text = page.extract_text()
            if text:
                if not info['datetime']:
                    m = re.search(r'일\s*시\s*[:]?\s*(.*?)(?=\n|$)', text)
                    if m: info['datetime'] = m.group(1).strip()
                if not info['location']:
                    m = re.search(r'장\s*소\s*[:]?\s*(.*?)(?=\n|$)', text)
                    if m: info['location'] = m.group(1).strip()
                if not info['target']:
                    m = re.search(r'대\s*상\s*[:]?\s*(.*?)(?=\n|$)', text)
                    if m: info['target'] = m.group(1).strip()
                if not info['subject']:
                    m = re.search(r'과\s*목\s*[:]?\s*(.*?)(?=\n|$)', text)
                    if m: info['subject'] = m.group(1).strip()
                if not info['topic']:
                    m = re.search(r'(?:단\s*원|주\s*제)\s*[:]?\s*(.*?)(?=\n|$)', text)
                    if m: info['topic'] = m.group(1).strip()
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        
    return info

def extract_feedback_info(pdf_path):
    filename = os.path.basename(pdf_path)
    match = re.search(r'\(([^)]+)\)', filename)
    teacher = match.group(1) if match else "미상"
    
    strengths = []
    suggestions = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            
            # Use regex to find sections "수업의 장점" and "제언"
            # It's tricky because of varying formats. Let's look for keywords.
            parts = re.split(r'수업의?\s*장점|배울\s*점|좋았던\s*점', text)
            if len(parts) > 1:
                after_strength = parts[-1]
                subparts = re.split(r'제언|아쉬운\s*점|바라는\s*점|참관\s*소감', after_strength)
                strengths.append(subparts[0].strip())
                if len(subparts) > 1:
                    suggestions.append(subparts[1].strip())
            else:
                # If splitting didn't work, maybe just try extracting tables for feedback too
                for page in pdf.pages:
                    for table in page.extract_tables():
                        for row in table:
                            row_text = [str(cell).strip() for cell in row if cell]
                            row_joined = "".join(row_text).replace('\n', '')
                            if "장점" in row_joined:
                                for cell in row_text:
                                    if "장점" not in cell and cell: strengths.append(cell)
                            if "제언" in row_joined:
                                for cell in row_text:
                                    if "제언" not in cell and cell: suggestions.append(cell)
                                    
    except Exception as e:
        print(f"Error processing feedback {filename}: {e}")
        
    # Clean up
    s_text = " / ".join([s for s in strengths if s and len(s)>3]).replace('\n', ' ').strip()
    s_text = re.sub(r'\s+', ' ', s_text)
    
    sugg_text = " / ".join([s for s in suggestions if s and len(s)>3]).replace('\n', ' ').strip()
    sugg_text = re.sub(r'\s+', ' ', sugg_text)
    
    return {
        "teacher": teacher,
        "strengths": s_text,
        "suggestions": sugg_text
    }

def main():
    plan_folder = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 나눔의 날\국어과"
    obs_folder = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록"
    
    plans = []
    for f in glob.glob(os.path.join(plan_folder, "*.pdf")):
        plans.append(extract_plan_info(f))
        
    plans.sort(key=lambda x: x.get('teacher', ''))

    feedbacks = []
    for f in glob.glob(os.path.join(obs_folder, "*참관록*.pdf")):
        feedbacks.append(extract_feedback_info(f))

    data = {"plans": plans, "feedbacks": feedbacks}
    with open(r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\pdf_extracted_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
