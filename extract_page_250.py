import PyPDF2
import os

def extract_page_text(file_path, page_num):
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
            
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            print(f"Total Pages: {num_pages}")
            
            # Use 0-indexed page number
            if 0 <= page_num < num_pages:
                page = reader.pages[page_num]
                text = page.extract_text()
                # Write to file with utf-8 encoding
                with open("extracted_text_p250.txt", "w", encoding="utf-8") as out:
                    out.write(text)
                print(f"Extracted Page {page_num + 1} to extracted_text_p250.txt")
            else:
                print(f"Invalid page number: {page_num + 1}. Total pages: {num_pages}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Page 250 (1-indexed) is 249 (0-indexed)
    extract_page_text("2027 ?섎뒫?밴컯 臾명븰 ?먮낯.pdf", 249)
