import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc_id = "170cdJIDtPi47zL_bKr6bi8RqhY_LPoNBCwRxY2J2Fw8"
txt_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"

print(f"Fetching Google Doc TXT Export for ID: {doc_id}...")

try:
    req = urllib.request.Request(txt_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        print("=== Content Preview (First 1500 chars) ===")
        print(content[:1500])
        with open(r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\scratch\gdoc_170cd.txt", "w", encoding='utf-8') as f:
            f.write(content)
except Exception as e:
    print(f"Error fetching TXT export: {e}")
