# -*- coding: utf-8 -*-
import os
import sys
from fastapi.testclient import TestClient

# Add chatbot directory to path
base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
bot_dir = os.path.join(base_dir, "jinhae-bot", "jinhae-bot-main")
sys.path.append(bot_dir)

# Load env variables
from dotenv import load_dotenv
env_path = os.path.join(bot_dir, "api", ".env")
load_dotenv(env_path)

# Import app from api.index
from api.index import app

def test_chat():
    print("Initializing TestClient...")
    client = TestClient(app)
    
    question = "2026학년도 대입 결과(서울대, 의예과 등 합격자 수) 알려줘."
    print(f"Sending request: '{question}'")
    
    # Send request to chat endpoint (handles streaming)
    try:
        response = client.post("/api/chat", json={"message": question})
        print(f"Status Code: {response.status_code}")
        print("\n--- Response Content ---")
        print(response.text)
        print("------------------------")
    except Exception as e:
        print(f"Error testing chatbot: {e}")

if __name__ == '__main__':
    test_chat()
