# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import argparse

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

leaked_key = "MASKED_API_KEY"
placeholder = "YOUR_GEMINI_API_KEY_HERE"

def get_keys():
    school_key = None
    personal_key = None
    curr_dir = os.path.abspath(os.path.dirname(__file__))
    for _ in range(3):
        env_path = os.path.join(curr_dir, ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r', encoding='utf-8-sig') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            school_key = line.split("=", 1)[1].strip("'\"")
                        elif line.startswith("PERSONAL_GEMINI_API_KEY="):
                            personal_key = line.split("=", 1)[1].strip("'\"")
                return school_key, personal_key
            except Exception:
                pass
        curr_dir = os.path.dirname(curr_dir)
    return None, None

def search_keys(pre_commit=False):
    school_key, personal_key = get_keys()
    active_keys = []
    if school_key and school_key != placeholder:
        active_keys.append(school_key)
    if personal_key and personal_key != placeholder:
        active_keys.append(personal_key)
    active_keys.append(leaked_key)

    print("Searching workspace for hardcoded Gemini API keys...")
    found_count = 0
    targets_extensions = ('.html', '.js', '.py', '.txt', '.md', '.json', '.gs')
    exclude_files = {'.env', 'replace_leak_keys.py', 'search_hardcoded_keys.py', 'test_gemini.py'}

    # If pre-commit, only check staged files (ultra fast: 0.01s)
    files_to_check = []
    if pre_commit:
        try:
            res = subprocess.run(['git', 'diff', '--cached', '--name-only'], cwd=base_dir, capture_output=True, text=True, check=True)
            for line in res.stdout.splitlines():
                fpath = os.path.join(base_dir, line.strip())
                if os.path.isfile(fpath) and fpath.endswith(targets_extensions) and os.path.basename(fpath) not in exclude_files:
                    files_to_check.append(fpath)
        except Exception:
            files_to_check = []
    
    if not files_to_check and not pre_commit:
        ignore_dirs = {'node_modules', '.git', '.google_messages_session', 'Cookies', 'temp_jinhae_bot', 'temp_unzip', '.venv', 'venv', 'build', 'dist', '__pycache__', '.pytest_cache'}
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
            for file in files:
                if file in exclude_files:
                    continue
                if file.endswith(targets_extensions):
                    files_to_check.append(os.path.join(root, file))

    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    for key in active_keys:
                        if key in line:
                            rel_path = os.path.relpath(file_path, base_dir)
                            print(f"[LEAK DETECTED] in {rel_path} (Line {i+1})")
                            found_count += 1
                            break
        except Exception:
            pass

    if found_count > 0:
        print(f"\n[ERROR] Found {found_count} occurrences of active/leaked API keys!")
        print("Please run: python scratch/replace_leak_keys.py --mode clean")
        if pre_commit:
            sys.exit(1)
    else:
        print("No hardcoded active/leaked API keys found. Clean!")
        if pre_commit:
            sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--pre-commit", action="store_true")
    args = parser.parse_args()
    search_keys(pre_commit=args.pre_commit)
