import urllib.request
import json

url = "https://api.github.com/repos/hyh54311-dev/jinhae-bot2/contents/api"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        files = json.loads(response.read().decode('utf-8'))
        print("Files in api folder:")
        for f in files:
            print(f"- {f.get('name')} (Size: {f.get('size')} bytes)")
except Exception as e:
    print("Error getting api files:", e)

# Also check root files
url_root = "https://api.github.com/repos/hyh54311-dev/jinhae-bot2/contents"
try:
    req = urllib.request.Request(url_root, headers=headers)
    with urllib.request.urlopen(req) as response:
        files = json.loads(response.read().decode('utf-8'))
        print("\nFiles in root folder:")
        for f in files:
            print(f"- {f.get('name')} (Size: {f.get('size')} bytes)")
except Exception as e:
    print("Error getting root files:", e)
