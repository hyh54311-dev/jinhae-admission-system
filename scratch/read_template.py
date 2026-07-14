import pdfplumber

pdf_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록\2026. 1학기 2차 교과 협의록 양식(국어).pdf"
out_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\template_dump.txt"

with open(out_path, "w", encoding="utf-8") as f:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text(layout=True)
                if text:
                    f.write(text + "\n")
    except Exception as e:
        f.write(f"Error: {e}")
