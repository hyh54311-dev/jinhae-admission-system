# -*- coding: utf-8 -*-
import os
import sys
import json
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

def run_test_harness():
    client = TestClient(app)
    
    test_cases = [
        {
            "id": 1,
            "category": "야간자율학습 (기숙사생)",
            "question": "기숙사생인데 자율학습은 언제 어디서 해?",
            "use_history": False
        },
        {
            "id": 2,
            "category": "야간자율학습 (통학생)",
            "question": "기숙사 안 쓰는 통학생도 자율학습 참여할 수 있어?",
            "use_history": False
        },
        {
            "id": 3,
            "category": "야간자율학습 (공간 규칙)",
            "question": "기숙사생은 무조건 기숙사에서만 자율학습 해야 하나요?",
            "use_history": False
        },
        {
            "id": 4,
            "category": "신입생 합격 커트라인",
            "question": "작년에 입학 커트라인이 몇 퍼센트였어?",
            "use_history": False
        },
        {
            "id": 5,
            "category": "중학교별 진학생 수 (진해남중)",
            "question": "작년에 진해남중에서 몇 명이나 입학했는지 알려줘.",
            "use_history": False
        },
        {
            "id": 6,
            "category": "중학교별 진학생 수 (진해중)",
            "question": "진해중학교 출신 신입생은 몇 명이야?",
            "use_history": False
        },
        {
            "id": 7,
            "category": "중학교별 진학생 수 (냉천중)",
            "question": "냉천중학교 출신 신입생 수 알려줘.",
            "use_history": False
        },
        {
            "id": 8,
            "category": "대화 맥락 테스트 1 (장학금 질문)",
            "question": "1인이 최대로 많이 받은 장학금이 얼마야?",
            "use_history": False
        },
        {
            "id": 9,
            "category": "대화 맥락 테스트 2 (대명사/생략)",
            "question": "한 사람당은?",
            "use_history": True,
            "history": [
                {"role": "user", "message": "1인이 최대로 많이 받은 장학금이 얼마야?"},
                {"role": "bot", "message": "질문하신 장학금의 세부적인 개인별 수혜 금액에 대해서는, 개인정보 보호 및 지급 기준에 따라 일률적으로 공개하기 어렵습니다. 다만, 진해고등학교는 연간 약 1억 원 규모의 장학금을 운영하고 있으며 다양한 장학 제도가 마련되어 있습니다."}
            ]
        },
        {
            "id": 10,
            "category": "미답변 항목 방어 (교장 선생님)",
            "question": "진해고 교장 선생님 성함이 어떻게 되시나요?",
            "use_history": False
        }
    ]
    
    results = []
    
    print("Starting 10-Question Test Harness...")
    for tc in test_cases:
        qid = tc["id"]
        cat = tc["category"]
        q = tc["question"]
        print(f"Running Test {qid}/{len(test_cases)}: {cat}...")
        
        payload = {"message": q}
        if tc.get("use_history") and tc.get("history"):
            payload["history"] = tc["history"]
            
        try:
            response = client.post("/api/chat", json=payload)
            if response.status_code == 200:
                answer = response.text
                status = "PASS"
            else:
                answer = f"Error: Status code {response.status_code}"
                status = "FAIL"
        except Exception as e:
            answer = f"Exception: {e}"
            status = "FAIL"
            
        results.append({
            "id": qid,
            "category": cat,
            "question": q,
            "answer": answer,
            "status": status
        })
        
    # Generate Markdown report
    report_path = r"C:\Users\admin\.gemini\antigravity\brain\6f17156b-cb5e-4877-bdba-1ea12d375810\test_results.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 챗봇 통합 테스트 하네스 검증 보고서\n\n")
        f.write("본 문서는 챗봇 백엔드 엔진에 최근 업데이트된 데이터 및 대화 컨텍스트 기능의 정상 작동 여부를 검증하기 위한 10대 핵심 질문 테스트 결과입니다.\n\n")
        
        f.write("## 📊 테스트 결과 요약\n")
        f.write("| 순번 | 분류 | 테스트 질문 | 결과 |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for res in results:
            f.write(f"| {res['id']} | {res['category']} | {res['question']} | {res['status']} |\n")
        f.write("\n---\n\n## 📝 상세 테스트 응답 로그\n")
        for res in results:
            f.write(f"### [Test {res['id']}] {res['category']}\n")
            f.write(f"* **Q**: {res['question']}\n")
            f.write(f"* **A**:\n{res['answer']}\n\n")
            f.write("-" * 50 + "\n\n")
            
    print(f"Test complete. Markdown report generated at {report_path}")

if __name__ == '__main__':
    run_test_harness()
