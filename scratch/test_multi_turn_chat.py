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

def test_multi_turn():
    client = TestClient(app)
    
    # Simulate a conversation history
    # Turn 1: User asks about scholarship amount
    history = [
        {"role": "user", "message": "1인이 최대로 많이 받은 장학금이 얼마야?"},
        {"role": "bot", "message": "질문하신 장학금의 세부적인 개인별 수혜 금액에 대해서는, 개인정보 보호 및 지급 기준에 따라 일률적으로 공개하기 어렵습니다. 다만, 진해고등학교는 연간 약 1억 원 규모의 장학금을 운영하고 있으며 다양한 장학 제도가 마련되어 있습니다."}
    ]
    
    # Turn 2: User asks a follow-up "한 사람당은?"
    follow_up = "한 사람당은?"
    
    print(f"\nSending follow-up query: '{follow_up}' with previous turn context...")
    try:
        response = client.post("/api/chat", json={
            "message": follow_up,
            "history": history
        })
        print(f"Status: {response.status_code}")
        print("Response:")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_multi_turn()
