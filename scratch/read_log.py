# -*- coding: utf-8 -*-
import json
import os
import sys

# Ensure UTF-8 output
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

log_path = r'C:\Users\admin\.gemini\antigravity\brain\337abfaa-2ae1-4a62-9818-dab08b9eb7a5\.system_generated\logs\transcript.jsonl'

if not os.path.exists(log_path):
    print("Log path does not exist.")
    sys.exit(1)

with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f):
        try:
            data = json.loads(line)
            step = data.get("step_index", i)
            source = data.get("source", "")
            type_ = data.get("type", "")
            content = data.get("content", "")
            
            if type_ == "USER_INPUT":
                print(f"=== STEP {step} [USER] ===")
                print(content[:1000])
                print("="*40)
            elif source == "MODEL" and type_ == "PLANNER_RESPONSE" and ("404" in content or "m.stock" in content or "mstock" in content):
                print(f"=== STEP {step} [MODEL PLANNER] ===")
                print(content[:1000])
                print("="*40)
            elif type_ == "RUN_COMMAND" and ("404" in content or "m.stock" in content or "mstock" in content):
                print(f"=== STEP {step} [COMMAND RESPONSE] ===")
                print(content[:1000])
                print("="*40)
        except Exception as e:
            pass
