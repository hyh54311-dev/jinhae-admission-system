import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cloud_daily_news import call_gemini_api
from dotenv import load_dotenv

load_dotenv()

def test_modified_logic():
    print("Testing modified call_gemini_api logic...")
    try:
        # 이 테스트는 실제 API 키가 있는 경우에만 유효합니다.
        # 단순히 함수 호출이 가능한지 확인합니다.
        result = call_gemini_api("Hello")
        if result:
            print(f"Success! Result: {result[:50]}...")
        else:
            print("No result (this might be expected if no key is set)")
    except Exception as e:
        print(f"Caught exception: {e}")

if __name__ == "__main__":
    test_modified_logic()
