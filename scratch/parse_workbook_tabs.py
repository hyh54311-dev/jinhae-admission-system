import os
from bs4 import BeautifulSoup

def main():
    html_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\lms_workbook.html"
    if not os.path.exists(html_path):
        print("HTML file not found")
        return
        
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")
    
    # Let's find the left side navigation or buttons/tabs
    print("=== Left Navigation Elements ===")
    # Look for elements that might represent the tabs (e.g., div, button, li containing "1차시", "데이터로")
    for idx, div in enumerate(soup.find_all(lambda tag: tag.name in ["div", "button", "span", "li"] and tag.get_text() and ("1차시" in tag.get_text() or "2차시" in tag.get_text()))):
        text = div.get_text().strip().replace('\n', ' ')
        classes = div.get("class")
        id_attr = div.get("id")
        print(f"[{idx}] Tag: {div.name} | Text: {text} | Class: {classes} | ID: {id_attr}")

if __name__ == '__main__':
    main()
