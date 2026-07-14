import sys
import httpx
import traceback

# SSL ?⑥튂
original_client_init = httpx.Client.__init__
def new_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    original_client_init(self, *args, **kwargs)
httpx.Client.__init__ = new_client_init

from notebooklm_tools.cli.utils import get_client
from notebooklm_tools.services.sources import add_source

try:
    with get_client(None) as client:
        result = add_source(
            client,
            "a98f51c3-d8fa-4bca-bf37-3a587a516630",
            "file",
            file_path=r"d:\OneDrive - 寃쎌긽?⑤룄援먯쑁泥?諛뷀깢 ?붾㈃\吏꾪빐怨좊벑?숆탳\2026?숇뀈??antigravity_folder\寃쎌젣?댁뒪 TXT\2026-03-30_Macro_Briefing.md",
            wait=True
        )
        print("Success!", result)
except Exception as e:
    print("----- ?곸꽭 ?먮윭 濡쒓렇 -----")
    traceback.print_exc()
    if hasattr(e, 'response'):
        print("\n?묐떟 肄붾뱶:", e.response.status_code)
        print("?묐떟 ?댁슜:", e.response.text)
