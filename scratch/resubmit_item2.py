import os
import sys
import time
import io
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def main():
    url = "https://script.google.com/macros/s/AKfycbx7svjAJ03_YAbvn6HD7etnqfSXmDOjJ7D2erUNnDpAi6PpGbfdgQhdY09En7wdcyy9/exec"
    s = {
        "ban": 1, "num": 2, "name": "이유음",
        "topic": "교체 (비음화 & 유음화)",
        "initialHypothesis": "받침 ㄱ, ㄷ, ㅂ이 비음 ㄴ, ㅁ을 만나면 무조건 비음 ㅇ, ㄴ, ㅁ으로 변하고, ㄴ과 ㄹ이 만나면 무조건 ㄹㄹ로 변한다.",
        "aiHistory": "학생: 국물[궁물]은 비음화가 맞는데, 생산량[생산냥]은 왜 유음화가 아니라 ㄴ으로 발음되나요?\nAI튜터: 2음절 단어와 3음절 한자어(생산+량)의 구조적 차이를 파악해 볼까요? 한자어 결합에서는 비음화/ㄴ첨가 현상이 선행할 수 있습니다.",
        "finalHypothesis": "받침 ㄱ,ㄷ,ㅂ 뒤에 비음 ㄴ,ㅁ이 오면 각 자음의 위치를 유지한 채 비음(ㅇ,ㄴ,ㅁ)으로 교체된다. ㄴ과 ㄹ이 만나면 유음화(ㄹㄹ)가 일어나는 것이 원칙이나, 독립된 한자어 단어가 결합한 복합어의 경우 [생산냥]처럼 비음화가 적용되는 예외가 존재한다."
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        time.sleep(8)

        target_frame = None
        for f in page.frames:
            try:
                if f.evaluate("typeof google !== 'undefined' && google.script && google.script.run"):
                    target_frame = f
                    break
            except Exception:
                pass

        if target_frame:
            payload = {
                "ban": s["ban"],
                "num": s["num"],
                "name": s["name"],
                "topic": s["topic"],
                "initialHypothesis": s["initialHypothesis"],
                "aiHistory": s["aiHistory"],
                "finalHypothesis": s["finalHypothesis"]
            }

            eval_js = f"""
            new Promise((resolve, reject) => {{
                google.script.run
                    .withSuccessHandler((res) => resolve(res))
                    .withFailureHandler((err) => reject(err))
                    .submitGrammarAnswer({payload});
            }})
            """
            try:
                res = target_frame.evaluate(eval_js)
                print(f"✅ 재제출 성공: {res.get('message', res)}")
            except Exception as e:
                print(f"❌ 재제출 실패: {e}")

        browser.close()

if __name__ == '__main__':
    main()
