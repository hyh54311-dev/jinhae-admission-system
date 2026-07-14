import os
import sys
import io
import datetime
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

TOKEN_FILE = "token.json"
SPREADSHEET_ID = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
FOLDER_ID = "10-JmLFHo0Rh2aFxHCCeFoalEalgtt0D2"

# 250자 규격에 맞춰 축약한 10명의 가상 학생 데이터
MOCK_STUDENTS_250 = [
    {
        "grade": 2, "ban": 1, "num": 15, "name": "서태랑",
        "career": "의학/보건", "work": "오발탄 (이범선)",
        "title": "『오발탄』 속 주인공 철호의 치통 분석을 통한 전후 한국의 의료 소외 실태와 현대 공공의료/지역간 의료 격차 개선 방안 탐구",
        "motivation": "문학 수업 시간 중 철호가 극심한 치통을 앓으면서도 치료비가 없어 방치하는 장면을 보고 사회 안전망 부재와 개인의 파탄에 깊은 질문을 품게 됨.",
        "content_literary": "작품 속 치통이 서민들이 겪는 경제적 빈곤과 사회적 소외의 문학적 은유임을 해석하고 ‘사회적 질병은 공공의료망으로 해결 가능한가?’라는 탐구 질문을 구성함.",
        "content_fusion": "화자의 신체적 고통을 현대 의료 취약 지역의 필수 진료 접근성 상실 현상에 대입하여 고전과 현대의 공통점을 도출함.",
        "process": "도서 ‘아픔이 길이 되려면’을 분석하여 빈곤이 만성 질환으로 이어지는 기제에 대한 비평적 논리를 보완함.",
        "conclusion": "질병 치료가 개인의 차원을 넘어 국가 보건 정책의 책임이라는 결론을 제시하며, 의료 소외 지대를 살피는 공공의료 전문가로서의 소명 의식을 기름."
    },
    {
        "grade": 2, "ban": 2, "num": 20, "name": "유승준",
        "career": "컴퓨터공학/AI", "work": "대설주의보 (최승호)",
        "title": "「대설주의보」의 '백색 계엄령' 은유를 바탕으로 본 현대 빅데이터/AI 감시 사회의 통제 메커니즘과 윤리적 기술 제어 방안 분석",
        "motivation": "도시를 통제하는 폭설이 '백색 계엄령'으로 비유되는 것을 보며 보이지 않는 알고리즘이 개인의 자유를 억압하는 구조와 유사함을 포착하고 탐구함.",
        "content_literary": "폭설이 자유를 통제하는 백색 권력의 은유임을 분석하고 ‘AI의 빅데이터 감시는 현대판 백색 계엄령으로 기능하는가?’라는 질문을 지님.",
        "content_fusion": "화자의 통제 환경을 현대 IT 사회의 알고리즘적 감시 모델인 디지털 판옵티콘에 빗대어 공통점을 도출함.",
        "process": "미셸 푸코의 ‘감시와 처벌’을 분석해 규율 사회의 통제 메커니즘을 추적하며 비평 논리를 설계함.",
        "conclusion": "알고리즘 통제가 투명성과 인공지능 윤리 가이드라인으로 제어되어야 한다는 공학자적 소신을 도출하며 기술 윤리의 필요성을 자각함."
    },
    {
        "grade": 2, "ban": 3, "num": 29, "name": "최재민",
        "career": "경영/경제", "work": "원미동 사람들 (양귀자)",
        "title": "『원미동 사람들』 속 소시민의 갈등을 통해 본 현대 골목상권 침해 문제와 상생 경제 모델 분석",
        "motivation": "김포슈퍼와 형제슈퍼의 과도한 경쟁이 대형 점포의 침입으로 상호 몰락하는 소설 속 경제적 인과관계에 흥미를 느끼고 탐구함.",
        "content_literary": "소시민들끼리의 출혈경쟁이 자본주의적 공멸의 은유임을 분석하고 ‘골목상권 갈등은 상생 경제 모델로 해결 가능한가?’라는 질문을 세움.",
        "content_fusion": "소설 속 동네 슈퍼 갈등을 현대 대기업의 소상공인 골목상권 침해 통계에 대조해 공통점을 분석함.",
        "process": "행동경제학 도서 ‘넛지’를 완독하여 소비자 심리 메커니즘과 상생 규제의 타당성을 검토해 보완함.",
        "conclusion": "기업의 이윤 추구를 넘어 자영업자와 지역 공동체가 협력하는 상생적 경제 제도 설계가 필요하다는 공동체적 경영 소신을 정립함."
    },
    {
        "grade": 2, "ban": 4, "num": 22, "name": "윤태웅",
        "career": "생태/환경", "work": "새들도 세상을 뜨는구나 (황지우)",
        "title": "「새들도 세상을 뜨는구나」의 자연 이미지와 현대 기후 변화 위기에 대한 생태학적 비평",
        "motivation": "자유롭게 떠나는 새들과 억압된 관객의 대비를 배우고, 기후 변화 위기로 서식지를 잃고 멸종되는 생태 위기와 연계해 탐구함.",
        "content_literary": "새의 이미지를 현실 탈출의 자유로 분석하고 ‘인간의 생태계 침해는 지구 생명선을 언제까지 위협할 수 있는가?’라는 질문을 던짐.",
        "content_fusion": "화자의 억압 상황을 현대 온난화로 인한 생태 다양성 파괴 속도와 탄소 감축 의무에 빗대어 공통점을 분석함.",
        "process": "생태 고전인 ‘침묵의 봄’을 읽고 화학 오염이 생태 피라미드 붕괴에 미치는 인과관계를 고찰함.",
        "conclusion": "지구 서식지 붕괴를 경고하는 환경 보호 파수꾼의 소명을 깨닫고, 멸종 위기 생물다양성 보전에 헌신할 학업적 성장을 얻음."
    },
    {
        "grade": 2, "ban": 5, "num": 8, "name": "박관우",
        "career": "심리학", "work": "광장 (최인훈)",
        "title": "『광장』 속 이명준의 심리 분석을 통한 현대인의 정체성 혼란과 사회적 고립 극복 방안",
        "motivation": "광장과 밀실의 불균형 속에서 중립국을 택해 투신하는 이명준의 정신적 한계가 현대인의 고독과 유사하다고 느껴 심리학적으로 탐구함.",
        "content_literary": "주인공의 투신이 자아 수호의 실존적 선택임을 도출하고 ‘소속을 상실한 인간의 실존적 불안은 어떻게 극복 가능한가?’라는 질문을 구성함.",
        "content_fusion": "이명준의 고립감을 현대 청년층의 관계적 위축 및 1인 가구 소외 정서에 빗대어 공통점을 도출함.",
        "process": "에리히 프롬의 ‘자유로부터의 도피’를 읽고 전체주의 속 심리적 해리 정체성을 비평적으로 분석함.",
        "conclusion": "사회적 안전망 구축만큼이나 개인의 자아 정체성 치유가 중요함을 자각하고 따뜻한 심리치료사가 되겠다는 포부를 기름."
    },
    {
        "grade": 2, "ban": 6, "num": 15, "name": "여진우",
        "career": "법학/인권", "work": "아홉 켤레의 구두로 남은 사내 (윤흥길)",
        "title": "『아홉 켤레의 구두로 남은 사내』를 통해 본 도시 빈민의 주거권 실태와 인권적 관점의 개선 과제",
        "motivation": "철거민 권 씨가 최소한의 생존을 위해 대항하다 범죄를 저지르는 파탄 과정을 법에 보장된 주거권의 실제 한계와 연결해 분석함.",
        "content_literary": "구두의 은유가 무너진 가장의 마지막 자존심임을 분석하고 ‘도시 재개발 원주민의 주거권 박탈은 적법한 처사인가?’라는 질문을 구성함.",
        "content_fusion": "소설 속 이주 갈등을 현대 헌법상 주거 기본권 및 토지보상법의 원주민 재정착률 통계에 대조해 한계를 분석함.",
        "process": "소외 계층의 기본권 옹호 논문 「도시개발과 주거권 보장」을 정독하고 비평적 타당성을 기함.",
        "conclusion": "법은 사회적 약자의 생존을 보장하는 최후의 울타리여야 함을 깨닫고, 기본권 침해에 대항하는 공익 법조인의 진로를 다짐함."
    },
    {
        "grade": 2, "ban": 7, "num": 26, "name": "조현민",
        "career": "언론/미디어", "work": "태평천하 (채만식)",
        "title": "『태평천하』의 풍자 기법과 현대 뉴미디어 시대의 가짜 뉴스 및 사회 풍자 저널리즘 비교 분석",
        "motivation": "일제 침략 상황을 태평천하라 비아냥거리는 윤 직원의 이중성을 배우고 현대 언론의 사실 왜곡 전달과 비교하고자 탐구함.",
        "content_literary": "서술자의 반어적 어조가 역사관 부재를 조롱하는 은유임을 분석하고 ‘모순된 미디어 정보는 대중을 어떻게 현혹하는가?’라는 질문을 던짐.",
        "content_fusion": "반어적 태평천하 주장을 현대 미디어 프레이밍 효과와 필터 버블의 정보 왜곡 현상에 빗대어 분석함.",
        "process": "도서 ‘죽도록 즐기기’를 정독해 언론의 오락화와 사실 프레이밍 기술의 비판적 분석을 보완함.",
        "conclusion": "정보의 포장 속 왜곡된 진실을 가려내는 안목의 중요성을 깨닫고, 팩트를 밝혀내는 공정한 미디어 저널리스트로서 성장을 다짐함."
    },
    {
        "grade": 2, "ban": 8, "num": 22, "name": "이지우",
        "career": "교육학", "work": "동백꽃 (김유정)",
        "title": "『동백꽃』 속 해학적 인물 관계를 활용한 현대 다문화/소통 지향적 국어 교육 프로그램 설계",
        "motivation": "나와 점순이 사이의 사춘기 애증 갈등이 소통 불통에서 기인함을 포착하고, 청소년 소통 갈등 대안 교육으로 연결하고자 탐구함.",
        "content_literary": "점순이의 닭싸움이 표현의 미숙함과 엇갈린 소통의 은유임을 분석하고 ‘불통 갈등은 교감 프로그램으로 치료 가능한가?’라는 질문을 세움.",
        "content_fusion": "두 인물의 소통 부재를 현대 상호문화 교육 모델과 다문화 소외 청소년 소통 갈등 사례에 연계해 공통점을 도출함.",
        "process": "교과 융합 논문 「서사 텍스트를 활용한 문화 교류 방안」을 연구하여 교육 모형의 타당성을 보완함.",
        "conclusion": "문학 교육이 갈등을 매개하는 해학적 치유 도구임을 깨닫고 소통을 이끄는 포용적 교육 전문가로서의 포부를 다짐함."
    },
    {
        "grade": 2, "ban": 9, "num": 13, "name": "안도윤",
        "career": "생명공학", "work": "춘향전 (작자 미상)",
        "title": "『춘향전』 속 춘향의 절개 은유를 바탕으로 생명 다양성 보존을 위한 윤리적 관점의 성찰",
        "motivation": "변사또의 압력에도 굴하지 않고 매화와 대나무의 지조를 다짐하는 판소리 속에서 생명체의 고유 형질 보호와 연결해 탐구함.",
        "content_literary": "수청 거부가 유전적 다양성처럼 외부 환경 압박에 저항하는 독자성임을 해석하고 ‘생명 유전자 변형의 적정선은 어디인가?’라는 질문을 던짐.",
        "content_fusion": "춘향의 극복 의지를 현대 독점 다국적 종자 회사의 유전자 특허 남용과 생태계 단일화 위험에 대조해 분석함.",
        "process": "마이클 샌델의 ‘생명의 윤리를 말하다’를 읽고 유전자 개입에 따른 인간 자만의 한계를 성찰함.",
        "conclusion": "생명은 인위적으로 훼손해서는 안 되는 절대 영역임을 자각하고 인류와 자연 상생에 이바지하는 생명 윤리 연구가를 지향함."
    },
    {
        "grade": 2, "ban": 10, "num": 29, "name": "홍정훈",
        "career": "역사/사회", "work": "진달래꽃 (김소월)",
        "title": "「진달래꽃」의 전통적 한(恨)의 정서와 일제강점기 저항 의식의 역사사회학적 비평",
        "motivation": "슬픔을 억누르며 꽃을 즈려밟고 가라는 정한의 극복 정서가 일제강점기 민족 수탈을 극복하는 역사적 민중의 의지와 연계됨을 탐구함.",
        "content_literary": "꽃길을 깔아주는 반어적 행위가 이별의 슬픔을 의지로 승화하는 것임을 비평하고 ‘비극적 민족사는 문학으로 초극 가능한가?’라는 질문을 던짐.",
        "content_fusion": "슬픔의 정한을 일제강점기 민중 소작 쟁의와 역사적 극복 노력의 사실에 빗대어 공통점을 도출함.",
        "process": "신채호의 ‘조선상고사’를 탐독하여 역사의 주체적 비평 시각과 문학적 한의 정서를 역사학적으로 분석함.",
        "conclusion": "민족적 아픔을 예술로 정화한 문학의 저력을 깨닫고 아픈 과거를 보듬어 희망의 민주 역사를 만드는 사학자를 꿈꿈."
    }
]

def get_credentials():
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                session = requests.Session()
                session.verify = False
                creds.refresh(Request(session=session))
                return creds
        except Exception as e:
            print("Error loading credentials:", e)
    return None

def main():
    creds = get_credentials()
    if not creds:
        print("No Google credentials found.")
        return

    try:
        sheets_service = build("sheets", "v4", credentials=creds)
        docs_service = build("docs", "v1", credentials=creds)
        drive_service = build("drive", "v3", credentials=creds)

        # 1. 기존 데이터 초기화 (2행부터 삭제하여 시트 초기화)
        print("Clearing old mock rows in spreadsheet...")
        sheets_service.spreadsheets().values().clear(
            spreadsheetId=SPREADSHEET_ID,
            range="탐구보고서_응답!A2:Q100"
        ).execute()

        print(f"Start creating 10 condensed mock submissions (~250 chars) in Drive and Sheet...")
        
        for idx, student in enumerate(MOCK_STUDENTS_250):
            print(f"[{idx+1}/10] Submitting for {student['ban']}반 {student['num']}번 {student['name']}...")
            
            # 구글 문서 생성
            doc_name = f"[문학 심층보고서] {student['ban']}반_{student['num']}번_{student['name']}"
            doc = docs_service.documents().create(body={}).execute()
            doc_id = doc.get("documentId")
            
            # 본문 채우기
            title_p = "문학 교과 심층 탐구 보고서\n"
            hakbun_p = f"학생 정보: {student['grade']}학년 {student['ban']}반 {student['num']}번 | 이름: {student['name']} | 진로: {student['career']}\n\n"
            body_p = (
                f"■ 탐구 주제\n{student['title']}\n\n"
                f"■ 대상 작품 및 저자\n{student['work']}\n\n"
                f"1. 탐구 동기 (수업 연계성)\n{student['motivation']}\n\n"
                f"2-1. 작품 속 탐구 장면/시어의 문학적 분석\n{student['content_literary']}\n\n"
                f"2-2. 희망 진로 학문 및 현대 사회 사례 연계 분석\n{student['content_fusion']}\n\n"
                f"3. 탐구 과정 및 심화 노력 (도서/논문 등 독서 성과)\n{student['process']}\n\n"
                f"4. 결론 및 느낀 점 (인식의 변화와 학업적 성장)\n{student['conclusion']}\n"
            )
            
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={
                    "requests": [
                        {
                            "insertText": {
                                "location": {"index": 1},
                                "text": title_p + hakbun_p + body_p
                            }
                        }
                    ]
                }
            ).execute()
            
            # 맑은 고딕 적용
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={
                    "requests": [
                        {
                            "updateTextStyle": {
                                "range": {"startIndex": 1, "endIndex": len(title_p + hakbun_p + body_p)},
                                "textStyle": {
                                    "weightedFontFamily": {
                                        "fontFamily": "Malgun Gothic"
                                    }
                                },
                                "fields": "weightedFontFamily"
                            }
                        }
                    ]
                }
            ).execute()

            # 폴더 이동 및 보기 권한
            drive_service.files().update(
                fileId=doc_id,
                addParents=FOLDER_ID,
                removeParents="root",
                fields="id, parents"
            ).execute()
            
            drive_service.permissions().create(
                fileId=doc_id,
                body={"type": "anyone", "role": "reader"}
            ).execute()

            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            total_text_length = (
                len(student['motivation']) + 
                len(student['content_literary']) + 
                len(student['content_fusion']) + 
                len(student['process']) + 
                len(student['conclusion'])
            )
            
            # 스프레드시트 기입
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row_data = [
                timestamp, student['grade'], student['ban'], student['num'], student['name'],
                student['career'], student['work'], student['title'], student['motivation'],
                student['content_literary'], student['content_fusion'], student['process'], student['conclusion'],
                doc_url, "", total_text_length, "대기"
            ]
            
            sheets_service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range="탐구보고서_응답!A:Q",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [row_data]}
            ).execute()
            
        print("\nAll 10 mock student submissions re-created at ~250 chars successfully!")

    except Exception as e:
        print("Error re-submitting mock reports:", e)

if __name__ == "__main__":
    main()
