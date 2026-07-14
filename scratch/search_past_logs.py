import os
import json

log_path = r"C:\Users\admin\.gemini\antigravity\brain\d84b3a92-9d17-4a5a-81b1-20511d474960\.system_generated\logs\transcript.jsonl"

if not os.path.exists(log_path):
    print("Log file not found at:", log_path)
else:
    print("Log file found! Searching...")
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if 'script.google.com' in line:
                    try:
                        data = json.loads(line)
                        content = data.get('content', '')
                        print(f"Line {i} content contains script link:")
                        # Print occurrences of script.google.com
                        import re
                        urls = re.findall(r'https://script\.google\.com/macros/s/[a-zA-Z0-9-_]+/exec', line)
                        print("  URLs found:", urls)
                    except Exception as e:
                        print(f"Error parsing line {i}: {e}")
    except Exception as e:
        print("Error reading log:", e)
