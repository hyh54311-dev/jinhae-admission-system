import os

def check_content(filename):
    if not os.path.exists(filename):
        print(f"NOT FOUND: {filename}")
        return
    print(f"--- {filename} ---")
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Try CP949 first (common source)
    try:
        print(f"CP949: {data.decode('cp949')[:200]}")
    except Exception as e:
        print(f"CP949 FAIL: {e}")

    try:
        print(f"UTF-8: {data.decode('utf-8')[:200]}")
    except Exception as e:
        print(f"UTF-8 FAIL: {e}")

# Find index.html in temp_unzip (it might be nested)
for root, dirs, files in os.walk("temp_unzip"):
    for file in files:
        if file == "index.html":
            check_content(os.path.join(root, file))
        if file == "app.js":
            check_content(os.path.join(root, file))
