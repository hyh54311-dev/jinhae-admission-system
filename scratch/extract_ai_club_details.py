import PyPDF2
import sys
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def main():
    file_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\창체 동아리\2026. 창체동아리 연간계획서(대신해 AI).pdf"
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            print(f"=== Extracting from PDF: {file_path} ===")
            print(f"Total Pages: {len(reader.pages)}")
            for idx, page in enumerate(reader.pages):
                print(f"\n--- Page {idx+1} ---")
                text = page.extract_text()
                print(text)
    except Exception as e:
        print("Error reading PDF:", e)

if __name__ == '__main__':
    main()
