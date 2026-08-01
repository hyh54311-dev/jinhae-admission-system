# -*- coding: utf-8 -*-
import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
json_path = r"C:\Users\admin\.gemini\antigravity\brain\6f17156b-cb5e-4877-bdba-1ea12d375810\.system_generated\steps\1092\content.md"

def main():
    if not os.path.exists(json_path):
        print("content.md not found!")
        return
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find any vercel strings
    print("Searching for vercel occurrences...")
    pos = 0
    while True:
        pos = content.find("vercel", pos)
        if pos == -1:
            break
        print(content[pos-100:pos+200])
        pos += 6
        print("="*50)

if __name__ == '__main__':
    main()
