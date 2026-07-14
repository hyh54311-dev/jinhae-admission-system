import os
import json

log_path = r"C:\Users\admin\.gemini\antigravity\brain\b9b64f7c-7080-4072-828b-8c245365299b\.system_generated\logs\transcript.jsonl"

if os.path.exists(log_path):
    print("Log file found! Scanning...")
    with open(log_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if 'automation_standard.md' in line or 'automation_standard' in line:
                print(f"Match found at line {i}:")
                # Parse to see if it's a tool call
                try:
                    data = json.loads(line)
                    print(f"  Type: {data.get('type')}")
                    # Print tool calls or content
                    tool_calls = data.get('tool_calls', [])
                    for tc in tool_calls:
                        args = tc.get('args', {})
                        if 'automation_standard' in str(args):
                            print("  Tool args CodeContent:")
                            print(args.get('CodeContent', 'None')[:800])
                            print("=" * 60)
                except Exception as e:
                    print("  Error parsing JSON:", e)
                    print(line[:300] + "...")
else:
    print("Log not found.")
