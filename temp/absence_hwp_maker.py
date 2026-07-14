import os
import sys
import glob
import json
import time
import shutil

try:
    from pyhwpx import Hwp
except ImportError:
    print("pyhwpx_local 紐⑤뱢 ?ㅻ쪟. 'pip install pyhwpx' 瑜??뺤씤?섏꽭??")
    sys.exit(1)

def main():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    queue_dir = os.path.join(desktop, "寃곗꽍?뺤씤???湲곗뿴")
    done_dir = os.path.join(desktop, "寃곗꽍?뺤씤???꾨즺")
    # ?묒떇 ?뚯씪 (?섏쨷???좎깮?섍퍡???쒗뵆由우쓣 留뚮뱶?쒕㈃ ???대쫫??諛붽씀硫??⑸땲??
    template_path = os.path.join(desktop, "寃곗꽍?뺤씤???묒떇).hwp")

    # ????대뜑媛 ?놁쑝硫??앹꽦 (?깆씠 援щ룞?????덉젙?깆쓣 ?꾪빐)
    os.makedirs(queue_dir, exist_ok=True)
    os.makedirs(done_dir, exist_ok=True)

    print("===========================================")
    print("?쨼 ?먮룞 寃곗꽍?뺤씤??諛쒓툒 遊??湲?以?..")
    print(f"?뱛 媛먯떆 ?대뜑: {queue_dir}")
    print("===========================================")

    hwp = None

    while True:
        # ???대뜑 ?덉뿉 ?덈뒗 紐⑤뱺 JSON ?뚯씪(援ш? ???곗씠????李얠쓬
        json_files = glob.glob(os.path.join(queue_dir, "*.json"))
        
        if not json_files:
            time.sleep(5) # 5珥덈쭏??媛먯떆
            continue

        for j_file in json_files:
            try:
                print(f"\n?벂 ??寃곗꽍 ?좎껌???묒닔?? {os.path.basename(j_file)}")
                
                # 1. ?뚯씪?먯꽌 ?곗씠???쎄린
                with open(j_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                student_name = data.get("name", "?대쫫?놁쓬")
                absence_date = data.get("date", "?좎쭨?놁쓬")
                absence_reason = data.get("reason", "?ъ쑀?놁쓬")
                # std_class ???몃? ?뺣낫???ш린??爰쇰궡 ?????덉뒿?덈떎.
                
                if not os.path.exists(template_path):
                    print("?좑툘 ?ㅻ쪟: 諛뷀깢?붾㈃??'寃곗꽍?뺤씤???묒떇).hwp' ?뚯씪???놁뒿?덈떎. ?묒떇??以鍮꾪빐 二쇱꽭??")
                    time.sleep(10)
                    break
                
                # 2. ?쒓? ?꾨줈?몄뒪 ?닿린 (泥??뚯씪 泥섎━ ?쒖뿉留?
                if hwp is None:
                    print("?? ?쒓?(HWP) 諛깃렇?쇱슫???붿쭊 援щ룞 以?..")
                    hwp = Hwp()
                    hwp.set_visible(False)

                hwp.open(template_path)
                print(f"?뱷 {student_name} ?숈깮 ?뺤씤???앹꽦 以?..")

                # -----------------------------------------------------------------
                # [?ш린???쒖떇 蹂듭궗/遺숈뿬?ｊ린/移섑솚 濡쒖쭅???ㅼ뼱媛묐땲??
                # ?덉떆: 誘몃━ ?쒗뵆由우뿉 {{?대쫫}}, {{寃곗꽍?쇱옄}} ?깆쓣 ?곸뼱?먭퀬 李얠븘 諛붽씀湲?                # ?ㅼ젣 ?묒떇???ㅻ㈃ ??遺遺꾩쓣 hwp.TableRightCell() ?깆쑝濡?怨좊룄?뷀빀?덈떎.
                # -----------------------------------------------------------------
                def replace_text(old_text, new_text):
                    hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
                    hwp.HParameterSet.HFindReplace.FindString = old_text
                    hwp.HParameterSet.HFindReplace.ReplaceString = new_text
                    hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
                    hwp.HParameterSet.HFindReplace.Direction = 2 
                    hwp.HAction.Execute("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
                
                replace_text("{{?대쫫}}", student_name)
                replace_text("{{寃곗꽍?쇱옄}}", absence_date)
                replace_text("{{寃곗꽍?ъ쑀}}", absence_reason)
                
                # 3. ???뚯씪濡????                target_filename = f"寃곗꽍?뺤씤??{student_name}_{absence_date.replace('/','')}.hwp"
                target_path = os.path.join(done_dir, target_filename)
                
                hwp.save_as(target_path)
                print(f"???앹꽦 ?꾨즺: [寃곗꽍?뺤씤???꾨즺] ?대뜑????λ릺?덉뒿?덈떎.")

                # 4. ?ъ슜???앸궃 JSON 履쎌????????대뜑濡??대룞(援ш? ?쒕씪?대툕 ?숆린??諛⑹?)
                shutil.move(j_file, os.path.join(done_dir, os.path.basename(j_file)))
                
            except Exception as e:
                print(f"???묒뾽 以??ㅻ쪟 諛쒖깮: {e}")

        # 紐⑤뱺 泥섎━媛 ?앸궃 ???뚯씪???좎떆 ?湲?        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n遊뉗쓣 醫낅즺?⑸땲??")
