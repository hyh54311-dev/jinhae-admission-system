import urllib.request
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

doc_id = "1InMLEURyJazMsgMmEJsInKsxLQ5VMgDTPSv6LHTa-Ck"
txt_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
pdf_url = f"https://docs.google.com/document/d/{doc_id}/export?format=pdf"

LOCAL_DIR = r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\scratch"

print(f"Fetching Google Doc TXT for ID: {doc_id}...")

try:
    req = urllib.request.Request(txt_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        print(f"=== Content Length: {len(content)} chars ===")
        with open(os.path.join(LOCAL_DIR, "lesson_plan_1InMLEUR.txt"), "w", encoding='utf-8') as f:
            f.write(content)
        print("\n--- Lesson Plan Document Content ---")
        print(content[:3000])
except Exception as e:
    print(f"Error fetching TXT export: {e}")

try:
    req = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp, open(os.path.join(LOCAL_DIR, "lesson_plan_1InMLEUR.pdf"), "wb") as f:
        f.write(resp.read())
    print("\nDownloaded PDF export successfully!")
except Exception as e:
    print(f"Error fetching PDF export: {e}")
