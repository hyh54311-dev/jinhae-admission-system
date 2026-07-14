import zipfile
import sys
import xml.etree.ElementTree as ET
import re

sys.stdout.reconfigure(encoding='utf-8')

hwpx_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\쿨메신져 다운로드 파일\2026. 특수학급배치 특수교육대상자 시간표_3학년.hwpx"

try:
    with zipfile.ZipFile(hwpx_path, 'r') as z:
        xml_content = z.read('Contents/section0.xml').decode('utf-8', errors='replace')
        
        # Search for any Korean name-like strings (2-4 characters) and check their context
        # Or search for specific names we know:
        names_to_check = ['김승진', '문상현', '권해찬', '박동은', '김건우', '팽정욱', '조현준']
        print("Checking names in section0.xml:")
        for name in names_to_check:
            if name in xml_content:
                print(f"  Name '{name}' is in the XML!")
                # Print a snippet around the name
                idx = xml_content.find(name)
                start = max(0, idx - 100)
                end = min(len(xml_content), idx + 150)
                snippet = xml_content[start:end]
                # Clean XML tags for readability
                snippet_clean = re.sub(r'<[^>]+>', ' ', snippet)
                print(f"    Snippet: {snippet_clean}")
            else:
                print(f"  Name '{name}' is NOT in the XML.")
except Exception as e:
    print("Error:", e)
