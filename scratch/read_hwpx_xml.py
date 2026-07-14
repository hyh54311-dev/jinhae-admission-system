import zipfile
import sys
import xml.etree.ElementTree as ET
import re

sys.stdout.reconfigure(encoding='utf-8')

hwpx_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\쿨메신져 다운로드 파일\2026. 특수학급배치 특수교육대상자 시간표_3학년.hwpx"

try:
    with zipfile.ZipFile(hwpx_path, 'r') as z:
        # Let's inspect the contents of Contents/section0.xml
        xml_content = z.read('Contents/section0.xml')
        print("XML size:", len(xml_content))
        
        # We can extract all text inside elements. In HWPX section0.xml, text is usually in <hp:t> elements
        # Let's find all text matches using regex first as it's quick
        matches = re.findall(r'<hp:t[^>]*>(.*?)</hp:t>', xml_content.decode('utf-8', errors='replace'))
        print(f"Found {len(matches)} text nodes")
        
        # Print them out
        full_text = " ".join(matches)
        print("Cleaned text from XML:")
        print(full_text[:4000]) # Print first 4000 chars of combined text
        
        # Find anything like 3-3, 3-4, 3-6, 3-7, etc. or student name patterns
        print("\nStudent name patterns in XML:")
        # Look for <3-X Name> or similar in the matches
        for m in matches:
            if '3-' in m or '도움' in m or '특수' in m:
                print("  Match:", m)
except Exception as e:
    print("Error:", e)
