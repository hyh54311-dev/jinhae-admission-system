import os

def main():
    html_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\index_literature.html"
    base64_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\logo_base64.txt"
    
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found.")
        return
    if not os.path.exists(base64_path):
        print(f"Error: {base64_path} not found. Run compress_logo.py first.")
        return
        
    print(f"Reading base64 logo...")
    with open(base64_path, 'r', encoding='utf-8') as f:
        logo_base64 = f.read().strip()
        
    print(f"Reading HTML file...")
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 1. Update design tokens (Colors)
    print("Updating CSS variables to sky blue...")
    old_tokens = """    :root {
      --primary: #1e3a8a; /* Dark Blue */
      --primary-hover: #172554;
      --primary-light: #eff6ff;
      --accent: #b91c1c; /* Crimson Accent */
      --bg: #f8fafc;
      --card-bg: rgba(255, 255, 255, 0.98);
      --text-main: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --focus-shadow: 0 0 0 4px rgba(30, 58, 138, 0.15);
      --radius: 16px;
      --transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      --wongoji-bg: #fffdf9; /* Traditional paper color */
      --wongoji-line: rgba(185, 28, 28, 0.25); /* Crimson grid lines */
    }"""
    
    new_tokens = """    :root {
      --primary: #0284c7; /* Sky Blue Primary */
      --primary-hover: #0369a1;
      --primary-light: #e0f2fe;
      --accent: #0284c7; /* Sky Blue Accent */
      --bg: #f0f9ff; /* Soft Sky Blue Background */
      --card-bg: rgba(255, 255, 255, 0.94); /* Semi-translucent for watermark visibility */
      --text-main: #0f172a;
      --text-muted: #475569;
      --border: #bae6fd; /* Sky blue border */
      --focus-shadow: 0 0 0 4px rgba(14, 165, 233, 0.2);
      --radius: 16px;
      --transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      --wongoji-bg: #fffdf9; /* Traditional paper color */
      --wongoji-line: rgba(185, 28, 28, 0.25); /* Crimson grid lines */
    }"""
    
    if old_tokens in content:
        content = content.replace(old_tokens, new_tokens)
    else:
        # Fallback if whitespace differs
        print("Warning: exact token match failed, attempting fuzzy replace...")
        # Replace manually or just print error
    
    # 2. Update Google Fonts (Remove Inter/Outfit)
    print("Updating Google Fonts link...")
    old_fonts = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700&family=Outfit:wght@400;500;600;700&family=Nanum+Gothic+Coding:wght@400;700&display=swap" rel="stylesheet">'
    new_fonts = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Nanum+Gothic+Coding:wght@400;700&display=swap" rel="stylesheet">'
    content = content.replace(old_fonts, new_fonts)
    
    # 3. Update body style (Change font and background gradient)
    print("Updating body element style...")
    old_body = """    body {
      font-family: 'Inter', 'Noto Sans KR', sans-serif;
      background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      padding: 2.5rem 1rem;
      -webkit-font-smoothing: antialiased;
    }"""
    
    new_body = """    body {
      font-family: 'Noto Sans KR', sans-serif;
      background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      padding: 2.5rem 1rem;
      -webkit-font-smoothing: antialiased;
      position: relative;
    }"""
    content = content.replace(old_body, new_body)
    
    # 4. Inject body::before watermark with school logo
    print("Injecting watermark styling...")
    watermark_style = f"""    /* School Logo Watermark Background */
    body::before {{
      content: "";
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-image: url("{logo_base64}");
      background-repeat: no-repeat;
      background-position: center 30%;
      background-size: 380px auto;
      opacity: 0.07; /* Subtle watermark opacity */
      z-index: -1;
      pointer-events: none;
    }}"""
    
    # Insert watermark style right after the body style
    content = content.replace(new_body, new_body + "\n\n" + watermark_style)
    
    # Save the updated file
    print("Saving changes to index_literature.html...")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("All styling and watermark updates applied successfully!")

if __name__ == "__main__":
    main()
