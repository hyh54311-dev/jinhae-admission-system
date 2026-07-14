import os
import sys
import PyPDF2

def extract_pdf_texts():
    desktop_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면"
    pdf_files = ["1안.pdf", "2안.pdf", "3안.pdf", "4안.pdf"]
    
    output_path = "scratch/pdf_contents.txt"
    out_lines = []
    
    for pdf_name in pdf_files:
        full_path = os.path.join(desktop_dir, pdf_name)
        out_lines.append(f"============================================================")
        out_lines.append(f" FILE: {pdf_name}")
        out_lines.append(f"============================================================")
        
        if not os.path.exists(full_path):
            out_lines.append(f"Error: File not found at {full_path}")
            continue
            
        try:
            with open(full_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page_idx, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    text += f"--- Page {page_idx + 1} ---\n{page_text}\n"
                out_lines.append(text)
        except Exception as e:
            out_lines.append(f"Error reading PDF: {e}")
            
        out_lines.append("\n\n")
        
    with open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.write('\n'.join(out_lines))
        
    print(f"Extraction complete. Saved to {output_path}")

if __name__ == '__main__':
    extract_pdf_texts()
