import win32com.client
import os

def create_hwp():
    hwp = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule") # 보안 모듈 등록 (필요시)
    
    # 바탕화면 경로
    desktop = r"D:\OneDrive - 경상남도교육청\바탕 화면"
    file_path = os.path.join(desktop, "대만 여행 계획.hwp")
    
    # 텍스트 내용
    content = """[대만 여행 계획 - 성인 남성 4인]

1. 일정: 2027년 1월 말 ~ 2월 초 (설 연휴 2/6~2/9 제외)
   - 최적 기간: 1월 25일(월) ~ 2월 3일(수) 사이

2. 항공권 예매 핵심 전략 (최저가 공략)
   - 골든 타임: 2026년 7월 ~ 8월 (LCC 동계 스케줄 오픈 시기)
   - 타겟 항공사: 에어부산(Fly & Sale), 제주항공(JJIM 특가)
   - 예약 전술:
     * 2+2 분할 예매: 최저가 좌석 확보를 위해 2명씩 나누어 결제
     * 가오슝 루트: 타이베이가 비쌀 경우 가오슝 입국(기차 이동) 고려
     * 수하물 전략: 4명 중 2명만 위탁 수하물 추가하여 비용 절감

3. 숙소 및 이동 추천
   - 추천 지역: 타이베이 시먼딩(Ximending) 또는 타이베이역 인근
   - 숙소 형태: 성인 남성 4인용 쿼드러플 룸 또는 아파트형 숙소(거실 있는 곳)
   - 현지 이동: 이지카드(EasyCard) 활용 및 4인 이동 시 택시/우버 적극 활용

4. 준비물 및 기타
   - 환전: GLN(모바일) 또는 WOWPASS 카드 활용
   - 알림 설정: 2026년 7월 1일 '항공권 스케줄 오픈 확인' 알림 예정

※ 이 내용은 2026년 4월 22일 기준으로 작성된 최적의 가이드입니다."""

    # HWP에 텍스트 쓰기
    hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
    hwp.HParameterSet.HInsertText.Text = content
    hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
    
    # 저장
    hwp.SaveAs(file_path)
    hwp.Quit()
    print(f"SUCCESS: Created {file_path}")

if __name__ == "__main__":
    create_hwp()
