import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    "https://jinhae-bot2.vercel.app/api/health",
    "https://jinhae-bot2-qntp0dg1b-hyh54311-5307s-projects.vercel.app/api/health"
]

for url in urls:
    try:
        print(f"Testing URL: {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            print("Response:", data)
    except Exception as e:
        print("Failed:", e)
    print("-" * 50)
