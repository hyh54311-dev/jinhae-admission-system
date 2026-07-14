import os
import sys
import subprocess
import json
import time

def print_banner():
    print("=" * 60)
    print("      [?숆탳 PC ?먮룞???섍꼍 ?먭? ?꾧뎄 / Check & Repair]      ")
    print("=" * 60)
    print(f"?꾩옱 ?쒓컙: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"?묒뾽 ?대뜑: {os.getcwd()}")
    print("-" * 60)

def run_command(cmd_list):
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, encoding='utf-8')
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python():
    print("[1] ?뚯씠???섍꼍 ?뺤씤 以?..", end=" ", flush=True)
    version = sys.version.split()[0]
    if sys.version_info >= (3, 10):
        print(f"??OK (v{version})")
        return True
    else:
        print(f"?좑툘 寃쎄퀬 (v{version} - 3.10 ?댁긽 沅뚯옣)")
        return False

def check_libraries():
    print("[2] ?꾩닔 ?쇱씠釉뚮윭由?notebooklm-py) ?뺤씤 以?..", end=" ", flush=True)
    success, stdout, stderr = run_command([sys.executable, "-m", "pip", "show", "notebooklm-py"])
    if success:
        version = "Unknown"
        for line in stdout.splitlines():
            if line.startswith("Version:"):
                version = line.split(":")[1].strip()
        print(f"??OK (v{version})")
        return True
    else:
        print("???쇱씠釉뚮윭由??꾨씫. ?ㅼ튂瑜??쒕룄?⑸땲??..")
        install_success, _, _ = run_command([sys.executable, "-m", "pip", "install", "--upgrade", "notebooklm-py", "httpx", "rich"])
        if install_success:
            print("   -> ???ㅼ튂 ?꾨즺!")
            return True
        else:
            print("   -> ???ㅼ튂 ?ㅽ뙣. ?명꽣???곌껐???뺤씤?섏꽭??")
            return False

def check_login():
    print("[3] NotebookLM 濡쒓렇???곹깭 ?뺤씤 以?..", end=" ", flush=True)
    # run_nlm_patched.py瑜??듯빐 SSL ?고쉶?섎ŉ 泥댄겕
    success, stdout, stderr = run_command([sys.executable, "run_nlm_patched.py", "list"])
    
    if success and "Not logged in" not in stdout and "Not logged in" not in stderr:
        print("??OK (濡쒓렇?몃맖)")
        return True
    else:
        print("??濡쒓렇???꾩슂")
        print("\n[!] 議곗튂 諛⑸쾿:")
        print("    ?대뜑 ?댁쓽 'NotebookLM_珥덇린濡쒓렇??bat' ?뚯씪???ㅽ뻾?섏뿬")
        print("    ?섑??섎뒗 釉뚮씪?곗? 李쎌뿉??濡쒓렇?몄쓣 ?꾨즺??二쇱꽭??")
        return False

def check_file_sync():
    print("[4] 援ш? ?쒕씪?대툕 ?뚯씪 ?숆린???뺤씤 以?..", end=" ", flush=True)
    critical_files = ["notebooklm_auto.py", "run_nlm_patched.py", "daily_news.py"]
    missing = [f for f in critical_files if not os.path.exists(f)]
    
    if not missing:
        print("??OK (紐⑤몢 議댁옱)")
        return True
    else:
        print(f"???뚯씪 ?꾨씫: {', '.join(missing)}")
        print("    -> 援ш? ?쒕씪?대툕(?곗뒪?ы넲??媛 ?ㅽ뻾 以묒씤吏 ?뺤씤?섏꽭??")
        return False

def main():
    print_banner()
    
    python_ok = check_python()
    lib_ok = check_libraries()
    file_ok = check_file_sync()
    login_ok = check_login()
    
    print("-" * 60)
    if python_ok and lib_ok and file_ok and login_ok:
        print("??[理쒖쥌 寃곌낵] ?숆탳 PC ?섍꼍???꾨꼍?섍쾶 以鍮꾨릺?덉뒿?덈떎! ??)
        print("?댁씪 15:15???댁긽 ?놁씠 ?먮룞?붽? ?ㅽ뻾???덉젙?낅땲??")
    else:
        print("?좑툘 [理쒖쥌 寃곌낵] ?쇰? ?먭? ??ぉ??議곗튂媛 ?꾩슂?⑸땲??")
        print("?꾩쓽 ???뱀? ?좑툘 ?쒖떆????ぉ???덈궡瑜??곕씪二쇱꽭??")
    print("-" * 60)
    
    input("\n醫낅즺?섎젮硫??뷀꽣瑜??꾨Ⅴ?몄슂...")

if __name__ == "__main__":
    main()
