import olefile
import zlib
import re

def get_hwp_text(filename):
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
            except Exception as e:
                pass
        return text

t = get_hwp_text(r'd:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\개인적인 일\2026년 교육대학원연계 AI융합교육 전문과정 교육대상자 선발 추진 계획\2026년 교육대학원연계 AI융합교육 전문과정 교육대상자 선발 추진 계획.hwp')

with open('extracted_text.txt', 'w', encoding='utf-8') as out:
    out.write(t)
