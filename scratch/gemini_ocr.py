import os
import sys
import base64
import requests
import json

api_key = "AIzaSyCnK2Sbp_facY0A7zveaKU7ClEgURlOI-4"
model = "gemini-2.5-flash"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

def call_gemini_ocr(image_path, prompt):
    print(f"Calling Gemini OCR for: {image_path}...")
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return "Image not found"
        
    try:
        with open(image_path, "rb") as image_file:
            img_data = base64.b64encode(image_file.read()).decode("utf-8")
            
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": "image/png",
                                "data": img_data
                            }
                        }
                    ]
                }
            ]
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, json=payload, timeout=60) # Increased timeout to 60s
        
        if response.status_code == 200:
            result = response.json()
            answer = result['candidates'][0]['content']['parts'][0]['text']
            return answer
        else:
            print(f"API Error ({response.status_code}): {response.text}")
            return f"API Error: {response.text}"
            
    except Exception as e:
        print(f"Exception: {e}")
        return f"Exception: {e}"

if __name__ == "__main__":
    prompt_score = "이 이미지는 시험 문항 배점 표입니다. 표의 모든 내용을 마크다운 테이블로 정리해줘. 특히 황요한 교사의 출제 문항 번호, 배점, 문제 유형(선택형/서술형) 등을 상세히 한국어로 정리해줘."
    score_png = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\lit_score.png"
    
    score_res = call_gemini_ocr(score_png, prompt_score)
    
    # Read existing content first
    out_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\lit_ocr_result.txt"
    try:
        with open(out_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Keep only the Lit Role Result portion (up to the score result header)
            role_part = []
            for line in lines:
                if "=== LIT SCORE RESULT ===" in line:
                    break
                role_part.append(line)
            role_text = "".join(role_part)
    except:
        role_text = "=== LIT ROLE RESULT ===\n(Failed to load existing role text)\n"
        
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(role_text)
        f.write("\n=== LIT SCORE RESULT ===\n")
        f.write(score_res)
        
    print(f"Done. Saved to {out_path}")
