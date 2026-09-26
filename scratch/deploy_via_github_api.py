# -*- coding: utf-8 -*-
import subprocess
import urllib.request
import json
import base64
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Get token from Git Credential Manager
p = subprocess.Popen(
    ['git', 'credential-manager', 'get'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
stdout, _ = p.communicate(input="protocol=https\nhost=github.com\n\n")
token = ""
for line in stdout.splitlines():
    if line.startswith("password="):
        token = line.split("=", 1)[1]
        break

if not token:
    print("Failed to get GitHub token.")
    sys.exit(1)

print("Retrieved token successfully.")

repo = "hyh54311-dev/jinhae-bot2"
files_to_update = ["index.html", "app.js", "api/index.py"]
local_base = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\jinhae-bot\jinhae-bot-main"

for file_path in files_to_update:
    local_full_path = f"{local_base}\\{file_path.replace('/', '\\')}"
    with open(local_full_path, 'rb') as f:
        content_bytes = f.read()
    
    content_b64 = base64.b64encode(content_bytes).decode('utf-8')
    
    # Get current file SHA
    get_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    req = urllib.request.Request(get_url, headers={
        "Authorization": f"Bearer {token}",
        "User-Agent": "Antigravity-Deployer",
        "Accept": "application/vnd.github.v3+json"
    })
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            sha = data.get("sha")
            print(f"Current SHA for {file_path}: {sha}")
    except Exception as e:
        print(f"Error getting SHA for {file_path}: {e}")
        continue
        
    # Update file via PUT
    put_data = json.dumps({
        "message": f"feat: apply security hardening v3.7 (XSS sanitization, 300-char input limit, prompt injection hard guardrails) on {file_path}",
        "content": content_b64,
        "sha": sha,
        "branch": "main"
    }).encode('utf-8')
    
    put_req = urllib.request.Request(get_url, data=put_data, method="PUT", headers={
        "Authorization": f"Bearer {token}",
        "User-Agent": "Antigravity-Deployer",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    })
    
    try:
        with urllib.request.urlopen(put_req) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            print(f"✅ Successfully updated {file_path} on GitHub main branch! New Commit: {res_data.get('commit', {}).get('sha')[:7]}")
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")

