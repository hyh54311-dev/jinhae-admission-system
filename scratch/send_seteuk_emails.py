import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "hyh54311@gmail.com"
SENDER_PASSWORD = "obpv abgy acyh evho"

RECEIVERS = [
    {"name": "강필성 선생님", "email": "space88120@hanmail.net"},
    {"name": "강지영 선생님", "email": "btkjyzang@gmail.com"}
]

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/10diJ7L5Z-mtwDsRndOYv4cGx_OZMsSmwxvZ_kndmF24/edit?gid=1456060935#gid=1456060935"

def send_seteuk_email(receiver_info):
    name = receiver_info["name"]
    target_email = receiver_info["email"]
    
    subject = f"[진해고 국어과] 2026학년도 2학년 문학 교과 심층 탐구 보고서 세특 초안 공유 및 안내"
    
    body = f"""안녕하세요, {name}. 국어과 황요한입니다.

2학년 학생들이 제출한 '문학 교과 심층 탐구 보고서' 내용 및 제출 자료를 바탕으로 재정리한 2학년 문학 세특 초안 구글 스프레드시트 작업을 완료하여 안내해 드립니다.

이번 세특 초안은 학생들의 입력 자료와 첨부 파일을 종합하여 2022 개정 국어과 교육과정 성취기준 및 생기부 기재 지침에 맞게 5단계 유기적 구조로 다듬은 내용입니다. 아래 공유해 드리는 링크를 참고하시어 담당 학반 학생들의 세특 최종 기입 및 수정 검토를 진행해 주시면 감사하겠습니다.

----------------------------------------------------------------------
📌 1. 연동 구글 스프레드시트 링크 및 탭 구성
- 구글 시트 주소: {SPREADSHEET_URL}
- 탭 구성: 1~3반 탭 / 4~6반 탭 / 7~10반 탭
- 열 구성: A~C열(반, 번호, 이름), D열(세특 초안), E열(NEIS 바이트 수), F열(글자 수)

💡 2. 세특 초안 작성 시 주요 반영 규칙 및 참고 사항
1) 활동 명칭 통일: 모든 세특의 첫 문장은 "문학 교과 심층 탐구 활동에서..."로 통일하여 작성되었습니다.
2) 진로 연계 구분 적용: 
   - 인문/문학 관련 진로 학생: 희망 진로 및 전공과의 연계성을 잘 살려 작성되었습니다.
   - 문학 비관련 진로 학생(수학, 과학, 의학, 공학, 예체능 등): 억지스러운 진로 연결을 배제하고 2022 개정 문학 교육과정 핵심 역량(비평적 사고력, 심미적 감성, 주체적 해석, 인문학적 성찰) 중심으로 깊이 있게 기재하였습니다.
3) 5단계 유기적 단락 구조 적용: (동기&작품선정 -> 작품분석&탐구질문 -> 현대사회/인문/진로연계 -> 심화독서/논문탐구 -> 결론&성찰/후속확장)
4) 기재 금지 부호 및 언어 규격 정제:
   - 꺽쇠 표시(『 』, 《 》, < >) 및 큰따옴표 금지 -> 한글식 둥근 작은 따옴표(‘ ’)로 정제
   - 영문/알파벳 표기 배제 -> (PTSD), (AI) 대신 '상처 후 스트레스 장애', '인공지능' 등 순수 한글 표기로 대체
   - '진해', '장복', '대회' 등 생기부 금지어 완전 정제 조치
5) 국어 교과부장 학생 (10명): 전면에 143Byte 공통 문구가 반영되어 있으며, 전체 바이트 수(NEIS 1,100~1,250 Bytes / 500자 이내)에 맞춰 안정적으로 수록되어 있습니다.
----------------------------------------------------------------------

시트를 확인해 보시면서 학생별 특성이 더 잘 드러나도록 수정을 원하시는 부분은 자율적으로 변경하여 NEIS에 기입해 주시면 됩니다.

혹시 시트 접근 권한이나 내용 검토 중 문의 사항이 있으시면 언제든지 말씀해 주십시오.

늘 애써주셔서 감사드립니다.

황요한 드림
"""

    msg = MIMEMultipart()
    msg['From'] = f"황요한 <{SENDER_EMAIL}>"
    msg['To'] = f"{name} <{target_email}>"
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [target_email], msg.as_string())
        server.quit()
        print(f"✅ {name} ({target_email}) 님께 성공적으로 메일을 발송했습니다.")
        return True
    except Exception as e:
        print(f"❌ {name} ({target_email}) 메일 발송 실패: {e}")
        return False

def main():
    print("=== 강필성 선생님, 강지영 선생님 2학년 문학 세특 안내 메일 발송 시작 ===")
    for receiver in RECEIVERS:
        send_seteuk_email(receiver)

if __name__ == "__main__":
    main()
