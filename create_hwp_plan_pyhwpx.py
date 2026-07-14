from pyhwpx import Hwp
import os

def create_expert_hwp():
    try:
        hwp = Hwp()
        hwp.set_visible(False)
        
        desktop = r"D:\OneDrive - 경상남도교육청\바탕 화면"
        file_path = os.path.join(desktop, "대만 여행 계획.hwp")
        
        hwp.Run("FileNew")
        
        # 1. 제목 (단순화된 스타일링)
        hwp.set_font(FaceName="함초롬바탕", Height=24, Bold=True, TextColor="Navy")
        hwp.Run("ParagraphShapeAlignCenter")
        hwp.insert_text("대만 여행 계획서 (성인 남성 4인)\n\n")

        # 2. 본문 (스타일링 최소화하여 충돌 방지)
        hwp.Run("ParagraphShapeAlignJustify")
        hwp.set_font(FaceName="함초롬바탕", Height=12, Bold=True, TextColor="DarkBlue")
        hwp.insert_text("■ 1. 여행 개요\n")
        hwp.set_font(Height=11, Bold=False, TextColor="Black")
        hwp.insert_text("  - 일정: 2027년 1월 25일(월) ~ 2월 3일(수) (설 연휴 제외)\n  - 목적지: 대만 (타이베이 및 가오슝)\n  - 인원: 성인 남성 4명\n\n")

        hwp.set_font(Height=12, Bold=True, TextColor="DarkBlue")
        hwp.insert_text("■ 2. 항공권 예매 최저가 공략 (핵심 전략)\n")
        hwp.set_font(Height=11, Bold=False, TextColor="Black")
        hwp.insert_text("  - 예매 타이밍: 2026년 7월 ~ 8월 (LCC 동계 스케줄 오픈 즉시)\n")
        hwp.insert_text("  - 추천 항공사: 에어부산(Fly & Sale), 제주항공(JJIM), 타이거에어\n")
        hwp.insert_text("  - 핵심 전술: 2+2 분할 예매, 가오슝 입국 고려, 수하물 2인만 추가\n\n")

        hwp.set_font(Height=12, Bold=True, TextColor="DarkBlue")
        hwp.insert_text("■ 3. 숙소 및 현지 이동\n")
        hwp.set_font(Height=11, Bold=False, TextColor="Black")
        hwp.insert_text("  - 숙소: 시먼딩(Ximending) 인근 거실 포함 아파트형 숙소 권장\n  - 이동: 4인 이동 시 택시/우버가 가성비 최상, 고속열차 사전 예약 필수\n\n")
        
        hwp.set_font(Height=9, Italic=True, TextColor="Gray")
        hwp.Run("ParagraphShapeAlignRight")
        hwp.insert_text("작성: 인공지능 비서 Antigravity")
        
        hwp.save_as(file_path)
        hwp.quit()
        print(f"SUCCESS: Expert HWP created at {file_path}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    create_expert_hwp()
