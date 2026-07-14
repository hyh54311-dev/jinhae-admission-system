# -*- coding: utf-8 -*-
import os
import re

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
knowledge_path = os.path.join(base_dir, 'jinhae-bot', 'jinhae-bot-main', 'api', 'knowledge.txt')

def main():
    print("Searching knowledge.txt for URLs, '.pdf', '홍보책자', and '브로슈어'...")
    if not os.path.exists(knowledge_path):
        print("knowledge.txt not found!")
        return

    with open(knowledge_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Search for URLs
    urls = re.findall(r'https?://[^\s()<>]+(?:\([\w\d]+\)|[^\s`!()\[\]{{}};:\'".,<>?«»“”‘’])', content)
    print(f"Found URLs in knowledge.txt:")
    for url in urls:
        print(f"- {url}")

    # Search for lines containing pdf, 책자, 브로슈어, 리플렛
    print("\nMatching lines:")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in ['pdf', 'PDF', '책자', '브로슈어', '리플렛', '드라이브', '링크']):
            print(f"Line {i+1}: {line}")

if __name__ == '__main__':
    main()
