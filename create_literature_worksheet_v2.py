import os
import time
import ctypes
from pyhwpx import Hwp

def show_popup():
    ctypes.windll.user32.MessageBoxW(0, "학습지 생성이 완료되었습니다!", "작업 완료", 0x40 | 0x1)

def build_worksheet():
    desktop = r"D:\OneDrive - 경상남도교육청\바탕 화면"
    file_path = os.path.join(desktop, "[최종] 1980년대_두시선_심화학습.hwp")
    
    hwp = Hwp()
    hwp.set_visible(False)
    
    try:
        hwp.Run("FileNew")
        
        # --- 1. Header ---
        hwp.set_font(FaceName="맑은 고딕", Height=24, Bold=True)
        hwp.Run("ParagraphShapeAlignCenter")
        hwp.insert_text("「1980년대 시 두편」 심화 학습지\n\n")
        
        hwp.set_font(FaceName="맑은 고딕", Height=12, Bold=False)
        hwp.Run("ParagraphShapeAlignRight")
        hwp.insert_text("2학년 (     )반 (     )번 이름: (         )\n\n")
        
        # --- 2. Section 1 ---
        hwp.Run("ParagraphShapeAlignLeft")
        hwp.set_font(FaceName="맑은 고딕", Height=14, Bold=True)
        hwp.insert_text("1. 최승호,  「대설주의보」\n")
        
        # Table 1: 2 rows, 2 columns (1 row for header, 1 for content)
        hwp.create_table(2, 2)
        hwp.set_font(FaceName="맑은 고딕", Height=11, Bold=True)
        hwp.insert_text("시의 본문원문")
        hwp.Run("TableRightCell")
        hwp.set_font(FaceName="맑은 고딕", Height=11, Bold=True)
        hwp.insert_text("시적 의미 및 화자의 태도 분석")
        
        hwp.Run("TableRightCell")
        hwp.set_font(FaceName="맑은 고딕", Height=10, Bold=False)
        t1_c1 = """해일처럼 굽이치는 백색의 산들
제설차 한 대 올 리 없는
깊은 백색의 골짜기를 메우며
굵은 눈발은 휘몰아치고,
쬐그마한 숯덩이만한 게 짧은 날개를 파닥이며……
굴뚝새가 눈보라 속으로 날아간다.

길 잃은 등산객들 있을 듯
외딴 두메마을 길 끊어놓을 듯
은하수가 펑펑 쏟아져 날아오듯 덤벼드는 눈,
다투어 몰려오는 힘찬 눈보라의 군단,
눈보라가 내리는 백색의 계엄령.

쬐그마한 숯덩이만한 게 짧은 날개를 파닥이며……
날아온다 꺼칠한 굴뚝새가
서둘러 뒷간에 몸을 감춘다.
그 어디에 부리부리한 솔개라도 도사리고 있다는 것일까.

길 잃고 굶주리는 산짐승들 있을 듯
눈더미의 무게로 소나무 가지들이 부러질 듯
다투어 몰려오는 힘찬 눈보라의 군단,
때죽나무와 때 끓이는 외딴집 굴뚝에
해일처럼 굽이치는 백색의 산과 골짜기에
눈보라가 내리는
백색의 계엄령."""
        hwp.insert_text(t1_c1)
        
        hwp.Run("TableRightCell")
        hwp.set_font(FaceName="맑은 고딕", Height=10, Bold=False)
        t1_c2 = """• 해일처럼 굽이치는 백색의 산들:
➡ 압도적이고 위협적인 현실 

• 제설차 한 대 올 리 없는:
➡ 문제를 해결할 방법이 없는 절망적 현실

• 눈보라의 군단, 백색의 계엄령:
➡ 군사 용어를 사용하여 군사 독재 세력의 폭압적 모습을 나타냄

• 눈보라가 내리는 백색의 계엄령:
① 중의적 해석 가능 – 눈보라가 내리다/계엄령이 내리다
② 시행의 반복(2연, 4연)을 통해 폭압적 시대 상황 강조
③ 명사형 종결어미를 통해 엄중한 분위기를 형성하고 억압이 지속됨을 상기시킴

• 대립적 의미의 시어 분석:
- 해일, 굵은 눈발, 눈보라의 군단, 백색의 계엄령, 부리부리한 솔개:
➡ 민중을 위협하는 폭력적이고 억압적인 세력(군부 독재 정권)

- 굴뚝새, 길 잃은 등산객, 외딴 두메 마을, 길 잃고 굶주리는 산짐승, 소나무 가지, 외딴집 굴뚝:
➡ 나약한 존재이자 억압된 민중의 모습"""
        hwp.insert_text(t1_c2)
        
        # Exit table 1
        hwp.Run("CloseEx") 
        hwp.Run("MoveDocEnd")
        hwp.insert_text("\n\n")
        
        # --- 3. Section 2 ---
        hwp.set_font(FaceName="맑은 고딕", Height=14, Bold=True)
        hwp.insert_text("2. 황지우, 「새들도 세상을 뜨는구나」\n")
        
        hwp.create_table(2, 2)
        hwp.set_font(FaceName="맑은 고딕", Height=11, Bold=True)
        hwp.insert_text("시의 본문원문")
        hwp.Run("TableRightCell")
        hwp.set_font(FaceName="맑은 고딕", Height=11, Bold=True)
        hwp.insert_text("시적 의미 및 화자의 태도 분석")
        
        hwp.Run("TableRightCell")
        hwp.set_font(FaceName="맑은 고딕", Height=10, Bold=False)
        t2_c1 = """영화가 시작하기 전에 우리는
일제히 일어나 애국가를 경청한다
삼천리 화려 강산의
을숙도에서 일정한 군을 이루며
갈대 숲을 이륙하는 흰 새떼들이
자기들끼리 끼룩거리면서
자기들끼리 낄낄대면서
일렬 이열 삼렬 횡대로 자기들의 세상을
이 세상에서 떼어 메고
이 세상 밖 어디론가 날아간다
우리도 우리들끼리
낄낄대면서
깔쭉대면서
우리의 대열을 이루며
한 세상 떼어 메고
이 세상 밖 어디론가 날아갔으면
하는데 대한 사람 대한으로
길이 보전하세로
각각 자기 자리에 앉는다
주저앉는다"""
        hwp.insert_text(t2_c1)
        
        hwp.Run("TableRightCell")
        hwp.set_font(FaceName="맑은 고딕", Height=10, Bold=False)
        t2_c2 = """• 영화 상영 전 일제히 일어나 애국가 경청:
➡ 1980년대 군사 독재 시절의 획일적 이고 강압적인 시대 현실

• 자기들끼리 낄낄대면서 / 깔죽대면서:
➡ 강압적인 현실에 순응하는 모습을 비웃는 화자의 냉소적 이고 자조적인 태도

• 이 세상 밖 어디론가 날아간다:
➡억압적 현실에서 완전히 벗어난 자유로운 이상향의 공간

• 우리도 ... 날아갔으면 / 하는데:
➡ 새들처럼 억압적 현실에서 벗어나 자유로운 삶을 살고 싶은 강렬한 갈망 

• 각각 자기 자리에 앉는다 / 주저앉는다:
➡ 애국가가 끝나고 현실의 벽을 넘지 못하는 화자.
➡결국 억압에 순응할 수밖에 없는 소시민적 무력감과 체념, 좌절"""
        hwp.insert_text(t2_c2)
        
        hwp.Run("CloseEx")
        hwp.Run("MoveDocEnd")
        hwp.insert_text("\n\n")

        # --- 4. Section 3 ---
        hwp.set_font(FaceName="맑은 고딕", Height=14, Bold=True)
        hwp.insert_text("3. 종합 정리: 두 작품의 비교\n")
        
        hwp.create_table(4, 3)
        hwp.set_font(FaceName="맑은 고딕", Height=11, Bold=True)
        hwp.insert_text("비교 포인트")
        hwp.Run("TableRightCell")
        hwp.set_font(FaceName="맑은 고딕", Height=11, Bold=True)
        hwp.insert_text("최승호, 「대설주의보」")
        hwp.Run("TableRightCell")
        hwp.set_font(FaceName="맑은 고딕", Height=11, Bold=True)
        hwp.insert_text("황지우, 「새들도 세상을 뜨는구나」")
        
        hwp.Run("TableRightCell")
        hwp.set_font(FaceName="맑은 고딕", Height=10, Bold=False)
        hwp.insert_text("공통된 시대적 배경")
        hwp.Run("TableRightCell")
        hwp.insert_text("1980년대 군사 독재 정권의 억압적 현실")
        hwp.Run("TableRightCell")
        hwp.insert_text("1980년대 군사 독재 정권의 억압적 현실") # Replicated across columns for alignment
        
        hwp.Run("TableRightCell")
        hwp.insert_text("억압적 현실을 상징하는 소재")
        hwp.Run("TableRightCell")
        hwp.insert_text("생존을 위협받는 폭력적인 재난 상황인 폭설")
        hwp.Run("TableRightCell")
        hwp.insert_text("자유를 억압당하고 획일화된 일상생활 속 애국가")
        
        hwp.Run("TableRightCell")
        hwp.insert_text("암울한 현실에 대응하는 태도 및 결말")
        hwp.Run("TableRightCell")
        hwp.insert_text("숯불, 온기을 통해 끈질긴 생명력과 연대를 보여줌")
        hwp.Run("TableRightCell")
        hwp.insert_text("현실의 벽에 막혀 자리에 주저앉는 무력감과 좌절을 보여줌")
        
        hwp.Run("CloseEx")
        hwp.Run("MoveDocEnd")
        
        hwp.save_as(file_path)
        print(f"SUCCESS: HWP created at {file_path}")
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        hwp.quit()
        show_popup()

if __name__ == "__main__":
    build_worksheet()
