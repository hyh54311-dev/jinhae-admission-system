import io
import sys
import os
import telegram_assistant
import bot_stress_harness
from contextlib import redirect_stdout

def run_at_night():
    print("?뙔 ?쇨컙 ?먮룞 臾닿껐??寃利??쒖뒪??媛??..")
    
    # 1. ?섎꽕???ㅽ뻾 諛?寃곌낵 罹≪쿂
    f = io.StringIO()
    with redirect_stdout(f):
        bot_stress_harness.run_harness()
    output = f.getvalue()
    
    # 2. 寃곌낵 遺꾩꽍 (?⑷꺽瑜?異붿텧)
    pass_count_match = [line for line in output.split('\n') if '理쒖쥌 ?⑷꺽瑜? in line]
    summary = pass_count_match[0] if pass_count_match else "寃利??꾨즺 (?⑷꺽瑜??뺤씤 遺덇?)"
    
    # 3. ?붾젅洹몃옩 蹂닿퀬???묒꽦
    report_text = (
        "?뱤 [Antigravity ?쇨컙 臾닿껐??寃利?由ы룷??\n"
        "--------------------------------------\n"
        "?좎깮?? ?붿껌?섏떊 ?ㅽ썑 11???뺣? 寃利앹쓣 留덉낀?듬땲??\n\n"
        f"??{summary}\n\n"
        "?곸꽭 寃곌낵???쒕쾭 濡쒓렇??湲곕줉?섏뿀?듬땲??\n"
        "?댁젣 紐⑤뱺 ?쒖뒪?쒖씠 臾닿껐???곹깭?꾩쓣 ?뺤씤?덉뒿?덈떎.\n"
        "?됱븞??諛??섏떗?쒖삤!"
    )
    
    # 4. ?붾젅洹몃옩 諛쒖넚 以묐떒 (?ъ슜???붿껌)
    # target_chat_id = "5043815340" 
    # telegram_assistant.send_telegram_message(target_chat_id, report_text)
    
    log_msg = f"???쇨컙 寃利??꾨즺. (?⑷꺽瑜? {summary}) - ?붾젅洹몃옩 蹂닿퀬???꾩넚 ?앸왂??"
    print(log_msg)

if __name__ == "__main__":
    run_at_night()
