import requests
import base64
import json
import os

# API ?ㅼ젙 (?ъ슜??肄붾뱶?????쒖슜)
API_KEY = "os.getenv("GEMINI_API_KEY")"
MODEL_NAME = "models/gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/{MODEL_NAME}:generateContent?key={API_KEY}"

callerIdentity = "?쒕??덉씠???뚯뒪????곸옄"
prompt = f"""?덈뒗 援?뼱 ?좎깮?섏쓽 ?낅Т 鍮꾩꽌?? ?듯솕 ?곷? '{callerIdentity}'????댁슜???대え吏瑜??욎뼱 以꾧?濡??곸꽭 ?붿빟?댁쨾.
             留뚯빟 ?뚯쓬留??ㅻ┛?ㅻ㈃ '?댁슜 ?놁쓬'?대씪怨??듬???
             ?붿껌?ы빆?대굹 ???쇱? 留덉?留됱뿉 '*'濡??쒖옉?섎뒗 以꾩뿉 ?뺣━?댁쨾."""

# ?뚯뒪?몄슜 吏㏃? ?띿뒪??Base64) ?꾩넚 (媛吏??ㅻ뵒???먮굦?쇰줈 ?띿뒪???꾨떖)
dummy_text = "?덈뀞?섏꽭?? ?⑹슂???좎깮?? ?ㅼ쓬 二??붿슂???숆탳 諛⑸Ц ?덉젙?낅땲?? ?쒓컙 愿쒖갖?쇱떊媛??"
base64Data = base64.b64encode(dummy_text.encode('utf-8')).decode('utf-8')
mimeType = "text/plain" # ?ㅼ젣濡쒕뒗 audio/mp4 寃좎?留? API ?듭떊 ?먯껜媛 ?섎뒗吏 ?뺤씤?섍린 ?꾪븿

payload = { 
    "contents": [{ "parts": [{ "text": prompt }, { "inlineData": { "mimeType": mimeType, "data": base64Data } }] }],
    "safetySettings": [
        { "category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE" },
        { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE" },
        { "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE" },
        { "category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE" }
    ]
}

headers = {
    "Content-Type": "application/json"
}

print(f"--- Gemini API ?쒕??덉씠???쒖옉 (紐⑤뜽: {MODEL_NAME}) ---")

try:
    response = requests.post(URL, headers=headers, data=json.dumps(payload))
    code = response.status_code
    
    print(f"\n[HTTP ?곹깭 肄붾뱶]: {code}")
    
    if code != 200:
        print("[?먮윭 ?묐떟 蹂몃Ц]:")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
    else:
        result = response.json()
        print("[?뺤긽 ?묐떟 蹂몃Ц 援ъ“ ?쇰?]:")
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                text = candidate['content']['parts'][0].get('text', '')
                print(f"??異붿텧???붿빟 ?띿뒪??\n{text.strip()}")
            elif 'finishReason' in candidate:
                print(f"???띿뒪???앹꽦 遺덇? (醫낅즺 ?ъ쑀: {candidate['finishReason']})")
        else:
             print("???????녿뒗 ?묐떟 援ъ“")

except Exception as e:
    print(f"[?곌껐 ?ㅻ쪟 諛쒖깮]: {str(e)}")

print("\n--- ?쒕??덉씠??醫낅즺 ---")
