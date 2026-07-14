import re
import os

html_files = [f for f in os.listdir(".") if f.endswith(".html")]

found = False
for file_name in html_files:
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Look for url("data:image/...) or url('data:image/...)
        pattern = r'url\((["\']?)(data:image/[^)\'"]+)\1\)'
        match = re.search(pattern, content)
        if match:
            img_data = match.group(2)
            print(f"Found background image in file: {file_name}!")
            with open("scratch/logo_data.txt", "w", encoding="utf-8") as out:
                out.write(img_data)
            print(f"Successfully written base64 string from {file_name} to scratch/logo_data.txt (length: {len(img_data)})")
            found = True
            break
            
        # Look for background-image with base64
        pattern2 = r'data:image/[^;\'"]+;base64,[^\'" )]+'
        match2 = re.search(pattern2, content)
        if match2:
            img_data = match2.group(0)
            print(f"Found base64 image in file: {file_name}!")
            with open("scratch/logo_data.txt", "w", encoding="utf-8") as out:
                out.write(img_data)
            print(f"Successfully written base64 string from {file_name} to scratch/logo_data.txt (length: {len(img_data)})")
            found = True
            break
    except Exception as e:
        print(f"Error reading {file_name}: {e}")

if not found:
    print("No base64 logo found in any HTML file in the root directory.")
