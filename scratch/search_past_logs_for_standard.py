import os
import json
import re

brain_dir = r"C:\Users\admin\.gemini\antigravity\brain"
pattern = re.compile(r'automation_standard\.md')

print("Searching past conversation logs for automation_standard.md content...")

found = False
for folder in os.listdir(brain_dir):
    folder_path = os.path.join(brain_dir, folder)
    if os.path.isdir(folder_path):
        log_file = os.path.join(folder_path, ".system_generated", "logs", "transcript.jsonl")
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        if 'automation_standard.md' in line:
                            # Parse JSON to see if it was a write_to_file call with the contents
                            try:
                                data = json.loads(line)
                                # Search in tool calls or tool arguments
                                tool_calls = data.get('tool_calls', [])
                                for tc in tool_calls:
                                    args = tc.get('args', {})
                                    target = args.get('TargetFile', '') or args.get('Target', '')
                                    if 'automation_standard.md' in target:
                                        content = args.get('CodeContent', '') or args.get('ReplacementContent', '')
                                        if content:
                                            print(f"MATCH FOUND in folder: {folder}, line {i}")
                                            print(f"Content Length: {len(content)}")
                                            print("Content Preview:")
                                            print(content[:500])
                                            print("-" * 50)
                                            # Write to a backup file
                                            backup_path = f"scratch/backup_standard_{folder}.txt"
                                            with open(backup_path, 'w', encoding='utf-8') as bf:
                                                bf.write(content)
                                            print(f"Saved to {backup_path}")
                                            found = True
                            except Exception:
                                pass
            except Exception as e:
                print(f"Error reading {log_file}: {e}")

if not found:
    print("No matches found in past conversation transcripts.")
