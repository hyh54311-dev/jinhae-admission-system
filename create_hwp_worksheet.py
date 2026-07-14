from pyhwpx import Hwp
import os

def create_worksheet():
    try:
        hwp = Hwp()
        hwp.set_visible(False)
        
        desktop = r"D:\OneDrive - 경상남도교육청\바탕 화면"
        file_path = os.path.join(desktop, "1980년대_두시선_학습지.hwp")
        
        hwp.Run("FileNew")
        
        # 1. 제목
        hwp.set_font(FaceName="맑은 고딕", Height=20, Bold=True, TextColor="Navy")
        hwp.Run("ParagraphShapeAlignCenter")
        hwp.insert_text("[2학년 문학] 1980년대, 억압적 현실을 바라보는 두 가지 시선\n\n")
        
        # 이름 기입란
        hwp.Run("ParagraphShapeAlignRight")
        hwp.set_font(FaceName="맑은 고딕", Height=11, Bold=False, TextColor="Black")
        hwp.insert_text("[ 반 / 번호 / 이름:                 ]\n\n")

        # 2. 첫 번째 시
        hwp.Run("ParagraphShapeAlignJustify")
        hwp.set_font(FaceName="맑은 고딕", Height=14, Bold=True, TextColor="DarkBlue")
        hwp.insert_text("1. 최승호, 「대설주의보」\n\n")
        
        hwp.set_font(Height=11, Bold=False, TextColor="Black")
        hwp.insert_text("▶ 핵심 시구 분석\n")
        hwp.insert_text(" - 해일처럼 굽이치는 백색의 산들 : 압도적이고 위협적인 ( 현실 )\n")
        hwp.insert_text(" - 제설차 한 대 올 리 없는 : 문제를 해결할 방법이 없는 ( 절망적 ) 현실\n")
        hwp.insert_text(" - 눈보라의 군단, 백색의 계엄령 : ( 군사 ) 용어를 사용하여 폭압적 모습을 나타냄\n")
        hwp.insert_text(" - 눈보라가 내리는 백색의 계엄령 : \n")
        hwp.insert_text("   1) ( 중의적 ) 해석 가능 (눈보라/계엄령이 내리다)\n")
        hwp.insert_text("   2) 시행의 ( 반복 )을 통해 폭압적 상황 강조\n")
        hwp.insert_text("   3) ( 명사형 ) 종결어미를 통해 엄중한 분위기를 형성하고 억압이 지속됨을 상기시킴\n\n")
        
        hwp.insert_text("▶ 대립적 의미의 시어 찾기\n")
        hwp.insert_text(" - 폭력적이고 억압적인 세력 ( 폭설 ): 눈보라, 군단, 백색의 계엄령 등\n")
        hwp.insert_text(" - 연대와 생명력을 잃지 않는 ( 민중 ): 굴뚝새, 노루, 할머니의 화로(숯불) 등\n\n\n")

        # 3. 두 번째 시
        hwp.set_font(Height=14, Bold=True, TextColor="DarkBlue")
        hwp.insert_text("2. 황지우, 「새들도 세상을 뜨는구나」\n\n")
        
        hwp.set_font(Height=11, Bold=False, TextColor="Black")
        hwp.insert_text("▶ 시적 상황: 영화 상영 전 ( 애국가 )가 울려 퍼지는 극장 안. 1980년대 군사 독재 시절의 획일적이고 ( 강압적 )인 시대 현실을 보여줌.\n\n")
        
        hwp.insert_text("▶ 시적 의미 및 화자의 태도 분석\n")
        hwp.insert_text(" - 자기들끼리 낄낄대면서 / 깔죽대면서 : 강압적인 현실에 대한 화자의 자조적이고 ( 냉소적 )인 태도 (비웃음)\n")
        hwp.insert_text(" - 이 세상 밖 어디론가 날아간다 / 우리도 날아갔으면 하는데 : 억압적 현실에서 벗어난 '자유로운 ( 이상향 )'에 대한 강렬한 갈망\n")
        hwp.insert_text(" - 각자의 자리에 주저앉는다 : 현실의 벽을 넘지 못하고 억압에 순응할 수밖에 없는 소시민적 ( 무력감 )과 체념(좌절)\n\n\n")

        # 4. 종합 정리
        hwp.set_font(Height=14, Bold=True, TextColor="DarkBlue")
        hwp.insert_text("3. 종합 정리: 두 작품 완벽 비교\n\n")
        
        hwp.set_font(Height=11, Bold=False, TextColor="Black")
        hwp.insert_text(" - 공통된 시대적 배경: ( 1980년대 ) 군사 독재 정권의 억압적 현실\n")
        hwp.insert_text(" - 억압적 현실을 상징하는 소재: [대설주의보] ( 폭설 ) / [새들도 세상을 뜨는구나] ( 애국가 )\n")
        hwp.insert_text(" - 암울한 현실에 대응하는 태도 및 결말:\n")
        hwp.insert_text("   [대설주의보] 숯불(온기)을 통해 끈질긴 생명력과 ( 연대 )를 보여줌\n")
        hwp.insert_text("   [새들도 세상을 뜨는구나] 현실의 벽에 막혀 자리에 ( 주저앉는 ) 무력감과 좌절을 보여줌\n\n")
        
        hwp.save_as(file_path)
        hwp.quit()
        print(f"SUCCESS: HWP created at {file_path}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    create_worksheet()
