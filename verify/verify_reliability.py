import os
import json
import asyncio
import sys
from typing import List, Dict

# ?꾨줈?앺듃 猷⑦듃 諛?梨쀫큸 API 寃쎈줈 異붽?
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bot_root = os.path.join(project_root, 'jinhae-bot', 'jinhae-bot-main')
sys.path.append(bot_root)

import google.generativeai as genai
from dotenv import load_dotenv

# kakao_bot/api/index.py??濡쒖쭅???쒕??덉씠?섑븯湲??꾪븳 ?⑥닔??
def load_knowledge():
    knowledge_path = os.path.join(bot_root, 'api', 'knowledge.txt')
    with open(knowledge_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_system_prompt(knowledge_base):
    return f"""?덈뒗 '吏꾪빐怨좊벑?숆탳'??移쒖젅?섍퀬 ?꾨Ц?곸씤 ?낇븰 ?곷떞 ?꾨Ц媛?? 
吏?먯옄???숇?紐⑥쓽 吏덈Ц??紐낇솗?섍퀬 ?좊ː媛??덇쾶 ?듬??댁쨾.

[?곷떞 吏移?
1. ?꾨옒 ?쒓났??[?숆탳 怨듭떇 ?덈궡 ?먮즺]瑜?理쒖슦?좎쑝濡?李멸퀬?섏뿬 ?듬???
2. ?먮즺???녿뒗 ?댁슜?대굹 ?꾩＜ 援ъ껜?곸씤 媛쒖씤蹂??곹솴? "?낇븰泥?055-546-2260)濡?臾몄쓽?섏떆硫????뺥솗???덈궡瑜?諛쏆쑝?????덉뒿?덈떎."?쇨퀬 ?덈궡??
3. 留먰닾??'?좊ː媛??덇퀬 ?ㅼ젙???좎깮?????ㅼ쓣 ?좎??섍퀬, ??긽 議대뙎留먯쓣 ?ъ슜??
4. ?듬? ?앹뿉??沅곴툑利앹씠 ?댁냼?섏뿀?붿? 媛蹂띻쾶 臾산굅??異붽? ?꾩????쒖븞??

[?숆탳 怨듭떇 ?덈궡 ?먮즺 (PDF)]
{knowledge_base}
"""

async def get_bot_response(model, system_prompt, user_question):
    try:
        full_prompt = f"{system_prompt}\n\n吏덈Ц: {user_question}\n?듬?:"
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

async def evaluate_response(eval_model, knowledge_base, question, reference, bot_answer):
    prompt = f"""?ㅼ쓬? 吏꾪빐怨좊벑?숆탳 ?낇븰?곷떞 梨쀫큸???듬??낅땲?? 
?쒓났??[?꾩껜 吏??踰좎씠??? [?뺣떟 洹쇨굅(Key Points)]瑜?諛뷀깢?쇰줈 梨쀫큸???듬????꾧꺽?섍쾶 ?됯???二쇱꽭??

[?꾩껜 吏??踰좎씠??
{knowledge_base}

[吏덈Ц]
{question}

[?뺣떟 洹쇨굅 (諛섎뱶???ы븿?섏뼱?????듭떖 ?ъ씤??]
{reference}

[梨쀫큸 ?듬?]
{bot_answer}

[?듭떖 ?됯? ?먯튃 - 留ㅼ슦 以묒슂]
1. **?뺥솗??*: 遊뉗쓽 ?듬? ?댁슜 以?[?꾩껜 吏??踰좎씠??? ?곸땐?섎뒗 ?뺣낫(?좎쭨, ?쒓컙, ?몄썝, ?섏튂 ??媛 **???섎굹?쇰룄 ?덉쑝硫?Accuracy??臾댁“嫄?0??*?낅땲??
2. **?좊（?쒕꽕?댁뀡**: [?꾩껜 吏??踰좎씠?????녿뒗 ?뺣낫瑜??ъ떎??寃껋쿂??吏?대궡???듬???寃쎌슦 0??泥섎━?⑸땲?? 
   - ?? 吏??踰좎씠?ㅼ뿉 ?덈뒗 ?댁슜??諛뷀깢?쇰줈 ???곸꽭?섍쾶 ?ㅻ챸?섎뒗 寃껋? ?덉슜?⑸땲??
3. **?꾩닔 ?뺣낫 ?꾨씫**: [?뺣떟 洹쇨굅]??紐낆떆???듭떖 ?ъ씤?멸? ?꾨씫??寃쎌슦 ?먯닔瑜?媛먯젏?섍굅??0??泥섎━?⑸땲??

[?됯? ??ぉ]
1. Accuracy (0 ?먮뒗 10): 紐⑤뱺 ?뺣낫媛 吏??踰좎씠?ㅼ? ?쇱튂?섍퀬 ?꾩닔 ?뺣낫媛 ?ы븿?섏뿀?붽??
2. Hallucination (Yes/No): 吏??踰좎씠?ㅼ뿉 ?녿뒗 媛吏??뺣낫瑜?吏?대깉?붽??
3. Tone (0-5): 移쒖젅?섍퀬 ?꾨Ц?곸씤 ?좎깮?섏쓽 留먰닾?멸??
4. Reasoning: 0?먯쓣 以 寃쎌슦 ?대뼡 ?뺣낫媛 吏??踰좎씠?ㅼ쓽 ?대뒓 遺遺꾧낵 ?곸땐?섎뒗吏, ?먮뒗 ?대뼡 ?꾩닔 ?뺣낫媛 ?꾨씫?섏뿀?붿? 援ъ껜?곸쑝濡??ㅻ챸?댁쨾.

??湲곗???諛뷀깢?쇰줈 ?꾨옒 JSON ?뺤떇?쇰줈留??묐떟?댁쨾.
{{
  "accuracy": ?먯닔,
  "hallucination": "Yes" ?먮뒗 "No",
  "tone": ?먯닔,
  "reasoning": "?ㅻ챸"
}}
"""
    try:
        response = eval_model.generate_content(prompt)
        # JSON ?뺤젣
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception as e:
        print(f"  - Evaluation Parsing Error: {e}")
        return {"accuracy": 0, "hallucination": "ParseError", "tone": 0, "reasoning": f"Could not parse eval response: {str(e)}"}

async def main():
    print("Loading environment and knowledge...")
    load_dotenv(os.path.join(bot_root, 'api', '.env'))
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in .env file")
        return

    genai.configure(api_key=api_key)
    # 理쒖떊 Pro 紐⑤뜽 ?곸슜 (gemini-3.1-pro-preview)
    MODEL_NAME = 'gemini-3.1-pro-preview'
    bot_model = genai.GenerativeModel(MODEL_NAME) 
    eval_model = genai.GenerativeModel(MODEL_NAME)

    knowledge = load_knowledge()
    system_prompt = get_system_prompt(knowledge)

    questions_path = os.path.join(project_root, 'verify', 'test_questions.json')
    with open(questions_path, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)

    results = []
    print(f"Starting reliability verification (Strict Mode) using {MODEL_NAME} for {len(test_cases)} cases...")

    for i, case in enumerate(test_cases):
        print(f"[{i+1}/{len(test_cases)}] Q{case['id']} ({case['category']}): {case['question']}...")
        bot_answer = await get_bot_response(bot_model, system_prompt, case['question'])
        
        if bot_answer.startswith("Error:"):
            print(f"  - Bot Error: {bot_answer}")
            evaluation = {"accuracy": 0, "hallucination": "BotError", "tone": 0, "reasoning": bot_answer}
        else:
            print(f"  - Bot answered. Evaluating correctness (Strict Mode)...")
            evaluation = await evaluate_response(eval_model, knowledge, case['question'], case['reference'], bot_answer)
        
        print(f"  - Score: {evaluation['accuracy']}, Hallucination: {evaluation['hallucination']}")
        
        results.append({
            "id": case["id"],
            "category": case["category"],
            "question": case["question"],
            "reference": case["reference"],
            "bot_answer": bot_answer,
            "accuracy": evaluation["accuracy"],
            "hallucination": evaluation["hallucination"],
            "tone": evaluation["tone"],
            "reasoning": evaluation["reasoning"]
        })
        # Rate limiting 諛⑹?瑜??꾪빐 1珥??湲?
        await asyncio.sleep(1)

    # 寃곌낵 ???
    output_path = os.path.join(project_root, 'verify', 'verification_results.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 由ы룷???앹꽦
    total_cases = len(results)
    pass_cases = sum(1 for r in results if r['accuracy'] >= 10)
    fail_cases = total_cases - pass_cases
    avg_accuracy = (pass_cases / total_cases) * 100 if total_cases > 0 else 0
    hallucinations = sum(1 for r in results if r['hallucination'] == "Yes")
    
    report = f"""# 吏꾪빐怨??낇븰?곷떞 梨쀫큸 ?좊ː??寃利?由ы룷??(?꾧꺽 寃利?紐⑤뱶)
- 寃利??쇱떆: 2026-04-03
- 珥??뚯뒪??耳?댁뒪: {total_cases}媛?
- 理쒖쥌 ?⑷꺽瑜?(Accuracy 100%): {avg_accuracy:.1f}% ({pass_cases}/{total_cases})
- ?좊（?쒕꽕?댁뀡(?⑺듃 ?ㅻ쪟) 諛쒓껄 嫄댁닔: {hallucinations}嫄?

> [!CAUTION]
> **寃利?湲곗?**: ?ъ슜?먯쓽 ?붿껌???곕씪 '?듭떖 ?뺣낫 以????섎굹?쇰룄 ?由щ㈃ ?ㅻ떟(0??' 泥섎━?섎뒗 媛???꾧꺽??湲곗????곸슜?섏??듬땲??

## ?붿빟
"""
    if fail_cases == 0:
        report += "??紐⑤뱺 ?듭떖 ?뺣낫?????100% ?쇱튂?섎뒗 ?꾨꼍???듬????앹꽦?섍퀬 ?덉뒿?덈떎.\n"
    elif fail_cases <= 3:
        report += f"?좑툘 ?遺遺??뺥솗?섎굹 {fail_cases}嫄댁쓽 ?듭떖 ?⑺듃 ?ㅻ쪟媛 諛쒓껄?섏뿀?듬땲?? ?대떦 ??ぉ??吏??踰좎씠?ㅻ? ?먭??섏꽭??\n"
    else:
        report += f"??{fail_cases}嫄댁쓽 ?ㅼ닔 ?듬??먯꽌 ?⑺듃 ?ㅻ쪟 ?먮뒗 ?좊（?쒕꽕?댁뀡??諛쒖깮?덉뒿?덈떎. 利됯컖?곸씤 ?꾨＼?꾪듃 ?섏젙???꾩슂?⑸땲??\n"

    report += "\n## ?곸꽭 寃곌낵 (遺덊빀寃?耳?댁뒪)\n"
    for r in results:
        if r['accuracy'] < 10:
            report += f"### Q{r['id']} [{r['category']}]\n"
            report += f"- **吏덈Ц**: {r['question']}\n"
            report += f"- **遊??듬?**: {r['bot_answer']}\n"
            report += f"- **?뺣떟 洹쇨굅**: {r['reference']}\n"
            report += f"- **?ㅻ쪟 ?ъ쑀**: {r['reasoning']}\n\n"

    report_path = os.path.join(project_root, 'verify', 'verification_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Verification complete. Results saved to {output_path}")
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    asyncio.run(main())
