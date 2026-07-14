content = """@echo off
echo ===================================================
echo [NotebookLM ?몄쬆 ?ㅽ겕由쏀듃]
echo.
echo ?댁젣 援ш? 釉뚮씪?곗? 李쎌씠 ?대┰?덈떎.
echo ?됱냼 ?ъ슜?섏떆??援ш? 怨꾩젙?쇰줈 濡쒓렇?명빐二쇱꽭??
echo (濡쒓렇?몄씠 ?꾨즺?섎㈃ 李쎌씠 ?ロ옓?덈떎)
echo ===================================================
echo.
nlm login
echo.
echo 濡쒓렇?몄씠 ?꾨즺?섏뿀?듬땲?? 李쎌쓣 ?レ븘二쇱꽭??
pause
"""

with open("NotebookLM_珥덇린濡쒓렇??bat", "w", encoding="cp949") as f:
    f.write(content)
