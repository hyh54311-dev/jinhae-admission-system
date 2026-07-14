# -*- coding: utf-8 -*-
import os

src1 = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더 (2)"
img_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic"}

def main():
    non_images = []
    if os.path.exists(src1):
        for root, dirs, files in os.walk(src1):
            for file in files:
                _, ext = os.path.splitext(file.lower())
                if ext not in img_extensions:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, src1)
                    non_images.append(rel_path)
                    
    with open("scratch/src1_non_images.txt", "w", encoding="utf-8") as f:
        for item in sorted(non_images):
            f.write(item + "\n")
            
    print(f"Total non-images in src1: {len(non_images)}")

if __name__ == "__main__":
    main()
