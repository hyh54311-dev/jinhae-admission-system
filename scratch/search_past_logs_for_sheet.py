import os
import json
import re

log_path = r"C:\Users\admin\.gemini\antigravity\brain\d84b3a92-9d17-4a5a-81b1-20511d474960\.system_generated\logs\transcript.jsonl"

if os.path.exists(log_path):
    print("Log file found!")
    pattern_sheet = re.compile(r'1[a-zA-Z0-9-_]{43}')
    found_ids = set()
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            matches = pattern_sheet.findall(line)
            for m in matches:
                found_ids.add(m)
    print("All 44-character IDs found in log:")
    for m in found_ids:
        print("  -", m)
else:
    print("Log not found.")
