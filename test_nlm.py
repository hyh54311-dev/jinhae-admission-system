import traceback
import httpx

# 1. Httpx Client??verify ?듭뀡??臾댁“嫄?False濡?媛뺤젣?섎뒗 ?⑥튂
# (寃쎌긽?⑤룄援먯쑁泥??숆탳 ?ㅽ듃?뚰겕???꾨줉???몄쬆??臾몄젣 ?고쉶)
original_client_init = httpx.Client.__init__
def new_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    original_client_init(self, *args, **kwargs)
httpx.Client.__init__ = new_client_init

original_async_client_init = httpx.AsyncClient.__init__
def new_async_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    original_async_client_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = new_async_client_init

import sys
from notebooklm.notebooklm_cli import cli as cli_app

if __name__ == "__main__":
    print("SSL ?고쉶 紐⑤뱶濡?nlm ?ㅽ뻾 ?뚯뒪??以?..")
    sys.argv = ["nlm", "notebook", "list"]
    try:
        cli_app()
    except Exception as e:
        print("?먮윭 諛쒖깮:")
        traceback.print_exc()
