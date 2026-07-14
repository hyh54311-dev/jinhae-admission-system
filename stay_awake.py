import ctypes
import time
import threading

# Windows API Constants
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_AWAYMODE_REQUIRED = 0x00000040

def keep_system_awake():
    """?쒖뒪???덉쟾 紐⑤뱶瑜?諛⑹??섎뒗 猷⑦봽 (諛깃렇?쇱슫???ㅻ젅?쒖슜)"""
    try:
        # ES_SYSTEM_REQUIRED: ?쒖뒪???덉쟾 諛⑹?
        # ES_AWAYMODE_REQUIRED: ?붾㈃??爰쇱졇???쒖뒪?쒖? ?묐룞 ?좎? (Modern Standby ???
        # ES_CONTINUOUS: ?ㅼ젙??怨꾩냽 ?좎?
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED
        )
        print("[StayAwake] ?쒖뒪???덉쟾 諛⑹? 紐⑤뱶媛 ?쒖꽦?붾릺?덉뒿?덈떎.")
        
        while True:
            # 二쇨린?곸쑝濡???踰덉뵫 ???몄텧?댁쨲 (?덉젙???뺣낫)
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED
            )
            time.sleep(60)
    except Exception as e:
        print(f"[StayAwake] ?ㅻ쪟 諛쒖깮: {e}")

def start_stay_awake_thread():
    """蹂꾨룄 ?ㅻ젅?쒖뿉???덉쟾 諛⑹? ?쒖옉"""
    thread = threading.Thread(target=keep_system_awake, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    # ?⑤룆 ?ㅽ뻾 ???뚯뒪?몄슜
    print("10遺??숈븞 ?덉쟾 諛⑹? ?뚯뒪?몃? ?섑뻾?⑸땲??..")
    start_stay_awake_thread()
    time.sleep(600)
