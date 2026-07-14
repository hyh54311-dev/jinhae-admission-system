from pyhwpx import Hwp
import os

def create_scholarship_minutes():
    hwp = Hwp()
    
    # 문서 기본 설정
    hwp.set_font(Size=15, Bold=True)
    hwp.insert_text("협  의  록\n")
    # hwp.ParaShape.Alignment = 2 # Center
    hwp.insert_text("\n")
    
    # 표 생성 (4행 2열 구조)
    table = hwp.insert_table(4, 2)
    
    # 표 너비 조절 (SetWidth 대신 다른 방식 또는 생략)
    # table.SetWidth(30, 0) # 첫 번째 열
    
    # 안건
    table.Cell(0, 0).insert_text("안  건")
    table.Cell(0, 1).insert_text("2026학년도 안주환 장학금 장학생 추천에 대한 추인")
    
    # 일시 및 장소
    table.Cell(1, 0).insert_text("일 시\n장 소")
    # 오른쪽 셀을 두 칸으로 나누거나 텍스트로 배치
    table.Cell(1, 1).insert_text("● 일시: 2026년 5월 7일(13:00 ~ )             ● 장소: 2층 교무실")
    
    # 참석자
    table.Cell(2, 0).insert_text("참석자\n(서 명)")
    table.Cell(2, 1).insert_text("위원장: 교감 (인),  교무부장 (인),  1학년부장 (인),  2학년부장 (인),  3학년부장 (인),  간사 (인)")
    
    # 회의 내용
    table.Cell(3, 0).insert_text("\n\n\n회\n\n의\n\n내\n\n용\n\n\n")
    
    content = (
        "1. 안건\n"
        "   안주환 장학금 장학생 선발과 관련하여 장학생선발소심의위원회의 추천자에 대한 추인\n\n"
        "2. 협의 내용\n"
        "   가. 추천 기준\n"
        "      1) 성적이 우수하나 경제적 어려움이 있는 학생\n"
        "      2) 학습 태도가 바르고 모범적인 학생\n"
        "      3) 특별한 재능과 능력이 있어 국가 및 학교의 명예를 선양할 수 있는 학생\n"
        "   나. 추천 인원은 총 5명으로 2학년 2명, 3학년 3명\n"
        "   다. 2학년부에서는 학교생활의 모든 면에서 우수한 모습을 보이고 있고, 경제적으로 어려운 학생이 없어 내신 성적순으로 "
        "2-1 정은준, 2-2 이승기 학생을 추천함. 3학년부에서도 추천 받은 학생 모두 학교생활의 모든 면에서 우수한 모습을 보이고 있어 "
        "내신 성적이 우수한 3-4 이윤건, 3-5 조윤성, 3-7 박예준 학생을 추천함.\n\n"
        "3. 회의 결과\n"
        "   장학생 선발 심의위원회의 협의 결과, 소심의위원회의 추천 학생에 다른 결격 사유가 없고, "
        "장학금 수여 목적과 선발 기준에 부합한다고 판단되어 해당 학생에 대한 추천을 추인함."
    )
    
    table.Cell(3, 1).insert_text(content)
    
    # 표 정렬 및 폰트 정리
    hwp.SelectAll()
    hwp.set_font(Name="바탕", Size=11)
    
    save_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\2026학년도 장학생선발심의위원회 협의록(안주환장학금).hwp"
    hwp.save_as(save_path)
    hwp.quit()
    print(f"파일이 성공적으로 생성되었습니다: {save_path}")

if __name__ == "__main__":
    create_scholarship_minutes()
