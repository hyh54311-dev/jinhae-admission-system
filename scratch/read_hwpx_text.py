import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8')

hwpx_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\쿨메신져 다운로드 파일\2026. 특수학급배치 특수교육대상자 시간표_3학년.hwpx"

try:
    with zipfile.ZipFile(hwpx_path, 'r') as z:
        with z.open('Preview/PrvText.txt') as f:
            text = f.read().decode('utf-16le') # HWPX preview text is usually UTF-16LE or UTF-8. Let's try utf-16 first, or try to decode with fallbacks.
            print("Preview Text Content:")
            print(text)
except Exception as e:
    print("Error reading PrvText.txt:", e)
    # Let's try other encodings if it failed
    try:
        with zipfile.ZipFile(hwpx_path, 'r') as z:
            with z.open('Preview/PrvText.txt') as f:
                text = f.read().decode('utf-8')
                print("Preview Text Content (UTF-8):")
                print(text[:1000])
    except Exception as e2:
        print("Error reading with UTF-8:", e2)
