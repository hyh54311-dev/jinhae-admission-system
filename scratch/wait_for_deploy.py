# -*- coding: utf-8 -*-
import requests
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    url = "https://jinhae-bot2.vercel.app/api/health"
    start_time = time.time()
    timeout = 120  # 2 minutes timeout
    
    print("Polling jinhae-bot2.vercel.app/api/health for version v2.2...")
    
    while True:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                version = data.get("version")
                print(f"[{int(time.time() - start_time)}s] Current version: {version}")
                if version == "v2.2":
                    print("SUCCESS! Deployment completed successfully!")
                    break
            else:
                print(f"[{int(time.time() - start_time)}s] Error: Status code {response.status_code}")
        except Exception as e:
            print(f"[{int(time.time() - start_time)}s] Connection error: {e}")
            
        if time.time() - start_time > timeout:
            print("TIMEOUT! Vercel did not deploy version v2.2 in time.")
            break
            
        time.sleep(5)

if __name__ == '__main__':
    main()
