def try_read(filename):
    encodings = ['utf-8', 'cp949', 'euc-kr']
    for enc in encodings:
        try:
            with open(filename, 'r', encoding=enc) as f:
                content = f.read()
                # Check for some Korean characters to confirm
                if any('\uac00' <= c <= '\ud7a3' for c in content):
                    print(f"{filename}: SUCCESS with {enc}")
                    return
        except:
            continue
    print(f"{filename}: FAILED all encodings")

files = [
    r"jinhae-bot\jinhae-bot-main\index.html",
    r"jinhae-bot\jinhae-bot-main\app.js",
    r"jinhae-bot\jinhae-bot-main\index.css",
    r"jinhae-bot\jinhae-bot-main\admission_knowledge.js"
]

for f in files:
    try:
        try_read(f)
    except Exception as e:
        print(f"Error checking {f}: {e}")
