# -*- coding: utf-8 -*-
import os
import shutil

src_path = r"C:\Users\admin\.gemini\antigravity\brain\6f17156b-cb5e-4877-bdba-1ea12d375810\jinhae_poster_classic_final_1783995965369.png"
dest_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교_입학챗봇_홍보포스터_A4.png"

def main():
    print(f"Copying final poster image from {src_path} to Desktop...")
    try:
        shutil.copy(src_path, dest_path)
        print(f"SUCCESS: Poster image successfully copied to Desktop: {dest_path}")
    except Exception as e:
        print(f"FAILED to copy image: {e}")

if __name__ == '__main__':
    main()
