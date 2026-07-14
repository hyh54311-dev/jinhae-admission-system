import urllib.request
import json

url = "https://api.github.com/repos/hyh54311-dev/jinhae-bot2/commits"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        commits = json.loads(response.read().decode('utf-8'))
        print("Latest Commits:")
        for c in commits[:3]:
            commit_info = c.get('commit', {})
            author = commit_info.get('author', {}).get('name')
            date = commit_info.get('author', {}).get('date')
            msg = commit_info.get('message')
            print(f"- Author: {author} | Date: {date}")
            print(f"  Msg: {msg}")
except Exception as e:
    print("Error getting commits:", e)

# Also check file content
file_url = "https://raw.githubusercontent.com/hyh54311-dev/jinhae-bot2/main/api/index.py"
try:
    req = urllib.request.Request(file_url, headers=headers)
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
        print("\nChecking raw api/index.py from GitHub:")
        if "to_thread" in content:
            print("-> CONTAINS to_thread (Updated!)")
        else:
            print("-> DOES NOT CONTAIN to_thread (STILL OLD!)")
except Exception as e:
    print("Error getting file:", e)
