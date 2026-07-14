import os
import sys
import uvicorn
import requests
import io
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Force UTF-8 encoding for Windows console output
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

app = FastAPI()

# CORS ?ㅼ젙 (釉뚮씪?곗? 蹂댁븞 ?뺤콉 ?닿껐)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ?뺤쟻 ?뚯씪 ?쒕튃 (CSS, JS, ?대?吏)
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

# Gemini API ?꾨줉???붾뱶?ъ씤??@app.post("/api/chat")
async def chat_proxy(request: Request):
    data = await request.json()
    api_key = data.get("apiKey")
    model = data.get("model")
    contents = data.get("contents")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    try:
        response = requests.post(url, json={"contents": contents}, timeout=60)
        res_json = response.json()
        if "error" in res_json:
            print(f"??Google API Error: {res_json['error']}")
        return res_json
    except Exception as e:
        print(f"?좑툘 Proxy Server Exception: {str(e)}")
        return {"error": str(e)}

@app.get("/{file_path:path}")
async def get_static_file(file_path: str):
    full_path = os.path.join(BASE_DIR, file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(full_path)
    return HTMLResponse("File not found", status_code=404)

if __name__ == "__main__":
    print("--------------------------------------------------")
    print("Jinhae High School Chatbot 2.0 Local Server")
    print("Address: http://localhost:8000")
    print("--------------------------------------------------")
    
    import webbrowser
    webbrowser.open("http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
