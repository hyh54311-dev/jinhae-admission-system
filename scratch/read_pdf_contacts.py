import pdfplumber
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무 이외\연락망, 배치도\2026.3.5.자 교직원 비상연락처(휴직자포함 전체).pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            print(f"--- Page {i+1} ---")
            lines = text.split('\n')
            for line in lines:
                if any(k in line for k in ['보건', '행정', '교무', '전화', '번호', '연락처', '팩스']):
                    print(line.strip())
except Exception as e:
    print(f"Error reading PDF: {e}")
