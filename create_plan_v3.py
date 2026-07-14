import win32com.client
import os
import time

def create_plan_v3():
    try:
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.XHwpWindows.Item(0).Visible = True
        
        ref_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무 이외\수업 교환, 대강 계획서\2026학년도 수업 교환 및 대강 계획서(2026.3.6.).hwp"
        desktop = r"D:\OneDrive - 경상남도교육청\바탕 화면"
        output_path = os.path.join(desktop, "2026.04.24 수업 대강 계획서(황요한).hwp")
        
        if not os.path.exists(ref_path):
            print(f"Reference file not found: {ref_path}")
            return

        hwp.Open(ref_path)
        time.sleep(2)

        # 1. 일자 수정 (검색 및 이동)
        hwp.HAction.GetDefault("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        hwp.HParameterSet.HFindReplace.FindString = "2026."
        hwp.HAction.Execute("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        
        # 날짜 부분 덮어쓰기 (단어 선택 후 입력)
        hwp.Run("MoveSelWordEnd")
        hwp.Run("Delete")
        hwp.Run("Delete")
        hwp.Run("Delete")
        hwp.Run("Delete")
        hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = " 4. 24.(금)"
        hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)

        # 2. 대강 테이블 찾기
        hwp.HAction.GetDefault("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        hwp.HParameterSet.HFindReplace.FindString = "교시"
        # "대강" 섹션의 "교시"를 찾기 위해 두 번 검색할 수도 있음
        hwp.HAction.Execute("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        hwp.HAction.Execute("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)

        # 행 추가 로직
        # 현재 위치가 헤더일 테니 아래로 이동
        hwp.Run("TableLowerCell")
        
        def add_row_data(period, class_info, subject, teacher):
            hwp.Run("TableCellBlock") # 현재 셀 선택
            hwp.Run("Delete") # 기존 내용 삭제
            hwp.Run("Cancel")
            
            # 입력
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = period
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
            
            hwp.Run("TableRightCell")
            hwp.Run("TableCellBlock"); hwp.Run("Delete"); hwp.Run("Cancel")
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = class_info
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
            
            hwp.Run("TableRightCell")
            hwp.Run("TableCellBlock"); hwp.Run("Delete"); hwp.Run("Cancel")
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = subject
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
            
            hwp.Run("TableRightCell")
            hwp.Run("TableCellBlock"); hwp.Run("Delete"); hwp.Run("Cancel")
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = "황요한"
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
            
            hwp.Run("TableRightCell")
            hwp.Run("TableCellBlock"); hwp.Run("Delete"); hwp.Run("Cancel")
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = teacher
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
            
            hwp.Run("TableRightCell")
            hwp.Run("TableCellBlock"); hwp.Run("Delete"); hwp.Run("Cancel")
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = "출장"
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
            
            hwp.Run("TableLowerCell")
            for _ in range(5): hwp.Run("TableLeftCell")

        # 5교시 3-3 강필성
        add_row_data("5", "3-3", "화법과 작문", "강필성 (국어)")
        # 6교시 2-9 김승우
        add_row_data("6", "2-9", "문학", "김승우 (국어)")

        # 3. 저장 및 완료
        hwp.SaveAs(output_path)
        
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showinfo("Antigravity", f"대강 계획서 작성을 완료하였습니다.\n바탕화면의 '{os.path.basename(output_path)}' 파일을 확인해주세요.")
        root.destroy()
        
        hwp.Quit()

    except Exception as e:
        print(f"ERROR: {e}")
        try: hwp.Quit()
        except: pass

if __name__ == "__main__":
    create_plan_v3()
