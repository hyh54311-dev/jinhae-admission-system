import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

log_path = r"C:\Users\admin\.gemini\antigravity\brain\b9b64f7c-7080-4072-828b-8c245365299b\.system_generated\logs\transcript.jsonl"

if os.path.exists(log_path):
    print("Log file found! Scanning for all matches...")
    with open(log_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if 'automation_standard' in line:
                print(f"Match found at line {i}:")
                for m in re.finditer(r'automation_standard', line):
                    start = max(0, m.start() - 100)
                    end = min(len(line), m.end() + 200)
                    print(f"  Context: ...{line[start:end]}...")
else:
    print("Log not found.")
