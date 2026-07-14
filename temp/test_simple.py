import google.generativeai as genai
import sys

API_KEY = "os.getenv("GEMINI_API_KEY")"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

print("Starting test...")
sys.stdout.flush()

try:
    response = model.generate_content("Hello, this is a test. Please reply with 'OK'.")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")
sys.stdout.flush()

