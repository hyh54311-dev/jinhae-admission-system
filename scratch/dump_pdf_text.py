import pdfplumber
import glob
import os

folder = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 나눔의 날\국어과"
output_file = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\pdf_raw_dump.txt"

with open(output_file, "w", encoding="utf-8") as f_out:
    for pdf_path in glob.glob(os.path.join(folder, "*.pdf")):
        f_out.write(f"\n\n{'='*20}\nFILE: {os.path.basename(pdf_path)}\n{'='*20}\n")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract first page text with layout
                text = pdf.pages[0].extract_text(layout=True)
                if text:
                    f_out.write(text)
                else:
                    f_out.write("No text extracted.")
        except Exception as e:
            f_out.write(f"Error: {e}")
