import google.generativeai as genai
import sys

# API ?ㅼ젙
API_KEY = "os.getenv("GEMINI_API_KEY")"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

SAMPLES = [
    {"isB": False, "data": "?μ냼(?꾩꽌愿), ?뚮━(梨낆옣 ?섍린???뚮━), ?섎Т(?먭꺽利?怨듬?), ?댁쭞(??紐⑥쓬吏??쎄린), 湲곕텇(李⑤텇??, ?ㅼ쭚(吏꾨줈?????源딆씠 怨좊???"},
    {"isB": True, "data": "怨듦컙(?먯뒿??, 遺?꾨윭?(?댁젣 ??섎뜕 湲곗뼲), ?ㅼ쭚(?ㅻ뒛遺??留ㅼ씪 1?몄뵫 ?쎄린)"},
    {"isB": False, "data": "?μ냼(怨듭썝), ?뚮━(諛붾엺 ?뚮━), ?섎Т(?곸뼱 ?⑥뼱 ?붽린), ?댁쭞(援щ쫫 援ш꼍), 湲곕텇(?곸풄??, ?ㅼ쭚(?ъ쑀濡쒖슫 留덉쓬?쇰줈 怨듬???"}
]

def create_prompt_v8(data_str):
    return f"""怨좉탳 援?뼱 援먯궗濡쒖꽌 "?ㅻ룞二쇱쓽 '?쎄쾶 ?뚯뼱吏???瑜??듯빐"濡??쒖옉?섍퀬 紐낆궗???대?(~?? ~??濡??앸굹???숈깮 ?앺솢湲곕줉遺 ?명듅???묒꽦?섏꽭??
[議곌굔]
1. 遺꾨웾: ?쒓? 100???댁긽 (諛붿씠??300 ?댁긽)
2. 臾몄껜: 紐낆궗???대? ?꾧껐
?낅젰: {data_str}
異쒕젰:"""

print("Running 3-case simulation...")
sys.stdout.flush()

for i, sample in enumerate(SAMPLES):
    try:
        response = model.generate_content(create_prompt_v8(sample["data"]), generation_config={"temperature": 0.7})
        print(f"[CASE {i+1}] {response.text.strip()}")
    except Exception as e:
        print(f"[CASE {i+1}] Error: {str(e)}")
    sys.stdout.flush()

