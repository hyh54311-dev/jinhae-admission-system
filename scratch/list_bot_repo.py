# -*- coding: utf-8 -*-
import os

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\jinhae-bot"

def main():
    print(f"Recursively listing all files in {base_dir}...")
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"- {os.path.relpath(file_path, base_dir)}")

if __name__ == '__main__':
    main()
