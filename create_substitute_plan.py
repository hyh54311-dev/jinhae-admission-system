import win32com.client
import os
import time

def create_substitute_plan():
    try:
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.XHwpWindows.Item(0).Visible = True # Show it so we can see what's happening
        
        template_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무 이외\수업 교환, 대강 계획서\2026학년도 수업 교환 및 대강 계획서(양식).hwp"
        desktop = r"D:\OneDrive - 경상남도교육청\바탕 화면"
        output_path = os.path.join(desktop, "2026.04.24 수업 대강 계획서(황요한).hwp")
        
        if not os.path.exists(template_path):
            print(f"Template not found: {template_path}")
            return

        hwp.Open(template_path)
        time.sleep(1)

        # 1. 일자 수정 (4.24(금) 삽입)
        # 보통 "2026.  .  ." 또는 "일시 :" 뒤에 빈칸이 있음. 
        # 여기서는 "일 시"를 찾아서 그 옆에 날짜를 넣거나, 적절한 위치를 찾습니다.
        hwp.HAction.GetDefault("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        hwp.HParameterSet.HFindReplace.FindString = "일 시"
        if hwp.HAction.Execute("RepeatFind", hwp.HParameterSet.HFindReplace.HSet):
            hwp.Run("MoveRight")
            hwp.Run("MoveRight")
            hwp.InsertText(" 2026. 4. 24.(금)")

        # 2. 대강 내용 입력
        # "대강"을 찾고 그 아래 표로 이동
        hwp.HAction.GetDefault("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        hwp.HParameterSet.HFindReplace.FindString = "대강"
        hwp.HAction.Execute("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        
        # 표 내부로 진입 (보통 대강 아래에 표가 있음)
        # 표가 나올 때까지 아래로 이동
        found_table = False
        for _ in range(10):
            hwp.Run("MoveDown")
            if hwp.ParentCtrl: # 윈도우 기반 API에서 표 안에 있는지 확인
                found_table = True
                break
        
        if not found_table:
            # 대강 글자 자체를 선택하고 아래로
            hwp.Run("MoveDown")
        
        # 표의 첫 번째 셀로 이동
        hwp.Run("TableLowerCell")
        hwp.Run("TableCellBlock")
        hwp.Run("Cancel") # 선택 해제

        # 데이터 채우기 함수
        def fill_row(period, grade_class, missing_sub, sub_teacher, sub_sub):
            # 교시 | 학년-반 | 결강과목 | 결강교사 | 대강교사 | 대강사유
            # 순서는 양식마다 다를 수 있으나 보통 이렇습니다.
            # 5 | 3-3 | 화법과 작문 | 황요한 | 강필성 (국어) | 출장
            hwp.InsertText(period)
            hwp.Run("TableRightCell")
            hwp.InsertText(grade_class)
            hwp.Run("TableRightCell")
            hwp.InsertText(missing_sub)
            hwp.Run("TableRightCell")
            hwp.InsertText("황요한")
            hwp.Run("TableRightCell")
            hwp.InsertText(sub_teacher)
            hwp.Run("TableRightCell")
            hwp.InsertText("출장")
            hwp.Run("TableLowerCell")
            for _ in range(5): hwp.Run("TableLeftCell") # 다시 앞으로

        # 5교시 3-3 강필성
        fill_row("5", "3-3", "화법과 작문", "강필성 (국어)", "화법과 작문")
        # 6교시 2-9 김승우
        fill_row("6", "2-9", "문학", "김승우 (국어)", "문학")

        # 3. 저장 및 완료 알림
        hwp.SaveAs(output_path)
        print(f"SUCCESS: Saved to {output_path}")
        
        # 알림창 띄우기 (별도 프로세스로 실행 권장하지만 여기서는 간단히)
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Antigravity", f"대강 계획서 작성을 완료하였습니다.\n바탕화면의 '{os.path.basename(output_path)}' 파일을 확인해주세요.")
        root.destroy()

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        try:
            hwp.Quit()
        except:
            pass

if __name__ == "__main__":
    create_substitute_plan()
