import os
import sys
import io

# Windows 肄섏넄?먯꽌 UTF-8(?대え吏 ?ы븿) 異쒕젰 吏??if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

# Windows?먯꽌 ?뚯씠??COM ?쒖뼱瑜??꾪븳 ?쇱씠釉뚮윭由?try:
    from pyhwpx import Hwp
except ImportError:
    print("pyhwpx 紐⑤뱢???ㅼ튂?섏뼱 ?덉? ?딆뒿?덈떎. ?곕??먯뿉??'pip install pyhwpx'瑜??ㅽ뻾??二쇱꽭??")
    sys.exit(1)

def main():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    source_path = os.path.join(desktop, "2024?숇뀈???섏뾽援먰솚 諛??媛?怨꾪쉷???묒떇).hwp")
    target_path = os.path.join(desktop, "2024?숇뀈???섏뾽援먰솚 諛??媛?怨꾪쉷???덊떚洹몃옒鍮꾪떚 ?앹꽦 ?뚯씪).hwp")

    if not os.path.exists(source_path):
        print(f"???먮낯 ?뚯씪??李얠쓣 ???놁뒿?덈떎: {source_path}")
        return

    print("?? [HWP 諛깃렇?쇱슫??援щ룞 ?쒖옉]")
    # pyhwpx ?ъ슜 ??蹂댁븞 寃쎄퀬李??묎렐 ?덉슜)???섑??섏? ?딅룄濡??대??곸쑝濡??먮룞 泥섎━?⑸땲??
    hwp = Hwp()
    
    try:
        # 諛깃렇?쇱슫??紐⑤뱶濡??ㅽ뻾
        hwp.set_visible(False)

        print(f"?뱰 ?먮낯 ?뚯씪 ?щ뒗 以?.. ({source_path})")
        hwp.open(source_path)

        # ---------------------------------------------------------
        # 1. ?띿뒪???쇨큵 移섑솚 (寃곗옱?? ?대쫫 ??
        # ---------------------------------------------------------
        def replace_text(old_text, new_text):
            hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
            hwp.HParameterSet.HFindReplace.FindString = old_text
            hwp.HParameterSet.HFindReplace.ReplaceString = new_text
            hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
            hwp.HParameterSet.HFindReplace.Direction = 2 # 2=AllDoc (臾몄꽌 ?꾩껜 寃??
            hwp.HAction.Execute("AllReplace", hwp.HParameterSet.HFindReplace.HSet)

        print("?뵇 ?띿뒪??移섑솚 以?..")
        replace_text("2024??  00??  00??, "2026??4??11??) # ?섎떒 ?쒕챸??        replace_text("2024?? ?? ??, "2026??4??8??) # 2. 寃곌컯 ?쇱옄
        replace_text("2024?숇뀈??, "2026?숇뀈??)
        replace_text("0 0 0", "?⑹슂??)
        replace_text("0   0   0", "?? ?? ??) # ?ㅽ럹?댁뒪諛?泥섎━??遺遺??덉쇅 諛⑹뼱
        replace_text("1. 援먯궗 ?깅챸 : ", "1. 援먯궗 ?깅챸 : ?⑹슂??")
        replace_text("3. 寃곌컯 ?ъ쑀 : ", "3. 寃곌컯 ?ъ쑀 : 媛쒖씤 ?ъ쑀")

        # ---------------------------------------------------------
        # 2. '?섏뾽 援먰솚' ??李얠븘???곗씠???쎌엯
        # ---------------------------------------------------------
        def insert_text(text):
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = str(text)
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)

        # 而ㅼ꽌瑜?臾몄꽌 留??꾨줈 ?대룞
        hwp.Run("MoveDocBegin")

        print("?렞 ??? ?꾩튂 異붿쟻 諛??쎌엯 以?..")
        # '?쇱옄(?붿씪)' 臾몄옄?댁쓣 李얠븘??洹?移몄쑝濡?而ㅼ꽌 ?대룞
        hwp.HAction.GetDefault("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        hwp.HParameterSet.HFindReplace.FindString = "?쇱옄(?붿씪)"
        hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
        hwp.HAction.Execute("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)

        # 釉붾줉吏?뺣맂 ?곹깭瑜???댁쨲
        hwp.Run("Cancel")

        # ?꾩옱 而ㅼ꽌(?ㅻ뜑 '?쇱옄')?먯꽌 ??移??꾨옒 ?濡??대젮媛?(?곗씠?곌? ?ㅼ뼱媛?鍮덉뭏 泥ル쾲吏???
        hwp.Run("TableLowerCell")

        # 李⑤??濡?5媛쒖쓽 ?곗씠???쎌엯 ???곗륫 ?濡??대룞
        insert_text("4/11")        # ?쇱옄(移??묒냼瑜?怨좊젮?섏뿬 媛꾨왂蹂몄쑝濡쒕룄 ?곷땲?? ?좎깮???묒떇??4??11?쇰줈 ?쇰떎硫?"4??11??)
        hwp.Run("TableRightCell")
        insert_text("3援먯떆")
        hwp.Run("TableRightCell")
        insert_text("2諛?)
        hwp.Run("TableRightCell")
        insert_text("援?뼱")
        hwp.Run("TableRightCell")
        insert_text("?⑹슂??)

        # ---------------------------------------------------------
        # 3. ??????リ린
        # ---------------------------------------------------------
        print(f"?뮶 ???뚯씪 ???以?.. ({target_path})")
        hwp.save_as(target_path)
        print("?럦 [?꾨즺] ?뚯씪??諛뷀깢?붾㈃???깃났?곸쑝濡??앹꽦?섏뿀?듬땲??")

    except Exception as e:
        print(f"??HWP ?쒖뼱 以??먮윭 諛쒖깮: {e}")
    finally:
        # 醫낅즺 泥섎━瑜??섏? ?딆쑝硫??꾨줈?몄뒪媛 諛깃렇?쇱슫?쒖뿉 ?⑥븘 ?됱씠 嫄몃┝
        print("?㏏ 由ъ냼???뺣━ 諛??쒓? 醫낅즺")
        hwp.quit()

if __name__ == "__main__":
    main()
