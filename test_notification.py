import os
import sys
import subprocess
import io

# Windows 肄섏넄?먯꽌 UTF-8(?대え吏 ?ы븿) 異쒕젰 吏??if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def test_popup():
    print("--- [?뚮┝李??뚯뒪???쒖옉] ---")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    popup_script = os.path.join(base_dir, "notify_popup_perfect.py")
    
    if not os.path.exists(popup_script):
        print(f"???ㅻ쪟: '{popup_script}' ?뚯씪??李얠쓣 ???놁뒿?덈떎.")
        return

    print(f"???ㅽ뻾 ?뚯씪 ?뺤씤: {popup_script}")
    print("?뵒 ?좎떆 ??以묒븰???뚮┝李쎌씠 ?섑??⑸땲?? 湲??源⑥쭚 ?щ?瑜??뺤씤??二쇱꽭??")
    
    try:
        subprocess.Popen([sys.executable, popup_script])
        print("?? ?뚮┝李??몄텧 ?깃났! 李쎌씠 ?⑤㈃ 臾멸뎄瑜??뺤씤?섍퀬 '?뺤씤'???뚮윭二쇱꽭??")
    except Exception as e:
        print(f"???ㅽ뻾 以??ㅻ쪟 諛쒖깮: {e}")

if __name__ == "__main__":
    test_popup()
