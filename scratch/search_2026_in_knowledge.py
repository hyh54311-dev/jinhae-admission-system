# -*- coding: utf-8 -*-
import os

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
knowledge_path = os.path.join(base_dir, 'jinhae-bot', 'jinhae-bot-main', 'api', 'knowledge.txt')

def main():
    print("Searching knowledge.txt for '2026' and '2025' references...")
    if not os.path.exists(knowledge_path):
        print("knowledge.txt not found!")
        return

    with open(knowledge_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    found = False
    for i, line in enumerate(lines):
        if '2026' in line or '2025' in line:
            print(f"Line {i+1}: {line.strip()}")
            found = True
            
    if not found:
        print("No references to '2026' or '2025' found.")

if __name__ == '__main__':
    main()
