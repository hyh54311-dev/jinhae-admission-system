import os
import sys
import subprocess
import datetime
import time
import re
import json
import io
import threading
from datetime import datetime, timedelta, timezone


# Windows 肄섏넄?먯꽌 UTF-8(?대え吏 ?ы븿) 異쒕젰 吏??if sys.platform == 'win32' and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def log_message(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [NotebookLM] {message}")

def send_telegram_notification(text):
    """
    怨듭슜 ?붾젅洹몃옩 ?뚮┝ ?꾩넚 ?⑥닔
    """
    token = "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY"
    chat_id = "8518409134"
    telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        import urllib.request
        import urllib.parse
        import ssl
        
        data = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode('utf-8')
        req = urllib.request.Request(telegram_url, data=data)
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        urllib.request.urlopen(req, context=ctx)
        return True
    except Exception as e:
        log_message(f"?좑툘 ?붾젅洹몃옩 ?뚮┝ ?꾩넚 ?ㅽ뙣: {e}")
        return False

def verify_audio_and_notify(notebook_id, file_path, tg_prefix, instructions=None):
    """
    15遺??ㅼ뿉 ?ㅻ뵒???앹꽦???꾨즺?섏뿀?붿? ?뺤씤?섍퀬 ?뚮┝??蹂대깄?덈떎.
    ?ㅽ뙣 ??1???ъ떆?꾪빀?덈떎.
    """
    wait_time = 900 # 15遺?    log_message(f"??{wait_time//60}遺???理쒖쥌 ?앹꽦 寃곌낵瑜??뺤씤?⑸땲?? 諛깃렇?쇱슫??媛먯떆 ?쒖옉...")
    time.sleep(wait_time)
    
    log_message(f"?뵇 [{notebook_id}] ?ㅻ뵒???앹꽦 ?곹깭 ?뺤씤 以?..")
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf8"
    env["PYTHONUTF8"] = "1"
    
    try:
        # artifact list瑜?JSON?쇰줈 媛?몄????뺤씤
        result = subprocess.run([
            sys.executable, "run_nlm_patched.py", "list", "artifacts", notebook_id, "--json"
        ], capture_output=True, text=True, encoding='utf-8', env=env)
        
        data = json.loads(result.stdout.strip())
        artifacts = data.get("artifacts", [])
        audio_found = False
        
        # Audio ??낆씠硫?status媛 completed??寃?寃??        for art in artifacts:
            # type_id媛 audio?대ŉ status媛 completed??寃?寃??            if art.get("type_id") == "audio" and art.get("status") == "completed":
                audio_found = True
                break
        
        if audio_found:
            msg = f"??{tg_prefix}\n?ㅻ뵒??釉뚮━???앹꽦??理쒖쥌 ?꾨즺?섏뿀?듬땲??\n\n臾몄꽌紐? {os.path.basename(file_path)}\n\n?뺤긽?곸쑝濡??앹꽦???ㅻ뵒?ㅻ? ?뺤씤?덉뒿?덈떎. 吏湲?諛붾줈 NotebookLM?먯꽌 ?ㅼ뼱蹂댁떎 ???덉뒿?덈떎."
            send_telegram_notification(msg)
            log_message("???ㅻ뵒???앹꽦 ?깃났 ?뺤씤 諛??뚮┝ ?꾩넚 ?꾨즺.")
        else:
            log_message("?좑툘 15遺꾩씠 吏?ъ쑝???ㅻ뵒???앹꽦???뺤씤?섏? 紐삵뻽?듬땲?? ?먭? 移섏쑀(?ъ떆??瑜??쒖옉?⑸땲??")
            msg = f"?슚 {tg_prefix}\n?ㅻ뵒???앹꽦??吏?곕릺???먭? 移섏쑀(Self-healing)瑜??쒖옉?⑸땲??\n\n?쒖뒪?쒖씠 ?먮룞?쇰줈 ?앹꽦???ㅼ떆 ?붿껌?섎ŉ, ??15遺???理쒖쥌 ?곹깭瑜???踰???蹂닿퀬?섍쿋?듬땲??"
            send_telegram_notification(msg)
            
            # ?ъ떆??(is_retry=True濡?臾댄븳猷⑦봽 諛⑹?)
            submit_to_notebooklm(file_path, instructions=instructions, tg_prefix=f"{tg_prefix} [?먭?移섏쑀]", is_retry=True)
            
    except Exception as e:
        log_message(f"???곹깭 ?뺤씤 以??ㅻ쪟 諛쒖깮: {e}")

def submit_to_notebooklm(file_path, title=None, instructions=None, tg_prefix="[NotebookLM ?먮룞??", is_retry=False):
    """
    ?앹꽦??留덊겕?ㅼ슫 ?뚯씪??NotebookLM ?꾩슜 ?명듃遺곸뿉 ?낅줈?쒗븯怨??ㅻ뵒??釉뚮━?묒쓣 ?몃━嫄고빀?덈떎.
    """
    now = datetime.now()
    today_str = now.strftime("%m??%d??)
    # ?쒕ぉ??二쇱뼱吏吏 ?딆쑝硫?湲곕낯 寃쎌젣 ?댁뒪 ?쒕ぉ ?ъ슜
    notebook_title = title if title else f"?닿렐湲?20遺?寃쎌젣 ?댁뒪({today_str})"
    
    # ?ㅻ뵒???앹꽦 吏移?(Focus) - ?몄옄媛 ?놁쑝硫??좎깮???곸쐞 留덉뒪???꾨＼?꾪듃 ?ъ슜
    DEFAULT_AUDIO_INSTRUCTIONS = (
        "?뱀떊?ㅼ? 寃쎌젣 ?꾨Ц ?잛틦?ㅽ듃??踰좏뀒??吏꾪뻾?먮뱾?낅땲?? ?쒓? ?낅줈?쒗븳 理쒖떊 寃쎌젣 ?댁뒪 臾몄꽌?ㅼ쓣 諛뷀깢?쇰줈, "
        "泥?랬?먮뱾?먭쾶 源딆씠 ?덈뒗 ?듭같???쒓났?섎뒗 ?ъ링 ?ㅻ뵒??由щ럭瑜??앹꽦??二쇱꽭?? ??붾뒗 ?ㅼ쓬 吏移⑥쓣 ?꾧꺽???곕씪???⑸땲??\n\n"
        "遺꾨웾 諛??щ룄: > ?쒓컙???쒖빟???먯? 留먭퀬 ?띿뒪?몄뿉 ?쒖떆???댁슜??異⑸텇?? 異⑹떎??紐⑤몢 諛섏쁺?섏뿬 ??붾? ?섎늻??二쇱꽭?? "
        "?섎컯 寃됲븼湲곗떇??吏㏃? ?붿빟? 吏?묓븯怨? 媛??댁뒋?????異⑸텇???쒓컙???좎븷?섏뿬 ?곸꽭?섍퀬 源딆씠 ?덈뒗 ?잛틦?ㅽ듃瑜?留뚮뱾?댁빞 ?⑸땲??\n\n"
        "理쒖떊 ?댁뒋 ?좊퀎 諛?肄붿뒪??遺꾩꽍 (?꾩닔 諛섏쁺): > ?쒓났???뚯뒪 以?媛???뚭툒?μ씠 ??寃쎌젣 ?댁뒪?ㅼ쓣 硫붿씤 二쇱젣濡??ㅻ（??二쇱떆怨? "
        "?뱁엳 臾몄꽌 ?댁슜 以?'?곕━?섎씪 肄붿뒪???곸쐞 湲곗뾽 以??섎굹瑜??뺥빐??遺꾩꽍'???뚰듃媛 ?덉뒿?덈떎. "
        "??肄붿뒪??湲곗뾽 遺꾩꽍 ?댁슜? ?덈?濡??꾨씫?섏? 留먭퀬 諛섎뱶???ㅻ뵒??由щ럭???ы븿?섏뿬 ?щ룄 ?덇쾶 ?ㅻ쨪 二쇱꽭??\n\n"
        "誘몃옒 寃쎌젣 ?곹솴 ?꾨쭩 (媛??以묒슂): > ?⑥닚??湲곗궗 ?댁슜???꾨떖?섎뒗 寃껋쓣 ?섏뼱, **\"洹몃옒???욎쑝濡??대뼸寃???寃껋씤媛?\"**??吏묒쨷??二쇱꽭?? "
        "???댁뒪?ㅼ씠 ?ν썑 湲덈━, ?명뵆?덉씠?? 二쇱떇/遺?숈궛 ?쒖옣, 洹몃━怨?嫄곗떆 寃쎌젣 ?꾨컲???대뼡 蹂?붾? 珥됰컻?좎? ??吏꾪뻾?먭? ?ㅺ컖?꾨줈 遺꾩꽍?섍퀬 ?덉륫??二쇱꽭??\n\n"
        "?ъ슫 鍮꾩쑀? ?몄궗?댄듃: > 蹂듭옟??寃쎌젣 吏?쒕굹 ?꾨Ц ?⑹뼱媛 ?깆옣?섎㈃ 泥?랬?먭? 吏곴??곸쑝濡??댄빐?????덈룄濡??쇱긽?곸씤 鍮꾩쑀瑜??ㅼ뼱 ?ㅻ챸??二쇱꽭?? "
        "留덉?留됱뿉???쇰컲 ?以묒씠???ъ옄?먮뱾???대뼡 ?ㅽ깲?ㅻ? 痍⑦빐???좎? ?ㅼ쭏?곸씤 ?쒖궗?먯쓣 ?꾩텧?섎ŉ 留덈Т由ы빐 二쇱꽭??\n\n"
        "?ㅼ븻留ㅻ꼫: > 吏꾩??섍퀬 ?꾨Ц?곸씠硫댁꽌?? ??吏꾪뻾?먭? ?쒕줈 吏덈Ц???섏?怨??섍껄??蹂댁셿??二쇰뒗 ?먯뿰?ㅻ읇怨??고궎?移닿? ?댁븘?덈뒗 ????뺤떇???좎???二쇱꽭??\n\n"
        "紐⑤뱺 ??붾뒗 ?쒓뎅?대줈 吏꾪뻾?섏떗?쒖삤."
    )
    
    # ?덈룄???몄퐫??異⑸룎 諛⑹????섍꼍?ㅼ젙 異붽?
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf8"
    env["PYTHONUTF8"] = "1"
    
    # 1. ?덈줈???명듃遺??앹꽦
    log_message(f"?덈줈???명듃遺??앹꽦 ?붿껌 以? {notebook_title}")
    notebook_id = None
    try:
        # CLI 紐낅졊?? python run_nlm_patched.py notebook create "<title>"
        create_result = subprocess.run([sys.executable, "run_nlm_patched.py", "notebook", "create", notebook_title], check=True, capture_output=True, text=True, encoding='utf-8', env=env)
        log_message("???명듃遺??앹꽦???꾨즺?섏뿀?듬땲??")
        
        # 異쒕젰?먯꽌 ID 異붿텧 (JSON ?뺤떇?닿굅???띿뒪???뺤떇?????덉쓬)
        match = re.search(r"ID:\s+([a-f0-9\-]{36})", create_result.stdout, re.IGNORECASE)
        if match:
            notebook_id = match.group(1)
            log_message(f"???앹꽦???명듃遺?ID 異붿텧 ?꾨즺: {notebook_id}")
        else:
            log_message("?좑툘 ?명듃遺?ID瑜?異붿텧?섏? 紐삵뻽?듬땲?? ?쒕ぉ?쇰줈 ?쒕룄?⑸땲??")
            notebook_id = notebook_title
    except subprocess.CalledProcessError as e:
        log_message(f"???명듃遺??앹꽦 ?ㅽ뙣: {e.stderr}")
        return False
        
    time.sleep(2) # ?쒕쾭 諛섏쁺 ?湲?    
    # 2. ?뚯뒪 ?뚯씪 ?낅줈??    log_message(f"?뚯씪 ?낅줈??以? {os.path.basename(file_path)}")
    try:
        # CLI 紐낅졊?? python run_nlm_patched.py source add "<notebook_id>" --file "<file_path>"
        subprocess.run([sys.executable, "run_nlm_patched.py", "source", "add", notebook_id, "--file", file_path], check=True, capture_output=True, text=True, encoding='utf-8', env=env)
        log_message("??釉뚮━??臾몄꽌媛 ?깃났?곸쑝濡?NotebookLM???뚯뒪濡?異붽??섏뿀?듬땲??")
    except subprocess.CalledProcessError as e:
        log_message(f"???뚯뒪 異붽? ?ㅽ뙣: {e.stderr if e.stderr else e.stdout}")
        return False
        
    time.sleep(2)
    
    # 3. 梨꾪똿李????[留욎땄 ?ㅼ젙]???듯븳 ?ㅻ뵒???몃━嫄?    log_message(f"?숋툘 [留욎땄 ?ㅼ젙] 吏移⑥쑝濡??ㅻ뵒???앹꽦???몃━嫄고빀?덈떎.")
    try:
        final_instructions = instructions if instructions else DEFAULT_AUDIO_INSTRUCTIONS
        # CLI 紐낅졊?? python run_nlm_patched.py audio create "<notebook_id>" --focus "<prompt>" --confirm
        result = subprocess.run([
            sys.executable, "run_nlm_patched.py", "audio", "create", notebook_id, "--focus", final_instructions, "--confirm"
        ], check=True, capture_output=True, text=True, encoding='utf-8', env=env)
        
        log_message("??[留욎땄 ?ㅼ젙] 湲곕컲 ?ㅻ뵒???앹꽦 ?붿껌???꾨즺?섏뿀?듬땲??")

    except subprocess.CalledProcessError as e:
        log_message(f"???ㅻ뵒???앹꽦 ?붿껌 ?ㅽ뙣: {e.stderr if e.stderr else e.stdout}")
        return False
        
    # 4. ?붾젅洹몃옩 ?뚮┝ ?꾩넚 (1李??④퀎 ?깃났 蹂닿퀬)
    log_message("?벑 ?붾젅洹몃옩?쇰줈 1李??붿껌 ?깃났 ?뚮┝???꾩넚?⑸땲??..")
    msg = f"??{tg_prefix}\n[留욎땄 ?ㅼ젙?? ?ㅻ뵒???잛틦?ㅽ듃 ?앹꽦???붿껌?섏뿀?듬땲??\n\n臾몄꽌紐? {os.path.basename(file_path)}\n\n(??15遺???理쒖쥌 ?꾨즺 ?щ?瑜??ㅼ떆 ?뚮젮?쒕┰?덈떎.)"
    send_telegram_notification(msg)

    # 5. 諛깃렇?쇱슫??寃利??ㅻ젅???쒖옉 (?ъ떆??猷⑦봽媛 ?꾨땺 ?뚮쭔 ?쒖옉)
    if not is_retry:
        monitor_thread = threading.Thread(
            target=verify_audio_and_notify, 
            args=(notebook_id, file_path, tg_prefix, instructions),
            daemon=False # 硫붿씤 ?ㅽ겕由쏀듃媛 ?앸굹??媛먯떆瑜??꾪빐 ?좎?
        )
        monitor_thread.start()
        log_message("??諛깃렇?쇱슫??紐⑤땲?곕쭅 ?ㅻ젅?쒓? ?쒖옉?섏뿀?듬땲??")
    
    return True

def cleanup_old_notebooks(days_ago=7):
    """
    理쒓렐 ?낅뜲?댄듃??吏 ?쇱젙 湲곌컙(湲곕낯 7????吏??援ы삎 ?명듃遺곷뱾??李얠븘 ??젣?⑸땲??
    """
    log_message(f"?㏏ {days_ago}???댁긽 ??援ы삎 ?명듃遺??뺣━ ?묒뾽???쒖옉?⑸땲??..")
    
    # ?덈룄???몄퐫???ㅼ젙
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf8"
    env["PYTHONUTF8"] = "1"
    
    # 1. ?명듃遺?紐⑸줉 媛?몄삤湲?    try:
        result = subprocess.run([
            sys.executable, "run_nlm_patched.py", "notebook", "list", "--json"
        ], capture_output=True, text=True, encoding='utf-8', env=env)
        
        # ?몄뀡 留뚮즺 吏꾨떒 濡쒖쭅 異붽?
        if result.returncode != 0:
            error_msg = (
                f"?슚 [NotebookLM ?쒕퉬???μ븷]\n\n"
                f"NotebookLM ?붿쭊 ?ㅽ뻾 以??ㅻ쪟媛 諛쒖깮?덉뒿?덈떎. (Exit Code: {result.returncode})\n"
                f"?몄뀡??留뚮즺?섏뿀??媛?μ꽦???믪뒿?덈떎.\n\n"
                f"?낅Т??而댄벂?곗뿉??'NotebookLM_珥덇린濡쒓렇??bat'???ㅽ뻾??二쇱꽭??"
            )
            # CLI?먯꽌 諛쒖깮??stderr媛 ?덈떎硫?異붽?
            if result.stderr:
                log_message(f"CLI Error Output: {result.stderr}")
            
            send_telegram_notification(error_msg)
            log_message("???붿쭊 ?ㅻ쪟 媛먯?: ?붾젅洹몃옩?쇰줈 湲닿툒 ?뚮┝???꾩넚?덉뒿?덈떎.")
            return False

        stdout_clean = result.stdout.strip()
        if not stdout_clean:
            log_message("??NotebookLM CLI媛 鍮?寃곌낵瑜?諛섑솚?덉뒿?덈떎.")
            return False

        try:
            notebooks = json.loads(stdout_clean)
            log_message(f"珥?{len(notebooks)}媛쒖쓽 ?명듃遺곸씠 諛쒓껄?섏뿀?듬땲??")
        except json.JSONDecodeError as e:
            log_message(f"???명듃遺?紐⑸줉 遺꾩꽍 ?ㅽ뙣 (JSON ?뚯떛 ?ㅻ쪟): {e}")
            log_message(f"諛쏆? ?곗씠???쇰?: {stdout_clean[:200]}...")
            
            if "Authentication" in stdout_clean or "login" in stdout_clean:
                msg = "?슚 [NotebookLM ?몄뀡 留뚮즺]\n?몄쬆 ?뺣낫媛 留뚮즺?섏뿀?듬땲?? ?ㅼ떆 濡쒓렇?명빐 二쇱꽭??"
                send_telegram_notification(msg)
            return False
    except Exception as e:
        log_message(f"???명듃遺?紐⑸줉 遺꾩꽍 以??덉쇅 諛쒖깮: {e}")
        return False

    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=days_ago)
    delete_count = 0

    # 2. ?좎쭨 鍮꾧탳 諛???젣
    for nb in notebooks:
        try:
            nb_id = nb.get("id")
            nb_title = nb.get("title", "")
            updated_at_str = nb.get("updated_at")
            
            if not updated_at_str:
                continue
                
            # 寃쎌젣 ?댁뒪 愿???쒕ぉ?몄? ?뺤씤 (寃쎌젣, ?댁뒪, Briefing, ?잛틦?ㅽ듃 ?ы븿 ?щ?)
            is_economic_news = any(keyword in nb_title for keyword in ["寃쎌젣", "?댁뒪", "Briefing", "?잛틦?ㅽ듃"])
            
            if not is_economic_news:
                continue

            # ISO 8601 ?щ㎎ ?뚯떛 (Z??+00:00?쇰줈 移섑솚)
            updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
            
            if updated_at < cutoff_date:
                log_message(f"?뿊截??ㅻ옒???명듃遺???젣 以? [{nb_title}] (理쒖쥌 ?낅뜲?댄듃: {updated_at_str})")
                subprocess.run([
                    sys.executable, "run_nlm_patched.py", "delete", nb_id, "--confirm"
                ], check=True, capture_output=True, text=True, encoding='utf-8', env=env)
                delete_count += 1
        except Exception as e:
            log_message(f"?좑툘 ?명듃遺???젣 以??ㅻ쪟 諛쒖깮 ({nb.get('title', 'Unknown')}): {e}")

    log_message(f"???뺣━ ?꾨즺: 珥?{delete_count}媛쒖쓽 ?명듃遺곸씠 ??젣?섏뿀?듬땲??")
    return True

def delete_notebooks_by_keywords(keywords, days_ago=1):
    """
    ?뱀젙 ?ㅼ썙?쒓? ?ы븿??理쒓렐 ?명듃遺곷뱾??李얠븘 ??젣?⑸땲?? (?ㅻ뒛???섎せ??釉뚮━????젣??
    """
    if not keywords: return False
    log_message(f"?㏏ ?ㅼ썙??{keywords} 湲곕컲 ?명듃遺???젣 ?묒뾽???쒖옉?⑸땲??..")
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf8"
    env["PYTHONUTF8"] = "1"
    
    try:
        result = subprocess.run([
            sys.executable, "run_nlm_patched.py", "notebook", "list", "--json"
        ], capture_output=True, text=True, encoding='utf-8', env=env)
        notebooks = json.loads(result.stdout.strip())
    except Exception as e:
        log_message(f"???명듃遺?紐⑸줉??媛?몄삤?????ㅽ뙣?덉뒿?덈떎: {e}")
        return False

    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=days_ago)
    delete_count = 0

    for nb in notebooks:
        try:
            nb_id = nb.get("id")
            nb_title = nb.get("title", "")
            if any(kw in nb_title for kw in keywords):
                log_message(f"?뿊截??ㅼ썙???쇱튂 ?명듃遺???젣 以? [{nb_title}]")
                subprocess.run([
                    sys.executable, "run_nlm_patched.py", "delete", nb_id, "--confirm"
                ], check=True, capture_output=True, text=True, encoding='utf-8', env=env)
                delete_count += 1
        except Exception as e:
                log_message(f"?좑툘 ?명듃遺???젣 以??ㅻ쪟 諛쒖깮 ({nb.get('title', 'Unknown')}): {e}")

    log_message(f"????젣 ?꾨즺: 珥?{delete_count}媛쒖쓽 ?명듃遺곸씠 ??젣?섏뿀?듬땲??")
    return True

if __name__ == "__main__":
    # 吏곸젒 ?ㅽ뻾 ???몄옄???곕씪 ?숈옉
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        cleanup_old_notebooks(days)
    elif len(sys.argv) > 1:
        # ?뚯씪 寃쎈줈媛 ?몄옄濡??ㅼ뼱??寃쎌슦 湲곗〈泥섎읆 ?낅줈??吏꾪뻾
        submit_to_notebooklm(sys.argv[1])
