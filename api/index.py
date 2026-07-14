import os
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS ?ㅼ젙
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API ?꾨줉???붾뱶?ъ씤??@app.post("/api/chat")
async def chat_proxy(request: Request):
    try:
        data = await request.json()
        api_key = data.get("apiKey")
        model = data.get("model")
        contents = data.get("contents")
        
        # 蹂댁븞???꾪빐 API Key媛 ?섏뼱?ㅼ? ?딆? 寃쎌슦 ?섍꼍蹂?섏뿉??媛?몄삤嫄곕굹 ?먮윭 諛섑솚
        if not api_key:
             # Vercel ?섍꼍蹂?섏뿉??媛?몄삤湲?(??諛고룷??
             api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            return {"error": "API Key is missing"}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        response = requests.post(url, json={"contents": contents}, timeout=60)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Vercel? 'app' 媛앹껜瑜??붽뎄??# (Next.js ?뱀? Python Runtime ?ㅼ젙???곕씪 ?ㅻ? ???덉쓬)
