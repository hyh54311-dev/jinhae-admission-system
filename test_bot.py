from bot_logic import get_answer_from_gemini

PDF_URLS = ["https://drive.google.com/file/d/1n9TbyKBxk9EKbwlVpBToNM4AeoM9LCK-/view?usp=sharing"]

if __name__ == "__main__":
    print("PDF 遺꾩꽍 以?.. ?좎떆留?湲곕떎??二쇱꽭??")
    try:
        # Test query
        test_query = "??PDF ?뚯씪???듭떖 ?댁슜??3湲?먮줈 ?붿빟??以?"
        result = get_answer_from_gemini(test_query, PDF_URLS)
        print("寃곌낵:", result)
    except Exception as e:
        print("?ㅻ쪟 諛쒖깮:", e)
