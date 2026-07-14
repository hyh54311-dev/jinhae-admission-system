import win32com.client
import os

def create_expert_hwp():
    try:
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.XHwpWindows.Item(0).Visible = False
        
        desktop = r"D:\OneDrive - 경상남도교육청\바탕 화면"
        file_path = os.path.join(desktop, "대만 여행 계획.hwp")
        hwp.Run("FileNew")

        def insert_text(text):
            act = hwp.CreateAction("InsertText")
            pset = act.CreateSet()
            pset.SetItem("Text", text)
            act.Execute(pset)

        def set_char_shape(size, bold, color):
            act = hwp.CreateAction("CharShape")
            pset = act.CreateSet()
            act.GetDefault(pset)
            pset.SetItem("Height", size)
            pset.SetItem("Bold", bold)
            pset.SetItem("TextColor", color)
            act.Execute(pset)

        def set_align(align_type):
            act = hwp.CreateAction("ParagraphShape")
            pset = act.CreateSet()
            act.GetDefault(pset)
            pset.SetItem("AlignType", align_type)
            act.Execute(pset)

        # 제목
        set_char_shape(2200, 1, 0x663300)
        set_align(3)
        insert_text("대만 여행 계획서 (성인 남성 4인)\r\n\r\n")

        # 본문
        set_align(0)
        
        set_char_shape(1300, 1, 0x804000)
        insert_text("■ 1. 여행 개요\r\n")
        set_char_shape(1000, 0, 0)
        insert_text("  - 일정: 2027년 1월 25일(월) ~ 2월 3일(수)\r\n  - 목적지: 대만 (타이베이 및 가오슝)\r\n  - 인원: 성인 남성 4명\r\n\r\n")

        set_char_shape(1300, 1, 0x804000)
        insert_text("■ 2. 항공권 예매 최저가 공략\r\n")
        
        # 표 생성
        act = hwp.CreateAction("TableCreate")
        pset = act.CreateSet()
        act.GetDefault(pset)
        pset.SetItem("Rows", 3)
        pset.SetItem("Cols", 2)
        act.Execute(pset)

        def fill_cell(text, bold=0):
            set_char_shape(1000, bold, 0)
            insert_text(text)
            hwp.Run("TableRightCell")

        fill_cell("예매 타이밍", 1); fill_cell("2026년 7월 ~ 8월 (LCC 오픈 즉시)")
        fill_cell("추천 항공사", 1); fill_cell("에어부산, 제주항공, 타이거에어")
        fill_cell("핵심 전략", 1); fill_cell("2+2 분할 예매, 가오슝 루트 활용")

        hwp.Run("MoveDocEnd")
        insert_text("\r\n")
        
        set_char_shape(1300, 1, 0x804000)
        insert_text("■ 3. 숙소 및 현지 이동\r\n")
        set_char_shape(1000, 0, 0)
        insert_text("  - 숙소: 시먼딩 인근 거실 포함 아파트형 숙소 추천\r\n  - 이동: 4인 택시/우버 이용 시 가성비 최상\r\n\r\n")

        hwp.SaveAs(file_path)
        hwp.Quit()
        print(f"SUCCESS: Expert HWP created at {file_path}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    create_expert_hwp()
