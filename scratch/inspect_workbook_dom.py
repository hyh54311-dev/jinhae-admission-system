import os
from bs4 import BeautifulSoup

def main():
    html_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\workbook_page_1.html"
    out_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\workbook_dom_inspection.txt"
    
    if not os.path.exists(html_path):
        print("HTML file not found:", html_path)
        return
        
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")
    
    with open(out_path, "w", encoding="utf-8") as out:
        out.write("=== INSPECTING WORKBOOK DOM ===\n\n")
        
        # Look for typical menu tags (li, a, button, div, span)
        for tag_name in ["a", "button", "div", "span", "li", "p"]:
            elements = soup.find_all(tag_name)
            for idx, el in enumerate(elements):
                text = el.get_text(strip=True)
                # Filter elements that have text matching tab keywords
                if any(k in text for k in ["차시", "학습", "정리", "데이터", "배신", "선"]):
                    classes = el.get("class", [])
                    id_attr = el.get("id", "")
                    onclick = el.get("onclick", "")
                    attrs = {k: v for k, v in el.attrs.items() if k not in ["class", "id", "onclick"]}
                    out.write(f"Tag: {tag_name} | Class: {classes} | ID: {id_attr} | OnClick: {onclick} | Attrs: {attrs}\n")
                    out.write(f"Text (len={len(text)}): {text[:150]}\n")
                    out.write("-" * 80 + "\n")
                    
    print("DOM inspection completed. Results saved to:", out_path)

if __name__ == "__main__":
    main()
