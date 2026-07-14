import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ?섍꼍蹂?섏뿉??API ??濡쒕뱶
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="Kakao Admission Chatbot Webhook")

# 吏??踰좎씠???뚯씪 濡쒕뱶 ?⑥닔
def load_knowledge():
    try:
        # api ?대뜑 ?댁쓽 knowledge.txt ?뚯씪 ?쎄린
        knowledge_path = os.path.join(os.path.dirname(__file__), 'knowledge.txt')
        with open(knowledge_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"吏??踰좎씠???뚯씪 濡쒕뱶 ?ㅽ뙣: {e}")
        return "?낇븰 愿??湲곕낯 ?뺣낫媛 ?놁뒿?덈떎."

KNOWLEDGE_BASE = load_knowledge()

# ?쒖뒪???꾨＼?꾪듃 (?낇븰 ?곷떞????븷 諛?湲곕낯 吏移??ㅼ젙)
SYSTEM_PROMPT = f"""?덈뒗 '吏꾪빐怨좊벑?숆탳'??移쒖젅?섍퀬 ?꾨Ц?곸씤 ?낇븰 ?곷떞 梨쀫큸?댁빞. 
吏?먯옄???숇?紐⑥쓽 吏덈Ц??紐낇솗?섍퀬 媛꾧껐?섍쾶 ?듬??댁쨾.
?꾨옒 ?쒓났??[吏꾪빐怨좊벑?숆탳 ?낇븰 ?덈궡 ?먮즺]瑜?諛뷀깢?쇰줈留??듬????묒꽦?섍퀬, ?덈궡 ?먮즺???녿뒗 ?댁슜?닿굅???뺤콉???뺣떟??以????녿뒗 ?댁슜?대씪硫? "?대떦 ?댁슜? ?낇븰泥?055-546-2260) ?먮뒗 援먮Т?ㅻ줈 臾몄쓽??二쇱떆硫??뺥솗???듬???諛쏆쑝?????덉뒿?덈떎."?쇨퀬 ?덈궡??
??긽 議대뙎留먯쓣 ?ъ슜?섍퀬, ?뺤쨷?섍퀬 ?щ쭩李??댁“濡?留먰빐以?

[吏꾪빐怨좊벑?숆탳 ?낇븰 ?덈궡 ?먮즺]
{KNOWLEDGE_BASE}
"""

def generate_gemini_response(prompt: str) -> str:
    """Gemini API瑜??몄텧?섏뿬 ?듬????앹꽦?⑸땲??"""
    if not GEMINI_API_KEY:
         return "二꾩넚?⑸땲?? 遊??쒕쾭???ㅻ쪟媛 諛쒖깮?덉뒿?덈떎. (API ??誘몄꽕??"
         
    try:
        # 紐⑤뜽 ?ㅼ젙 (媛??理쒖떊/?쒖? 紐⑤뜽??gemini-2.5-pro ?먮뒗 gemini-1.5-pro ?ъ슜 沅뚯옣)
        model = genai.GenerativeModel('gemini-1.5-pro-latest') 
        full_prompt = f"{SYSTEM_PROMPT}\n\n?ъ슜??吏덈Ц: {prompt}\n?듬?:"
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "二꾩넚?⑸땲?? ?쒕쾭 泥섎━ 以??ㅻ쪟媛 諛쒖깮?덉뒿?덈떎. ?좎떆 ???ㅼ떆 ?쒕룄??二쇱꽭??"

@app.post("/api/chat")
async def kakao_chat(request: Request):
    """移댁뭅??i ?ㅽ뵂鍮뚮뜑?먯꽌 ?ㅻ뒗 ?ㅽ궗 ?곗씠?곕? 泥섎━?⑸땲??"""
    payload = await request.json()
    
    # 移댁뭅?ㅽ넚 諛쒗솕 ?댁슜 異붿텧 (?ㅽ뵂鍮뚮뜑 Payload ?ㅽ럺)
    try:
        user_utterance = payload.get("userRequest", {}).get("utterance", "")
    except Exception:
        user_utterance = ""

    # 吏덈Ц??鍮꾩뼱?덉쓣 寃쎌슦 ?덉쇅 泥섎━
    if not user_utterance:
        bot_responseText = "留먯??섏떊 ?댁슜?????댄빐?섏? 紐삵뻽?댁슂. ?ㅼ떆 ??踰?吏덈Ц??二쇱떆寃좎뼱??"
    else:
        # Gemini API瑜??듯빐 ?듬? ?앹꽦
        bot_responseText = generate_gemini_response(user_utterance)
    
    # 移댁뭅??i ?ㅽ뵂鍮뚮뜑 ?묐떟 ?щ㎎ (SimpleText ?뺤떇)
    kakao_response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": bot_responseText
                    }
                }
            ]
        }
    }
    
    return JSONResponse(content=kakao_response)

# Vercel ?섍꼍???꾨땶 濡쒖뺄 ?뚯뒪?????ㅽ뻾?섎뒗 ?ㅼ젙
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True)
