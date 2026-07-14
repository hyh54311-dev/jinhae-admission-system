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

MOCK_STUDENTS = [
    {
        "grade": 2, "ban": 1, "num": 15, "name": "서태랑",
        "career": "의학/보건", "work": "오발탄 (이범선)",
        "title": "『오발탄』 속 주인공 철호의 치통 분석을 통한 전후 한국의 의료 소외 실태와 현대 공공의료/지역간 의료 격차 개선 방안 탐구",
        "motivation": "문학 수업 시간 중 주인공 철호가 극심한 치통을 앓으면서도 치료비가 없어 방치하는 장면을 배웠습니다. 이를 통해 사회 안전망의 부재가 개인의 육체적·정신적 파탄을 어떻게 유발하는지 의문을 품게 되어 탐구를 시작했습니다.",
        "content_literary": "소설 속 '치통'은 단순한 신체적 고통을 넘어 전후 서민들이 겪는 극심한 빈곤과 사회적 소외를 형상화한 은유적 장치입니다. 철호는 어머니의 실성, 여동생의 타락 등 가정의 붕괴 속에서 치통을 참으며 국가가 방치한 개인의 무기력함을 대변합니다.",
        "content_fusion": "이를 현대 보건의료학의 '사회적 질병 모델'과 결합하여 현대 한국의 의료 보장 제도 실태와 비교했습니다. 통계 자료에 따르면 도서·산간 지역의 필수의료 상실률이 매우 높으며, 공공 의료 강화가 단순 복지를 넘어 인권의 기본임을 역설했습니다.",
        "process": "김승섭 저 『아픔이 길이 되려면』을 읽고 사회적 상처가 신체적 고통으로 전환되는 생리학적 경로를 연구했으며, RISS 논문 「한국전쟁기 보건의료체계의 한계」를 분석해 역사적 맥락을 보완했습니다.",
        "conclusion": "질병 치료를 세포 수준에 국한하지 않고, 사회적 사각지대까지 살피는 공공의료 전문가로서의 소명 의식을 기르는 계기가 되었습니다."
    },
    {
        "grade": 2, "ban": 2, "num": 20, "name": "유승준",
        "career": "컴퓨터공학/AI", "work": "대설주의보 (최승호)",
        "title": "「대설주의보」의 '백색 계엄령' 은유를 바탕으로 본 현대 빅데이터/AI 감시 사회의 통제 메커니즘과 윤리적 기술 제어 방안 분석",
        "motivation": "대설주의보 시 구절 중 도시를 고립시키고 소통을 차단하는 폭설이 '백색 계엄령'으로 비유되는 것을 배웠습니다. 현대 정보통신 사회에서 보이지 않는 알고리즘이 개인의 정보와 생각을 통제하는 방식과 유사하다고 느껴 공학적 호기심이 생겼습니다.",
        "content_literary": "시에서 '폭설'은 도시의 모든 움직임을 정지시키고 군인처럼 세상을 지배하는 억압적 권력을 상징합니다. 이는 자유로운 의사소통과 개별성을 차단하는 독재 정권의 물리적 폭력을 백색의 이미지로 고도의 은유를 통해 비판한 것입니다.",
        "content_fusion": "이 통제 모델을 현대 정보기술의 '디지털 판옵티콘' 및 데이터 필터 버블 현상과 비교했습니다. 인공지능이 제공하는 맞춤형 정보가 개인의 무의식을 지배하는 감시 체계와 대조하여, 알고리즘 편향성을 제어하는 예방적 윤리 모형의 당위성을 도출했습니다.",
        "process": "미셸 푸코의 『감시와 처벌』을 탐독하며 규율 사회의 통제 원리를 분석했고, IEEE의 '인공지능 윤리 가이드라인' 문헌을 찾아 공학도로서의 기술 투명성 설계 과제를 리서치했습니다.",
        "conclusion": "코드 한 줄의 편향이 사회적 폭설이 될 수 있음을 성찰하며, 기술 개발 시 인권과 사생활 침해를 최우선으로 고려하는 인공지능 엔지니어가 되기로 결심했습니다."
    },
    {
        "grade": 2, "ban": 3, "num": 29, "name": "최재민",
        "career": "경영/경제", "work": "원미동 사람들 (양귀자)",
        "title": "『원미동 사람들』 속 소시민의 갈등을 통해 본 현대 골목상권 침해 문제와 상생 경제 모델 분석",
        "motivation": "소설 '일용할 양식'에서 김포슈퍼와 형제슈퍼가 과도한 경쟁을 벌이다 결국 대형 점포인 동네 랜드에 밀려 몰락하는 경제적 인과관계를 배우고, 현대 골목상권의 자영업 생존 전략과 연결하고자 탐구했습니다.",
        "content_literary": "작가는 원미동이라는 좁은 공간을 무대로 서민들끼리 벌이는 생존 경쟁의 비극을 리얼리즘 기법으로 조명합니다. 서로 돕던 이웃들이 이윤 추구를 위해 가차 없이 갈등하는 모습은 자본주의의 비정함과 인간성 상실을 예리하게 드러냅니다.",
        "content_fusion": "소설 속 슈퍼마켓 갈등을 현대 유통 대기업의 골목상권 침해 사례 및 독점 규제법과 매칭했습니다. 소상공인 생존을 위해 대형 유통업 의무휴업일 지정 제도 등 상생 협력의 실질적인 유효성을 게임이론적 관점으로 분석했습니다.",
        "process": "행동경제학 관련 도서인 『넛지』를 완독하며 소비자 심리를 이해하고, RISS에서 「대형 유통업체 진입이 골목상권에 미치는 영향」 논문을 검색하여 실증 데이터를 보완했습니다.",
        "conclusion": "이윤의 극대화만이 기업의 목적이 아니라, 소상공인과 동네 공동체의 상생 경제적 균형을 설계하는 미래 사회적 경영인으로서의 꿈을 확립했습니다."
    },
    {
        "grade": 2, "ban": 4, "num": 22, "name": "윤태웅",
        "career": "생태/환경", "work": "새들도 세상을 뜨는구나 (황지우)",
        "title": "「새들도 세상을 뜨는구나」의 자연 이미지와 현대 기후 변화 위기에 대한 생태학적 비평",
        "motivation": "자유롭게 날아가는 새들의 떼와 대조되어 애국가를 들으며 주저앉는 영화관 속 관객들의 대비를 학습하며, 환경 오염과 온난화로 서식지를 잃고 영원히 세상을 떠나는 멸종 위기종의 절박한 생태 환경 문제로 확장해 탐구하고자 했습니다.",
        "content_literary": "시에서 '새'는 억압적인 현실 세계를 탈출할 수 있는 자유의 생명적 표상입니다. 하지만 관객들은 어둠 속 자리에 앉아야 하는 현실의 한계를 보이며, 이는 생명력을 상실한 도시 문명과 그로 인해 질식당하는 자연 생태계를 생생하게 보여줍니다.",
        "content_fusion": "시의 억압 이미지를 기후 변화로 인한 지구 생태 한계선(Planetary Boundaries) 도달 현상에 대입했습니다. 생태학적 다양성이 파괴되는 속도를 경고하며, 파리기후협약의 탄소 감축 의무 이행 과제와 연계해 환경 인권 수호 의무를 역설했습니다.",
        "process": "레이첼 카슨의 『침묵의 봄』을 읽고 화학 물질과 지구 온난화가 생물종 소멸에 미치는 유기적 영향을 파악했으며, RISS 논문 「기후변화와 생물다양성 보전 대책」을 분석했습니다.",
        "conclusion": "문학을 통해 지구 생태계의 절규를 읽어냈으며, 앞으로 환경 정책과 생태 복원을 주도하는 생태 공학 연구원으로서 학업적 성장을 얻었습니다."
    },
    {
        "grade": 2, "ban": 5, "num": 8, "name": "박관우",
        "career": "심리학", "work": "광장 (최인훈)",
        "title": "『광장』 속 이명준의 심리 분석을 통한 현대인의 정체성 혼란과 사회적 고립 극복 방안",
        "motivation": "이명준이 밀실만 존재하고 광장은 없는 남한, 광장만 존재하고 밀실은 없는 북한 사이에서 번민하다가 중립국을 선택하고 투신하는 결말을 배우며, 그가 겪은 심리적 해리 상태와 고립감이 현대 청년들의 사회적 위축 현상과 닿아 있다고 생각하여 탐구했습니다.",
        "content_literary": "이명준의 바다 투신은 현실적 절망의 극단적 발현인 동시에, 진정한 자아를 지키기 위한 역설적 선택입니다. 남북 어디에서도 주체적인 인간으로 존재하지 못했던 심리적 외상(PTSD)과 실존적 불안이 결합한 비극적 상태임을 도출했습니다.",
        "content_fusion": "이명준의 고립 심리를 임상심리학의 '관계적 위축' 및 '실존주의 심리학의 정체성 확립' 모델에 대입했습니다. 현대 1인 가구 증가와 SNS 속 과시적 소통 이면에 감춰진 내면적 군중 속 고독 현상을 예방하기 위한 심리 치유 공동체 구축 방안을 제안했습니다.",
        "process": "에리히 프롬의 『자유로부터의 도피』를 읽고 전체주의와 자본주의 사회에서 개인이 겪는 고독의 심리학적 기제를 추적했으며, 청소년 상담학 논문을 분석해 방안을 구체화했습니다.",
        "conclusion": "사회적 제도 설계만큼이나 개인의 실존적 불안을 치유하는 일이 중요함을 자각하고, 마음의 병을 보듬는 심리치료 전문가로서 성장하고자 하는 다짐을 굳혔습니다."
    },
    {
        "grade": 2, "ban": 6, "num": 15, "name": "여진우",
        "career": "법학/인권", "work": "아홉 켤레의 구두로 남은 사내 (윤흥길)",
        "title": "『아홉 켤레의 구두로 남은 사내』를 통해 본 도시 빈민의 주거권 실태와 인권적 관점의 개선 과제",
        "motivation": "광주대단지 사건을 배경으로 철거민인 주인공 권 씨가 집을 마련하기 위해 처절하게 몸부림치다 결국 강도로 돌변하는 파탄 장면을 보고, 헌법에 보장된 주거권과 생존권이 현실 법망에서 어떻게 작동하고 괴리되는지 탐구하고 싶었습니다.",
        "content_literary": "권 씨가 집착하는 '아홉 켤레의 구두'는 도시 빈민으로 전락했으나 포기할 수 없는 지식인으로서의 마지막 자존심입니다. 주택 분양금을 감당하지 못해 범죄자가 되는 인물의 붕괴를 통해, 소외 계층의 기본권 박탈 과정을 객관적 서술로 폭로합니다.",
        "content_fusion": "소설 속 강제 이주 상황을 현대 주거 기본법 및 UN 세계인권선언 제25조(적절한 주거 기준)와 비교 분석했습니다. 재개발 과정에서 원주민 정착률이 20% 미만으로 떨어지는 젠트리피케이션 현상과 이에 대처하는 현행 토지보상법의 보완점을 법학적으로 짚어보았습니다.",
        "process": "도서 『난장이가 쏘아올린 작은 공』을 읽고 소외 계층의 주거권 문제를 연계 이해했으며, RISS에서 「도시재개발 사업에서의 세입자 주거권 보장에 관한 연구」 논문을 고찰했습니다.",
        "conclusion": "법은 사회적 약자를 보호하는 울타리여야 함을 절감하고, 향후 소외된 이웃의 주거 환경 개선과 기본권 옹호를 이끄는 공익 전문 법조인으로 성장할 토대를 쌓았습니다."
    },
    {
        "grade": 2, "ban": 7, "num": 26, "name": "조현민",
        "career": "언론/미디어", "work": "태평천하 (채만식)",
        "title": "『태평천하』의 풍자 기법과 현대 뉴미디어 시대의 가짜 뉴스 및 사회 풍자 저널리즘 비교 분석",
        "motivation": "윤 직원 영감이 일제강점기 가혹한 수탈의 현장을 두고 '태평천하'라고 찬양하는 반어적 결말을 학습했습니다. 이 모순적 상황 인식을 보면서, 사실을 왜곡 전달하는 현대 미디어의 프레이밍 효과와 풍자 뉴스의 사회적 역할을 연구하고자 시작했습니다.",
        "content_literary": "채만식은 서술자의 독특한 판소리 어조와 경어체를 사용해 윤 직원의 탐욕과 역사적 무지를 반어법적으로 풍자합니다. 윤 직원이 외치는 '태평천하'는 일제의 폭력과 억압 위에 쌓아 올린 가짜 평화이자 역사의식의 실종을 극적으로 대변합니다.",
        "content_fusion": "윤 직원의 태평천하 발언을 언론정보학의 '미디어 프레이밍(Framing)' 효과 및 현대 알고리즘 추천으로 인한 가짜 뉴스 정보 편향과 매칭했습니다. 사실 왜곡 보도에 대응하는 팩트체크 시스템과 사회적 대안 언론의 풍자 저널리즘 순기능을 분석했습니다.",
        "process": "닐 포스트만의 『죽도록 즐기기』를 읽으며 미디어 오락화가 대중의 비판적 인식을 어떻게 무디게 하는지 분석했고, RISS에서 풍자 저널리즘의 신뢰성에 관한 학술 논문을 읽었습니다.",
        "conclusion": "미디어의 겉포장 속 왜곡된 실체를 감별해 내는 비판적 문학 독해력이 필수임을 자각하고, 정론 직필을 실현하는 참된 저널리스트로서의 자질을 함양했습니다."
    },
    {
        "grade": 2, "ban": 8, "num": 22, "name": "이지우",
        "career": "교육학", "work": "동백꽃 (김유정)",
        "title": "『동백꽃』 속 해학적 인물 관계를 활용한 현대 다문화/소통 지향적 국어 교육 프로그램 설계",
        "motivation": "주인공 '나'와 점순이 사이의 사춘기 갈등과 감정적 소통 부재가 빚어내는 해학적 요소를 배웠습니다. 언어 표현이 서투르고 신체적 갈등을 빚는 양상이 현대 다문화 가정 아동이나 소통 장애 청소년들의 인간관계 갈등과 일치함을 발견해 교육적 대안을 세우고자 연구했습니다.",
        "content_literary": "김유정은 토속적이고 비속적인 어조와 역설적이고 해학적인 표현으로 두 남녀의 갈등을 유쾌하게 연출합니다. 점순이의 닭싸움과 감자 전달은 애정 표현의 서툰 방식이며, 이를 인지하지 못하는 '나'의 어수룩함이 해학을 완성하는 심리적 축임을 규명했습니다.",
        "content_fusion": "두 인물의 불통과 해학적 화해를 교육 연극 이론 및 상호문화 교육 모델에 연계했습니다. 서로 다른 문화적 배경을 가진 청소년들이 상대방의 서툰 행동 뒤에 숨겨진 감정을 연극 활동을 통해 발견하고 포용하는 교과 융합형 국어 수업 모형을 구상했습니다.",
        "process": "도서 『소통의 심리학』을 탐독하고, 다문화 국어 교육 연구 논문인 「서사 텍스트를 활용한 상호문화 역량 강화 방안」을 분석하여 교육 설계서의 학술적 타당성을 기했습니다.",
        "conclusion": "문학 교육이 갈등을 봉합하는 감성적 매개체임을 깨달았으며, 모든 학생이 소외받지 않고 존중받는 다문화 및 소통 지향적 국어 교사로서의 구체적 꿈을 가꾸게 되었습니다."
    },
    {
        "grade": 2, "ban": 9, "num": 13, "name": "안도윤",
        "career": "생명공학", "work": "춘향전 (작자 미상)",
        "title": "『춘향전』 속 춘향의 절개 은유를 바탕으로 생명 다양성 보존을 위한 윤리적 관점의 성찰",
        "motivation": "춘향이 변사또의 수청 요구를 거부하고 형틀 속에서도 매화와 대나무의 지조를 다짐하는 판소리 대목을 배웠습니다. 한 생명체가 급변하는 외적 압력 속에서 고유한 성질을 지키는 절개(지조)의 정서를 생태계 생물다양성 유지와 연계해 과학 윤리적 관점으로 탐구했습니다.",
        "content_literary": "춘향의 '수청 거부'와 지조는 유교적 신분 질서를 거스르고 인간 존엄성을 지키는 생명력 넘치는 주체적 저항입니다. 춘향이 감옥에서 읊는 시어 속 대나무와 매화는 자연 법칙처럼 꺾이지 않는 생명적 절대성의 상징임을 문학적으로 분석했습니다.",
        "content_fusion": "춘향의 외압 극복과 지조를 현대 유전공학의 특허 독점과 생태적 다양성 파괴(단일 작물 재배로 인한 생태 붕괴 위기) 현상에 대입했습니다. 자연의 고유한 생태 균형을 훼손하지 않는 범위 내에서 유전자 기술을 통제해야 한다는 생명 윤리 선언의 당위성을 입증했습니다.",
        "process": "도서 『생명의 윤리를 말하다』(마이클 샌델 저)를 정독하며 인간의 생명 개입 한계를 고민했고, RISS 학술 논문 「유전자 조작 식물 유입에 따른 생태계 영향 평가」를 검토했습니다.",
        "conclusion": "생명은 인위적인 이윤의 잣대로 통제할 수 없는 신성한 영역임을 성찰하고, 생태 가치를 지키며 인류에 기여하는 생명 윤리 연구자로서의 꿈을 선언했습니다."
    },
    {
        "grade": 2, "ban": 10, "num": 29, "name": "홍정훈",
        "career": "역사/사회", "work": "진달래꽃 (김소월)",
        "title": "「진달래꽃」의 전통적 한(恨)의 정서와 일제강점기 저항 의식의 역사사회학적 비평",
        "motivation": "진달래꽃에서 임을 보내는 슬픔을 억누르며 '사뿐히 즈려밟고 가시옵소서'라고 축원하는 이별의 정한을 학습했습니다. 슬픔을 극복하고 꽃을 뿌리는 행위에 내재된 초극의 정서가 일제강점기 가혹한 민족적 수탈을 이겨내고자 했던 민중의 역사적 의지와 닿아 있음을 탐색하고자 시작했습니다.",
        "content_literary": "시에서 '진달래꽃'은 임에 대한 헌신적 사랑을 대변하는 붉은 피의 상징물이자, 이별의 슬픔을 꽃을 즈려밟는 가학적 행위를 통해 극복하는 반어적 매개체입니다. 떠나려는 대상에게 오히려 꽃길을 깔아주는 극단적 애도와 이별의 초월 정서를 분석해 냈습니다.",
        "content_fusion": "정한의 극복 구조를 일제강점기 동양척식주식회사의 토지 약탈 및 민중 저항 운동 역사에 대입했습니다. 당시 서민들이 가혹한 지주 수탈 속에서도 소작 쟁의나 민족 학교 설립을 통해 희망을 발현했던 역사적 사실들과 시의 슬픔 초극 정서를 연결 지었습니다.",
        "process": "신채호의 『조선상고사』와 도서 『역사란 무엇인가』(E.H. 카)를 탐독하여 역사를 바라보는 주체적 비평안을 길렀으며, RISS에서 일제강점기 민족 저항 문학에 관한 역사 논문을 찾아 고찰했습니다.",
        "conclusion": "민족적 고통을 미학적으로 정화해 낸 문학의 저력을 깨달았으며, 과거의 아픔을 넘어 정의로운 민주 공동체를 구현해 나가는 역사학자로서의 학업 포부를 정립했습니다."
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
        # API 빌드
        docs_service = build("docs", "v1", credentials=creds)
        drive_service = build("drive", "v3", credentials=creds)
        sheets_service = build("sheets", "v4", credentials=creds)

        print(f"Start creating {len(MOCK_STUDENTS)} mock submissions in Google Drive and Sheet...")
        
        for idx, student in enumerate(MOCK_STUDENTS):
            print(f"\n[{idx+1}/10] Submitting for {student['ban']}반 {student['num']}번 {student['name']}...")
            
            # 1. 문서 생성
            doc_name = f"[문학 심층보고서] {student['ban']}반_{student['num']}번_{student['name']}"
            doc = docs_service.documents().create(body={}).execute()
            doc_id = doc.get("documentId")
            
            # 2. 문서 서술부 레이아웃 구성
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
            
            # 3. 문서 스타일 적용 (글꼴 설정)
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

            # 4. 폴더 이동 및 보기 권한 설정
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
            
            # 5. 스프레드시트에 행 기록 (총 17개 열)
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
            
            print(f" -> Successfully submitted. Length: {total_text_length} chars. Doc URL: {doc_url}")
            
        print("\nAll 10 mock student submissions completed successfully!")

    except Exception as e:
        print("Error submitting mock reports:", e)

if __name__ == "__main__":
    main()
