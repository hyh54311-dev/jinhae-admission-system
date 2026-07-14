import os
import sys
import json
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.getcwd())

import cloud_daily_news

def test_error_handling():
    print("Testing error handling in cloud_daily_news.py...")
    
    # Mocking GEMINI_API_KEY
    cloud_daily_news.GEMINI_API_KEY = "dummy_key"
    
    # 1. Test API error (e.g., 400 Bad Request)
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request: Invalid model name"
        mock_post.return_value = mock_response
        
        print("\n--- Testing API 400 Error ---")
        try:
            cloud_daily_news.call_gemini_api("Test prompt")
        except Exception as e:
            print(f"Correctly caught and re-raised: {e}")

    # 2. Test Empty Candidates (Safety Filter)
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"candidates": []}
        mock_post.return_value = mock_response
        
        print("\n--- Testing Empty Candidates ---")
        result = cloud_daily_news.call_gemini_api("Test prompt")
        print(f"Result (should be None): {result}")

    # 3. Test Telegram Failure (should not crash)
    cloud_daily_news.TELEGRAM_TOKEN = "dummy_token"
    cloud_daily_news.TELEGRAM_CHAT_ID = "dummy_id"
    with patch('requests.post') as mock_post:
        mock_post.side_effect = Exception("Connection timed out")
        
        print("\n--- Testing Telegram Connection Error ---")
        cloud_daily_news.send_telegram_message("Test message")
        print("Success: Script did not crash on Telegram error")

if __name__ == "__main__":
    test_error_handling()
