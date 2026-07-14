import os
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

brain_dir = r"C:\Users\admin\.gemini\antigravity\brain"
print("Scanning all logs for raw references to 'automation_standard'...")

found = False
for folder in os.listdir(brain_dir):
    folder_path = os.path.join(brain_dir, folder)
    if os.path.isdir(folder_path):
        log_file = os.path.join(folder_path, ".system_generated", "logs", "transcript.jsonl")
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        if 'automation_standard' in line:
                            # Skip current conversation matches to avoid clutter
                            if '3a893774-eea9-416e-b8a6-74d2b3ca8bc6' in log_file:
                                continue
                            print(f"Match in {folder} line {i}:")
                            print(f"  {line[:400]}...")
                            found = True
            except Exception as e:
                pass

if not found:
    print("No matches in past conversations.")
