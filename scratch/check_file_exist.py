import os

standard_path = "automation_standard.md"
print("File exists:", os.path.exists(standard_path))
if os.path.exists(standard_path):
    print("Size:", os.path.getsize(standard_path))
    # read first 200 chars and last 200 chars
    try:
        with open(standard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print("First 200 chars:")
        print(content[:200])
        print("\nLast 200 chars:")
        print(content[-200:])
    except Exception as e:
        print("Error reading:", e)
