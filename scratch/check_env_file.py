# -*- coding: utf-8 -*-
import os

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
env_path = os.path.join(base_dir, "jinhae-bot", "jinhae-bot-main", "api", ".env")

def main():
    print(f"Checking existence of: {env_path}")
    if os.path.exists(env_path):
        print("File exists. Variable names defined inside:")
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_clean = line.strip()
                if line_clean and not line_clean.startswith('#'):
                    if '=' in line_clean:
                        var_name = line_clean.split('=')[0]
                        print(f"- {var_name}")
    else:
        print("File does not exist.")

if __name__ == '__main__':
    main()
