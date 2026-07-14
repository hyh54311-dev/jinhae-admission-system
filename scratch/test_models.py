import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models_to_test = ['gemini-3.1-flash', 'gemini-3.1-flash-lite']

print(f"Testing models with API Key: {api_key[:10]}...")

for model_name in models_to_test:
    print(f"\n--- Testing {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        start_time = time.time()
        response = model.generate_content("진해고등학교에 대해 짧게 설명해줘.")
        end_time = time.time()
        
        print(f"Status: SUCCESS")
        print(f"Response Time: {end_time - start_time:.2f}s")
        print(f"Response Preview: {response.text[:100]}...")
    except Exception as e:
        print(f"Status: FAILED")
        print(f"Error: {e}")

print("\nTests completed.")
