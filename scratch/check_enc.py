import chardet

def check_encoding(filename):
    with open(filename, 'rb') as f:
        rawdata = f.read()
    result = chardet.detect(rawdata)
    print(f"{filename}: {result}")

files = [
    r"jinhae-bot\jinhae-bot-main\index.html",
    r"jinhae-bot\jinhae-bot-main\app.js",
    r"jinhae-bot\jinhae-bot-main\index.css",
    r"jinhae-bot\jinhae-bot-main\admission_knowledge.js"
]

for f in files:
    try:
        check_encoding(f)
    except Exception as e:
        print(f"Error checking {f}: {e}")
