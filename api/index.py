import os
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"status": "alive", "message": "Jinhae High School Admission Chatbot API Server is running."}

# Gemini API Chat Proxy Endpoint
@app.post("/api/chat")
async def chat_proxy(request: Request):
    try:
        data = await request.json()
        api_key = data.get("apiKey")
        model = data.get("model")
        contents = data.get("contents")
        
        # Fallback to Vercel environment variables if API Key is not passed in request
        if not api_key:
             api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            return {"error": "API Key is missing"}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        response = requests.post(url, json={"contents": contents}, timeout=60)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
