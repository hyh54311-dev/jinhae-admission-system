import os
import json
import re

brain_dir = r"C:\Users\admin\.gemini\antigravity\brain"

print("Searching past conversation logs for raw references...")
found_count = 0

for folder in os.listdir(brain_dir):
    folder_path = os.path.join(brain_dir, folder)
    if os.path.isdir(folder_path):
        log_file = os.path.join(folder_path, ".system_generated", "logs", "transcript.jsonl")
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        if 'automation_standard' in line:
                            print(f"Match found in folder {folder}, line {i}")
                            # Print a snippet of the line
                            print(line[:300] + "...")
                            found_count += 1
            except Exception as e:
                pass

print(f"Total matches found: {found_count}")
