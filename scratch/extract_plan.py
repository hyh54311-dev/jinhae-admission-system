import olefile
import zlib
import os

def get_hwp_text(filename):
    if not os.path.exists(filename):
        return f"File not found: {filename}"
    try:
        with olefile.OleFileIO(filename) as f:
            dirs = f.listdir()
            body_dirs = [d for d in dirs if d[0] == 'BodyText']
            text = ''
            for d in body_dirs:
                stream = f.openstream(d)
                data = stream.read()
                try:
                    unpacked_data = zlib.decompress(data, -15)
                    text += unpacked_data.decode('utf-16le', errors='ignore')
                except Exception:
                    pass
            return text
    except Exception as e:
        return f"Error reading HWP: {e}"

target_file = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\창체 동아리\2026. 창체동아리 연간계획서(대신해 AI).hwp"
text = get_hwp_text(target_file)

with open('scratch/plan_extracted.txt', 'w', encoding='utf-8') as out:
    out.write(text)

print("Extraction complete. Check scratch/plan_extracted.txt")
