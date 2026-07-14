# -*- coding: utf-8 -*-
import os
import json

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"

def main():
    for name in ['token.json', 'token_calendar.json', 'token_gmail.json', 'token_tasks.json']:
        path = os.path.join(base_dir, name)
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
            print(f"{name} scopes: {data.get('scopes')}")
        else:
            print(f"{name} not found")

if __name__ == '__main__':
    main()
