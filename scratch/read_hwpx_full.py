import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8')

hwpx_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\쿨메신져 다운로드 파일\2026. 특수학급배치 특수교육대상자 시간표_3학년.hwpx"

try:
    with zipfile.ZipFile(hwpx_path, 'r') as z:
        with z.open('Preview/PrvText.txt') as f:
            content_bytes = f.read()
            
            # Let's try to decode using different encodings with errors='replace'
            for encoding in ['utf-8', 'utf-16', 'utf-16-le', 'cp949']:
                try:
                    text = content_bytes.decode(encoding, errors='replace')
                    print(f"=== Decoded with {encoding} ===")
                    print(text)
                    print("================================")
                    break
                except Exception as e:
                    print(f"Failed decoding with {encoding}: {e}")
                    
except Exception as e:
    print("Error opening HWPX:", e)
