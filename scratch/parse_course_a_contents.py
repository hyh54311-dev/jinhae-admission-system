import os
import re
from bs4 import BeautifulSoup

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_html(file_path):
    if not os.path.exists(file_path):
        return f"File {file_path} not found."
        
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    result = []
    
    # Page title
    title_el = soup.find("title")
    if title_el:
        result.append(f"Title: {title_el.get_text(strip=True)}")
        
    # ProseMirror content
    prose_elements = soup.find_all(class_="ProseMirror")
    result.append("\n--- Text Content (ProseMirror) ---")
    seen_texts = set()
    for el in prose_elements:
        text = el.get_text(strip=True)
        if text and text not in seen_texts:
            seen_texts.add(text)
            result.append(f"- {text}")
            
    # Interactive elements
    result.append("\n--- Interactive Elements / Data Inputs ---")
    data_elements = soup.find_all(attrs={"data-ele": True})
    for idx, el in enumerate(data_elements):
        data_str = el.get("data-ele")
        try:
            import json
            data = json.loads(data_str)
            target = data.get("target", {})
            cat = data.get("category", "")
            t_type = target.get("type", "")
            
            result.append(f"[{idx+1}] Category: {cat} | Type: {t_type}")
            
            if t_type == "table":
                table_data = target.get("tableData", {})
                col_titles = []
                for col in table_data.get("colTitle", []):
                    col_text = BeautifulSoup(col.get("content", ""), "html.parser").get_text(strip=True)
                    col_titles.append(col_text)
                result.append(f"    Table Columns: {col_titles}")
                
                rows_data = []
                for row in table_data.get("data", []):
                    row_cells = []
                    for cell in row:
                        cell_text = BeautifulSoup(cell.get("content", ""), "html.parser").get_text(strip=True)
                        row_cells.append(cell_text)
                    rows_data.append(row_cells)
                result.append(f"    Table Rows (Initial Data): {rows_data}")
                
            elif t_type == "text":
                text_content = BeautifulSoup(target.get("text", ""), "html.parser").get_text(strip=True)
                result.append(f"    Text Content: {text_content}")
                
            elif t_type == "image":
                result.append(f"    Image upload component")
                
            elif t_type == "question":
                result.append(f"    Question component")
                
        except Exception as e:
            result.append(f"    Error parsing data-ele JSON: {e}")
            
    return "\n".join(result)

def main():
    scratch_dir = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch"
    out_path = os.path.join(scratch_dir, "parsed_course_a_structure.txt")
    
    with open(out_path, "w", encoding="utf-8") as out:
        out.write("=== COURSE A WORKBOOK STRUCTURE ANALYSIS ===\n\n")
        
        for idx in range(6):
            file_name = f"course_a_page_{idx+1}.html"
            file_path = os.path.join(scratch_dir, file_name)
            out.write(f"\n=========================================\n")
            out.write(f"PAGE {idx+1}: {file_name}\n")
            out.write(f"=========================================\n")
            
            page_content = parse_html(file_path)
            out.write(page_content)
            out.write("\n\n")
            
    print("Course A parsed. Summary saved to:", out_path)

if __name__ == "__main__":
    main()
