from pyhwpx import Hwp
import os
import shutil

def create_substitute_plan_from_reference():
    try:
        hwp = Hwp()
        hwp.set_visible(True)
        
        ref_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무 이외\수업 교환, 대강 계획서\2026학년도 수업 교환 및 대강 계획서(2026.3.6.).hwp"
        desktop = r"D:\OneDrive - 경상남도교육청\바탕 화면"
        output_path = os.path.join(desktop, "2026.04.24 수업 대강 계획서(황요한).hwp")
        
        if not os.path.exists(ref_path):
            print(f"Reference file not found: {ref_path}")
            return

        hwp.open(ref_path)
        
        # 1. 일자 수정
        # 이전 파일이 2026. 3. 6. 일 테니 이를 검색해서 수정
        hwp.find_all("2026.")
        # 보통 "2026.  .  ." 형식이거나 날짜가 적혀있음
        # 안전하게 "일 시" 뒤를 찾음
        if hwp.find_all("일 시"):
            hwp.move_right()
            hwp.move_right()
            # 기존 날짜 지우기 (단어 끝까지)
            hwp.run("MoveSelWordEnd")
            hwp.run("Delete")
            hwp.insert_text(" 2026. 4. 24.(금)")

        # 2. 대강 테이블 찾기
        # "대강" 텍스트를 찾음
        if hwp.find_all("대강"):
            # 보통 제목 바로 아래 표가 있음
            hwp.move_down()
            # 표 내부로 진입 (pyhwpx의 경우 move_down이 표 내부로 들어갈 수 있음)
            # 만약 표 안에 있다면 첫 번째 셀로 이동
            if hwp.is_in_table():
                # 표의 모든 내용 지우기 (헤더 제외하고 지우는 게 좋지만 일단 빈 줄 추가)
                # 안전하게: "교시" 행 아래부터 지우거나, 새로운 행을 추가
                pass
            
        # 데이터 삽입 로직
        # 5교시 3-3 강필성(국어) 화법과 작문
        # 6교시 2-9 김승우(국어) 문학
        
        # 실제로는 표의 구조를 정확히 맞추기 위해 
        # "교시"가 있는 표를 찾아서 그 행 아래에 데이터를 넣음
        
        hwp.find_all("교시")
        if hwp.is_in_table():
            # "교시"가 있는 행에서 아래로 이동하여 데이터 입력 시작
            hwp.move_down()
            
            def add_data(period, class_info, subject, teacher):
                hwp.insert_text(period)
                hwp.table_right_cell()
                hwp.insert_text(class_info)
                hwp.table_right_cell()
                hwp.insert_text(subject)
                hwp.table_right_cell()
                hwp.insert_text("황요한")
                hwp.table_right_cell()
                hwp.insert_text(teacher)
                hwp.table_right_cell()
                hwp.insert_text("출장")
                hwp.table_lower_cell()
                for _ in range(5): hwp.table_left_cell()

            add_data("5", "3-3", "화법과 작문", "강필성 (국어)")
            add_data("6", "2-9", "문학", "김승우 (국어)")

        # 3. 저장 및 팝업
        hwp.save_as(output_path)
        print(f"SUCCESS: Created {output_path}")
        
        # 팝업 알림 (tkinter)
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showinfo("Antigravity", f"대강 계획서 작성을 완료하였습니다.\n바탕화면의 '{os.path.basename(output_path)}' 파일을 확인해주세요.")
        root.destroy()
        
        hwp.quit()

    except Exception as e:
        print(f"ERROR: {e}")
        try: hwp.quit()
        except: pass

if __name__ == "__main__":
    create_substitute_plan_from_reference()
