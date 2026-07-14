import sys
import os
import pdfplumber
from pyhwpx import Hwp

sys.stdout.reconfigure(encoding='utf-8')

files = [
    r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\창체 동아리\개인별 활동계획서(4.15.).hwpx",
    r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\쿨메신져 다운로드 파일\2026. 동아리 조직현황(발송용).hwpx",
    r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\쿨메신져 다운로드 파일\2026.교사개설 동아리 각반 안내.hwpx"
]

scratch_dir = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch"

hwp = Hwp()
hwp.set_visible(False)

for fp in files:
    if not os.path.exists(fp):
        print(f"File not found: {fp}")
        continue
    base = os.path.splitext(os.path.basename(fp))[0]
    pdf_path = os.path.join(scratch_dir, f"{base}.pdf")
    
    print(f"\n======================================")
    print(f"Converting to PDF: {os.path.basename(fp)}")
    print(f"======================================")
    
    try:
        hwp.open(fp)
        hwp.SaveAs(pdf_path, "PDF")
        print(f"Saved PDF to: {pdf_path}")
        
        # Now read using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Total pages: {len(pdf.pages)}")
            for page_idx, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                lines = text.split('\n')
                for line_idx, line in enumerate(lines):
                    if '대신해' in line or '동행' in line or '성빈' in line or '준수' in line or '영주' in line:
                        print(f"Page {page_idx+1}, Line {line_idx+1}: {line.strip()}")
                        # Print some context around it
                        start = max(0, line_idx - 3)
                        end = min(len(lines), line_idx + 8)
                        print("--- Context ---")
                        for idx in range(start, end):
                            marker = ">>>" if idx == line_idx else "   "
                            print(f"{marker} {idx+1}: {lines[idx].strip()}")
                        print("-" * 30)
    except Exception as e:
        print(f"Error processing {fp}: {e}")

hwp.quit()
