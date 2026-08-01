# -*- coding: utf-8 -*-
import os
import sys
import argparse

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"

# Targets grouped by key type
school_targets = [
    "performance_seteuk_system/config.js",
    "scratch/gemini_ocr.py",
    "scratch/test_flash_lite.py"
]

personal_targets = [
    "scratch/gas_daily_news_gas.json",
    "scratch/gas_weekend_news_gas.json"
]

leaked_key = "MASKED_API_KEY"
placeholder = "YOUR_GEMINI_API_KEY_HERE"

def get_keys():
    # Robustly find .env file up to parent directories
    curr_dir = os.path.abspath(os.path.dirname(__file__))
    school_key = None
    personal_key = None
    
    for _ in range(3):
        env_path = os.path.join(curr_dir, ".env")
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY="):
                        school_key = line.split("=", 1)[1]
                        if (school_key.startswith('"') and school_key.endswith('"')) or (school_key.startswith("'") and school_key.endswith("'")):
                            school_key = school_key[1:-1]
                    elif line.startswith("PERSONAL_GEMINI_API_KEY="):
                        personal_key = line.split("=", 1)[1]
                        if (personal_key.startswith('"') and personal_key.endswith('"')) or (personal_key.startswith("'") and personal_key.endswith("'")):
                            personal_key = personal_key[1:-1]
            return school_key, personal_key
        curr_dir = os.path.dirname(curr_dir)
                    
    return None, None

def main():
    parser = argparse.ArgumentParser(description="Inject or Clean Gemini API keys in workspace files.")
    parser.add_argument("--mode", choices=["inject", "clean"], default="inject",
                        help="Mode: 'inject' to apply keys, 'clean' to restore placeholders.")
    args = parser.parse_args()

    school_key, personal_key = get_keys()
    
    if args.mode == "inject":
        # Validate keys
        if not school_key or school_key == placeholder or school_key == leaked_key or school_key.strip() == "":
            print("Error: Valid GEMINI_API_KEY (School) not found in .env.")
            sys.exit(1)
        if not personal_key or personal_key == placeholder or personal_key == leaked_key or personal_key.strip() == "":
            print("Error: Valid PERSONAL_GEMINI_API_KEY (Personal) not found in .env.")
            sys.exit(1)
            
        print("Injecting keys into target files...")
        
        # Inject School Key
        for rel_path in school_targets:
            abs_path = os.path.join(base_dir, rel_path)
            if os.path.exists(abs_path):
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                content = content.replace(leaked_key, school_key)
                content = content.replace(placeholder, school_key)
                
                if content != original_content:
                    with open(abs_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  Successfully injected School Key into: {rel_path}")
                else:
                    print(f"  No change needed for: {rel_path}")
            else:
                print(f"  File not found: {rel_path}")
                
        # Inject Personal Key
        for rel_path in personal_targets:
            abs_path = os.path.join(base_dir, rel_path)
            if os.path.exists(abs_path):
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                content = content.replace(leaked_key, personal_key)
                content = content.replace(placeholder, personal_key)
                
                if content != original_content:
                    with open(abs_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  Successfully injected Personal Key into: {rel_path}")
                else:
                    print(f"  No change needed for: {rel_path}")
            else:
                print(f"  File not found: {rel_path}")

    elif args.mode == "clean":
        print("Cleaning API keys in target files (restoring placeholders)...")
        
        # Clean School targets
        for rel_path in school_targets:
            abs_path = os.path.join(base_dir, rel_path)
            if os.path.exists(abs_path):
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                if school_key and school_key != placeholder:
                    content = content.replace(school_key, placeholder)
                content = content.replace(leaked_key, placeholder)
                
                if content != original_content:
                    with open(abs_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  Successfully cleaned: {rel_path}")
                else:
                    print(f"  Already clean: {rel_path}")
            else:
                print(f"  File not found: {rel_path}")
                
        # Clean Personal targets
        for rel_path in personal_targets:
            abs_path = os.path.join(base_dir, rel_path)
            if os.path.exists(abs_path):
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                if personal_key and personal_key != placeholder:
                    content = content.replace(personal_key, placeholder)
                content = content.replace(leaked_key, placeholder)
                
                if content != original_content:
                    with open(abs_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  Successfully cleaned: {rel_path}")
                else:
                    print(f"  Already clean: {rel_path}")
            else:
                print(f"  File not found: {rel_path}")

if __name__ == '__main__':
    main()
