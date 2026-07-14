import PyPDF2
import sys

def check_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            print(f"Total Pages: {num_pages}")
            if num_pages > 1:
                page = reader.pages[1]
                text = page.extract_text()
                print("--- Extract from Second Page ---")
                print(text[:500])
                print("-------------------------------")
            elif num_pages > 0:
                page = reader.pages[0]
                text = page.extract_text()
                print("--- Extract from First Page ---")
                print(text[:500])
                print("-------------------------------")
            else:
                print("PDF has no pages.")
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    # In Windows terminal, the file path might be tricky to pass as an argument due to encoding,
    # so we use a hardcoded or globbed name.
    import glob
    files = glob.glob("*2027*pdf*")
    if files:
        check_pdf(files[0])
    else:
        print("File not found.")
