# scratch/logo_data.txt의 내용(진해고 교표 base64)을 문학_탐구보고서_웹앱_Index.html에 주입하는 스크립트

try:
    with open("scratch/logo_data.txt", "r", encoding="utf-8") as f:
        logo_base64 = f.read().strip()
    
    with open("문학_탐구보고서_웹앱_Index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    target_url = "https://upload.wikimedia.org/wikipedia/commons/e/e0/Placeholder_empty_square.png"
    
    if target_url in html_content:
        new_html_content = html_content.replace(target_url, logo_base64)
        with open("문학_탐구보고서_웹앱_Index.html", "w", encoding="utf-8") as f:
            f.write(new_html_content)
        print("Successfully injected Jinhae High School logo base64 into 문학_탐구보고서_웹앱_Index.html!")
    else:
        print("Target URL not found in HTML file. Please check the file content.")
except Exception as e:
    print("Error:", e)
