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

def test_self_study_questions():
    client = TestClient(app)
    
    questions = [
        "자율학습은 언제, 어디에서 해요?",
        "기숙사가 아닌 학생들은 자율학습 못해요?",
        "기숙사에 들어가면 자율학습은 기숙사 안에서만 해요? 교실에서는 안해요?"
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
    test_self_study_questions()
