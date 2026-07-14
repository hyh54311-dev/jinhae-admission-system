# -*- coding: utf-8 -*-
import os

pdf_path = r"C:\Users\admin\.gemini\antigravity\brain\6f17156b-cb5e-4877-bdba-1ea12d375810\media__1783927432357.pdf"

def main():
    print(f"Inspecting PDF file size and existence: {pdf_path}")
    if not os.path.exists(pdf_path):
        print("PDF file not found in artifacts!")
        return

    print(f"File size: {os.path.getsize(pdf_path)} bytes")
    
    # Try using pypdf to extract text
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        print(f"Number of pages: {len(reader.pages)}")
        
        # Extract text from the first 2 pages
        for i in range(min(5, len(reader.pages))):
            print(f"\n--- Page {i+1} ---")
            text = reader.pages[i].extract_text()
            print(text[:1000]) # print first 1000 characters of each page
    except Exception as e:
        print(f"Failed with pypdf: {e}")

if __name__ == '__main__':
    main()
