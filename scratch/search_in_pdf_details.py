# -*- coding: utf-8 -*-
import os
import pypdf

pdf_path = r"C:\Users\admin\.gemini\antigravity\brain\6f17156b-cb5e-4877-bdba-1ea12d375810\media__1783927432357.pdf"
output_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\pdf_search_results.txt"

def main():
    print(f"Searching PDF content for year references to see if it's outdated...")
    if not os.path.exists(pdf_path):
        print("PDF file not found in artifacts!")
        return

    reader = pypdf.PdfReader(pdf_path)
    results = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        for line in text.split('\n'):
            if any(year in line for year in ['2026', '2025', '2024', '2023']):
                results.append(f"Page {i+1}: {line.strip()}")

    with open(output_path, 'w', encoding='utf-8') as f:
        for res in results:
            f.write(res + "\n")
            
    print(f"SUCCESS: Search results written to {output_path}")

if __name__ == '__main__':
    main()
