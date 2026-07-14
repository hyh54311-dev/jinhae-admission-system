import sys

# Force stdout to be utf-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

log_path = 'C:/Users/admin/.gemini/antigravity/brain/d84b3a92-9d17-4a5a-81b1-20511d474960/.system_generated/tasks/task-53.log'

with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

print(f"Total lines in log: {len(lines)}")
print("First 25 lines of task-53.log:")
for line in lines[:25]:
    print(line, end='')
