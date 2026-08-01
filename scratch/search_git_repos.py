# -*- coding: utf-8 -*-
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"

def search_git():
    print(f"Searching for .git folders recursively in: {base_dir}")
    git_folders = []
    
    # We walk the directories
    for root, dirs, files in os.walk(base_dir):
        # We can inspect dirs to see if '.git' is in it
        if '.git' in dirs:
            git_path = os.path.join(root, '.git')
            git_folders.append(git_path)
            print(f"Found .git: {git_path}")
            
    print(f"Total .git folders found: {len(git_folders)}")

if __name__ == '__main__':
    search_git()
