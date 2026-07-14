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
    
    # Let's extract the page title if any
    title_el = soup.find("title")
    if title_el:
        result.append(f"Title: {title_el.get_text(strip=True)}")
        
    # Main title in slide content
    # Look for slide titles or headers like h1, h2, h3, or bold texts with certain classes
    headers = soup.find_all(["h1", "h2", "h3", "h4", "strong", "p"])
    
    # We can also search for interactive components like tables, input placeholders, etc.
    # In rootsall, tip-tap ProseMirror content holds the text.
    prose_elements = soup.find_all(class_="ProseMirror")
    
    result.append("\n--- Text Content (ProseMirror) ---")
    seen_texts = set()
    for el in prose_elements:
        text = el.get_text(strip=True)
        if text and text not in seen_texts:
            seen_texts.add(text)
            result.append(f"- {text}")
            
    # Look for table data or input configurations in data-ele attributes
    result.append("\n--- Interactive Elements / Data Inputs ---")
    data_elements = soup.find_all(attrs={"data-ele": True})
    for idx, el in enumerate(data_elements):
        data_str = el.get("data-ele")
        # Just extract key properties from the JSON-like string
        # e.g., type, tableTitle, colTitle, text
        try:
            import json
            data = json.loads(data_str)
            target = data.get("target", {})
            cat = data.get("category", "")
            t_type = target.get("type", "")
            content = target.get("content", {})
            
            result.append(f"[{idx+1}] Category: {cat} | Type: {t_type}")
            
            if t_type == "table":
                table_data = target.get("tableData", {})
                col_titles = []
                for col in table_data.get("colTitle", []):
                    # strip html tags from col title
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
                
        except Exception as e:
            result.append(f"    Error parsing data-ele JSON: {e}")
            
    return "\n".join(result)

def main():
    scratch_dir = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch"
    out_path = os.path.join(scratch_dir, "parsed_curriculum_structure.txt")
    
    with open(out_path, "w", encoding="utf-8") as out:
        out.write("=== CURRICULUM WORKBOOK STRUCTURE ANALYSIS ===\n\n")
        
        for idx in range(6):
            file_name = f"workbook_page_{idx+1}.html"
            file_path = os.path.join(scratch_dir, file_name)
            out.write(f"\n=========================================\n")
            out.write(f"PAGE {idx+1}: {file_name}\n")
            out.write(f"=========================================\n")
            
            page_content = parse_html(file_path)
            out.write(page_content)
            out.write("\n\n")
            
    print("Workbook parsed. Summary saved to:", out_path)

if __name__ == "__main__":
    main()
