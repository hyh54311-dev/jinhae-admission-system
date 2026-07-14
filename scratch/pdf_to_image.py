import os
import pypdfium2 as pdfium

def pdf_to_png(pdf_path, output_png_path):
    print(f"Rendering {pdf_path} to {output_png_path}...")
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return False
    try:
        doc = pdfium.PdfDocument(pdf_path)
        page = doc[0] # First page
        bitmap = page.render(scale=2.0) # High quality render
        pil_img = bitmap.to_pil()
        pil_img.save(output_png_path)
        print("Success.")
        return True
    except Exception as e:
        print(f"Error rendering PDF: {e}")
        return False

if __name__ == "__main__":
    dir_2nd = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 고사\2학년 1학기고사\중간고사"
    
    score_pdf = os.path.join(dir_2nd, "문항 배점.pdf")
    score_png = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\lit_score.png"
    pdf_to_png(score_pdf, score_png)
    
    role_pdf = os.path.join(dir_2nd, "역할 배정.pdf")
    role_png = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\lit_role.png"
    pdf_to_png(role_pdf, role_png)
