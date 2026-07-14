import olefile
import zlib
import struct

def get_hwp_text(filename):
    f = olefile.OleFileIO(filename)
    dirs = f.listdir()
    
    # Try to get PrvText first (it's uncompressed and easy)
    if ['PrvText'] in dirs:
        text = f.openstream('PrvText').read().decode('utf-16le')
        return text
    
    # If not, we have to deal with BodyText (compressed)
    # This is much harder as it involves HWP5 structure
    return "PrvText not found"

import os
folder = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 나눔의 날\국어과"
for filename in os.listdir(folder):
    if filename.endswith(".hwp"):
        print(f"File: {filename}")
        try:
            print(get_hwp_text(os.path.join(folder, filename))[:500])
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 20)
