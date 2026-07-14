import os
from bs4 import BeautifulSoup

def main():
    html_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\lms_dashboard.html"
    if not os.path.exists(html_path):
        print("HTML file not found")
        return
        
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")
    
    print("=== All Links (<a>) ===")
    for idx, a in enumerate(soup.find_all("a")):
        text = a.get_text().strip().replace('\n', ' ')
        href = a.get("href")
        print(f"[{idx}] Text: {text} | Href: {href}")
        
    print("\n=== All Buttons ===")
    for idx, b in enumerate(soup.find_all("button")):
        text = b.get_text().strip().replace('\n', ' ')
        print(f"[{idx}] Button: {text}")

if __name__ == '__main__':
    main()
