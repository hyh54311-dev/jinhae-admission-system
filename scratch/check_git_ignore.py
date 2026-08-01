# -*- coding: utf-8 -*-
import os

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"

def main():
    paths_to_check = [
        os.path.join(base_dir, "jinhae-bot", ".gitignore"),
        os.path.join(base_dir, "jinhae-bot", "jinhae-bot-main", ".gitignore")
    ]
    
    for path in paths_to_check:
        print(f"Checking: {path}")
        if os.path.exists(path):
            print("  Exists! Content:")
            with open(path, 'r', encoding='utf-8') as f:
                print(f.read())
        else:
            print("  Does not exist.")

if __name__ == '__main__':
    main()
