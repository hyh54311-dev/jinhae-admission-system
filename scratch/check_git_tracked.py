# -*- coding: utf-8 -*-
import subprocess
import os

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"

def run_git_command(args):
    try:
        res = subprocess.run(['git'] + args, cwd=base_dir, capture_output=True, text=True)
        return res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return "", str(e)

def main():
    print("Checking if files containing hardcoded keys are tracked by Git...")
    files = [
        "performance_seteuk_system/config.js",
        "scratch/gemini_ocr.py",
        "scratch/test_flash_lite.py",
        "scratch/test_gemini.py"
    ]
    
    # We don't have git in system path in default command runner, but let's try calling it.
    # Wait, earlier 'git' worked in the user's CMD prompt because they have Git installed on their machine!
    # So if we run it through subprocess.run, it should work if git is in their system PATH (which it is since they ran it in CMD successfully).
    for file in files:
        stdout, stderr = run_git_command(["ls-files", file])
        if stdout:
            print(f"- [TRACKED] {file}")
        else:
            print(f"- [NOT TRACKED] {file} (stderr: {stderr})")

if __name__ == '__main__':
    main()
