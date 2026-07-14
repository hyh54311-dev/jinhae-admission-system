import requests
import re
import sys
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.stdout.reconfigure(encoding='utf-8')

url = "https://docs.google.com/spreadsheets/d/1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU/edit?usp=sharing"

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    r = requests.get(url, headers=headers, verify=False)
    print("Response status:", r.status_code)
    
    # Search for "forms" or "form" in the response text
    matches = re.findall(r'https://docs.google.com/forms/[^\s"]+', r.text)
    print("Found Form Links:")
    for m in set(matches):
        print("  ", m)
        
    # Search for any form-related JSON in the page source
    # Sometimes there is a form url inside bootstrap data
    for line in r.text.split('\n'):
        if 'forms/d' in line:
            print("Form line found:")
            print(line[:500])
except Exception as e:
    print("Error:", e)
