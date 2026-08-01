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

def test_cutline_questions():
    client = TestClient(app)
    
    questions = [
        "작년 커트라인이 어떻게 돼?",
        "입학 성적은 어느 정도 되어야 할까요?"
    ]
    
    for q in questions:
        print(f"\n==================== QUESTION: {q} ====================")
        try:
            response = client.post("/api/chat", json={"message": q})
            print(f"Status: {response.status_code}")
            print(response.text)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    test_cutline_questions()
