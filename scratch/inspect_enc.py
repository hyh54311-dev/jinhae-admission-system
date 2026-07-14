def check_content(filename):
    print(f"--- {filename} ---")
    with open(filename, 'rb') as f:
        data = f.read()
    
    try:
        print(f"UTF-8: {data.decode('utf-8')[:200]}")
    except Exception as e:
        print(f"UTF-8 FAIL: {e}")
        
    try:
        print(f"CP949: {data.decode('cp949')[:200]}")
    except Exception as e:
        print(f"CP949 FAIL: {e}")

check_content(r"jinhae-bot\jinhae-bot-main\index.html")
