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
    print(f"HTML Length: {len(html)}")
    
    iframes = soup.find_all("iframe")
    print(f"Found {len(iframes)} iframes:")
    for idx, iframe in enumerate(iframes):
        print(f"  [{idx}] Name: {iframe.get('name')} | Src: {iframe.get('src')} | ID: {iframe.get('id')}")

if __name__ == '__main__':
    main()
