import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8')

hwpx_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\쿨메신져 다운로드 파일\2026. 특수학급배치 특수교육대상자 시간표_3학년.hwpx"

try:
    with zipfile.ZipFile(hwpx_path, 'r') as z:
        print("Files inside HWPX:")
        for name in z.namelist():
            print(f"  {name}")
except Exception as e:
    print("Error opening HWPX:", e)
