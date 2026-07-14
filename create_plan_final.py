import win32com.client
import os
import time

def create_plan_fixed():
    try:
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.XHwpWindows.Item(0).Visible = True
        
        # 실제 양식 파일 경로 (첫 번째로 알려준 경로)
        template_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무 이외\수업 교환, 대강 계획서\2026학년도 수업 교환 및 대강 계획서(양식).hwp"
        desktop = r"D:\OneDrive - 경상남도교육청\바탕 화면"
        output_path = os.path.join(desktop, "2026.04.24 수업 대강 계획서(황요한).hwp")
        
        if not os.path.exists(template_path):
            print(f"Template not found: {template_path}")
            return

        hwp.Open(template_path)
        time.sleep(2)

        # 1. 일자 수정
        # "일 시" 또는 "202 ." 등의 패턴을 찾음
        hwp.HAction.GetDefault("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        hwp.HParameterSet.HFindReplace.FindString = "일 시"
        if hwp.HAction.Execute("RepeatFind", hwp.HParameterSet.HFindReplace.HSet):
            hwp.Run("MoveRight")
            hwp.Run("MoveRight")
            # 양식에는 빈칸이나 점이 있을 수 있음. 그냥 입력
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = " 2026. 4. 24.(금)"
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)

        # 2. 대강 내용 입력
        # "대강" 섹션을 찾아 표 내부로 진입
        hwp.HAction.GetDefault("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        hwp.HParameterSet.HFindReplace.FindString = "대강"
        hwp.HAction.Execute("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        
        # 표 내부 진입 (보통 글자 아래에 표가 있음)
        # "교시" 헤더를 찾아서 그 아래 행부터 입력
        hwp.HAction.GetDefault("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        hwp.HParameterSet.HFindReplace.FindString = "교시"
        hwp.HAction.Execute("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        
        hwp.Run("TableLowerCell") # 헤더 아래 행으로 이동
        
        def fill_row(period, class_info, subject, teacher):
            # 교시 입력
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = period
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
            
            hwp.Run("TableRightCell")
            # 학년-반
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = class_info
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
            
            hwp.Run("TableRightCell")
            # 결강과목
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = subject
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
            
            hwp.Run("TableRightCell")
            # 결강교사
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = "황요한"
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
            
            hwp.Run("TableRightCell")
            # 대강교사
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = teacher
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
            
            hwp.Run("TableRightCell")
            # 사유
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = "출장"
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
            
            hwp.Run("TableLowerCell")
            for _ in range(5): hwp.Run("TableLeftCell")

        # 데이터 입력
        fill_row("5", "3-3", "화법과 작문", "강필성 (국어)")
        fill_row("6", "2-9", "문학", "김승우 (국어)")

        # 3. 저장 (덮어쓰기)
        # HWP SaveAs can overwrite if the path is the same
        hwp.SaveAs(output_path)
        
        # 팝업 알림
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showinfo("Antigravity", f"양식에 맞춰 대강 계획서 작성을 완료하였습니다.\n바탕화면의 '{os.path.basename(output_path)}' 파일을 확인해주세요.")
        root.destroy()
        
        hwp.Quit()

    except Exception as e:
        print(f"ERROR: {e}")
        try: hwp.Quit()
        except: pass

if __name__ == "__main__":
    create_plan_fixed()
