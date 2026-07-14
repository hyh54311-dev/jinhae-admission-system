import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

import sys
import io

# UTF-8 異쒕젰 媛뺤젣 ?ㅼ젙
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

if not api_key:
    print("Error: GEMINI_API_KEY is not set.")
else:
    print(f"Success: Environment variable loaded (Last 4 chars: {api_key[-4:]})")
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-3.1-flash-lite')
        response = model.generate_content("?깃났?곸쑝濡??곌껐?섏뿀?섏슂?")
        print(f"?? ?묐떟 ?깃났: {response.text}")
    except Exception as e:
        print(f"??API ?몄텧 ?ㅽ뙣: {e}")
