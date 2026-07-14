import os
import json
import traceback
import httpx
import sys
import io
import re
import urllib.parse

# 1. ?덈룄??肄섏넄 ?쒓? ?몄퐫???먮윭(cp949) 諛⑹???媛뺤젣 UTF-8 紐⑤뱶
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 2. 理쒖떊 ?몄뀡 ?뺣낫 諛??꾩옣 吏臾?Sniffed Data) 濡쒕뱶
SNIFF_PATH = os.path.join(os.environ["USERPROFILE"], ".notebooklm-mcp-cli", "profiles", "default", "sniff.json")
AUTH_PATH = os.path.join(os.environ["USERPROFILE"], ".notebooklm-mcp-cli", "profiles", "default", "auth.json")

SNIFFED_HEADERS = {}
SNIFFED_DATA = {}
if os.path.exists(SNIFF_PATH):
    try:
        with open(SNIFF_PATH, "r", encoding="utf-8") as f:
            SNIFFED_DATA = json.load(f)
            SNIFFED_HEADERS = SNIFFED_DATA.get("headers", {})
    except: pass

SESSION_DATA = {}
if os.path.exists(AUTH_PATH):
    try:
        with open(AUTH_PATH, "r", encoding="utf-8") as f:
            SESSION_DATA = json.load(f)
    except: pass

# 3. Httpx Client ?⑥튂 (蹂댁븞 ?ㅻ뜑 ?꾨꼍 ?꾩옣)
original_client_init = httpx.Client.__init__
def new_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    headers = kwargs.get('headers', {})
    
    # 媛濡쒖콌 紐⑤뱺 蹂댁븞 ?ㅻ뜑(sec-ch-ua ?? 二쇱엯
    for key, value in SNIFFED_HEADERS.items():
        if key.lower() not in ["content-length", "content-type", "host"]:
            headers[key] = value
            
    kwargs['headers'] = headers
    original_client_init(self, *args, **kwargs)
httpx.Client.__init__ = new_client_init

# 4. NotebookLM CLI ??濡쒕뱶 諛??듭떖 ?대옒???⑥튂
try:
    from notebooklm_tools.cli.main import app as cli_app
    from notebooklm_tools.core.base import BaseClient
    
    # [Monkey Patch] ?쇱씠釉뚮윭由??대????섎뱶肄붾뵫???섏씠吏 ?ㅻ뜑 媛뺤젣 蹂寃?    for key, value in SNIFFED_HEADERS.items():
        BaseClient._PAGE_FETCH_HEADERS[key] = value
    
    # [Monkey Patch] URL ?앹꽦 ???몄뀡 ID? 鍮뚮뱶 ?쇰꺼??媛뺤젣濡?二쇱엯
    original_build_url = BaseClient._build_url
    def patched_build_url(self, rpc_id, source_path="/"):
        url = original_build_url(self, rpc_id, source_path)
        
        # 罹≪쿂??理쒖떊 ?뺣낫媛 ?덈떎硫?媛뺤젣 ?곸슜
        forced_sid = SESSION_DATA.get("session_id")
        forced_bl = SESSION_DATA.get("build_label")
        
        if forced_sid or forced_bl:
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            if forced_sid: qs["f.sid"] = [forced_sid]
            if forced_bl: qs["bl"] = [forced_bl]
            # ?쒓뎅????묒쓣 ?꾪빐 hl=ko 媛뺤젣
            qs["hl"] = ["ko"]
            new_query = urllib.parse.urlencode(qs, doseq=True)
            url = parsed._replace(query=new_query).geturl()
        return url
    
    BaseClient._build_url = patched_build_url

    # [Monkey Patch] 珥덇린??諛??좏겙 媛뺤젣 二쇱엯
    original_init = BaseClient.__init__
    def patched_init(self, cookies, csrf_token="", session_id="", build_label=""):
        c_token = csrf_token or SESSION_DATA.get("csrf_token", "")
        # 留뚯빟 ?ㅻ땲???곗씠?곗뿉 理쒖떊 at ?좏겙???덈떎硫?洹멸쾬???곗꽑 ?ъ슜
        if "post_data" in SNIFFED_DATA:
            at_match = re.search(r'at=([^&]+)', SNIFFED_DATA["post_data"])
            if at_match:
                c_token = urllib.parse.unquote(at_match.group(1))
        
        s_id = session_id or SESSION_DATA.get("session_id", "")
        b_label = build_label or SESSION_DATA.get("build_label", "")
        original_init(self, cookies, c_token, s_id, b_label)
    
    BaseClient.__init__ = patched_init

except ImportError:
    try:
        from notebooklm.notebooklm_cli import cli as cli_app
    except ImportError:
        print("??NotebookLM CLI ?⑦궎吏瑜?李얠쓣 ???놁뒿?덈떎.")
        sys.exit(1)

# 5. ?ㅽ뻾
if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.argv[0] = "nlm"
    else:
        sys.argv = ["nlm", "notebook", "list"]
        
    try:
        cli_app()
    except Exception as e:
        print("\n[Antigravity] 理쒖쥌 ?⑥튂 紐⑤뱶濡??ㅽ뻾 以??ㅻ쪟 諛쒖깮:")
        traceback.print_exc()
        sys.exit(1)
