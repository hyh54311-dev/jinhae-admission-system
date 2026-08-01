# -*- coding: utf-8 -*-
import os

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"

def main():
    paths = [
        base_dir,
        os.path.join(base_dir, "jinhae-bot"),
        os.path.join(base_dir, "jinhae-bot", "jinhae-bot-main")
    ]
    
    for path in paths:
        git_dir = os.path.join(path, ".git")
        print(f"Checking for .git in: {path}")
        if os.path.exists(git_dir):
            print("  FOUND .git!")
        else:
            print("  No .git folder here.")

if __name__ == '__main__':
    main()
