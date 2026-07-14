import os
import fitz  # PyMuPDF

import glob

def convert_pdfs_to_png():
    import subprocess
    cmd = 'dir /b /s "D:\\OneDrive - 경상남도교육청\\바탕 화면\\*안.pdf"'
    print(f"Running command: {cmd}")
    
    try:
        output = subprocess.check_output(cmd, shell=True).decode('cp949')
        pdf_files = [line.strip() for line in output.splitlines() if line.strip() and line.endswith('.pdf')]
    except Exception as e:
        print(f"Error executing dir command: {e}")
        return
        
    print(f"Found matching PDF files: {pdf_files}")
    output_dir = "scratch"
    os.makedirs(output_dir, exist_ok=True)
    
    for pdf_path in pdf_files:
        name = os.path.basename(pdf_path)
        try:
            print(f"Converting {name} to PNG...")
            doc = fitz.open(pdf_path)
            # Render first page at high resolution (300 DPI / scale 3x)
            page = doc[0]
            zoom = 3.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            output_name = name.replace(".pdf", ".png")
            output_path = os.path.join(output_dir, output_name)
            pix.save(output_path)
            print(f"  => Saved to {output_path}")
            doc.close()
        except Exception as e:
            print(f"  => Error converting {name}: {e}")
            
    print("All conversions complete.")

if __name__ == '__main__':
    convert_pdfs_to_png()
