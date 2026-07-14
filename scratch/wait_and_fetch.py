import time
import urllib.request

url = "https://jinhae-bot2.vercel.app/"
print("Sleeping for 40 seconds to allow Vercel build to complete...")
time.sleep(40)

try:
    print("Fetching URL...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
    if "2027학년도" in html:
        print("VERIFICATION_SUCCESS: The page now correctly contains '2027학년도'!")
    else:
        print("VERIFICATION_FAILED: The page still contains '2026학년도'. Cache or deployment delay.")
except Exception as e:
    print(f"Error fetching URL: {e}")
