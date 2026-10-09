import os
import sys
import argparse
from datetime import datetime, date
import requests

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# ----------------- 텔레그램 설정 ----------------- #
TELEGRAM_TOKEN = "8821847852:AAEpshxpceUmsJF8JHrDcwDvalW-9VaQ4ns"
TELEGRAM_CHAT_ID = "8518409134"

AUDIO_DIR = r"G:\내 드라이브\클로드"

# ----------------- 일차별 컨텐츠 정의 ----------------- #
CONTENT_MAP = {
    # 1. 2026-09-30 (수): Day 1
    "2026-09-30": {
        "type": "audio",
        "day": 1,
        "filename": "Day1_출퇴근영어라디오.mp3",
        "title": "Day 1: 반가운 재회 & 근황 확인",
        "performer": "Antigravity 출퇴근 영어 라디오 (20분)",
        "caption": "🚗 [Day 1] 출근길 차 안에서 귀로 배우는 20분 영어 라디오\n\n오늘의 핵심: be동사는 단순한 암기가 아니라 '동등 부호(=)'입니다!",
        "card": """🚗 [출퇴근 영어 라디오 — Day 1] 반가운 재회 & 근황 확인

좋은 아침입니다! 오늘부터 시작되는 5일간의 출퇴근 영어 여정, 1일차 방송을 배달해 드립니다.
오디오 파일을 재생하시고 운전하시면서 편안하게 소리 내어 따라 해보세요!

━━━━━━━━━━━━━━━━━━━━
📌 오늘의 핵심 표현 3개
1. What brings you here? (여기 웬일이야? / 뜻밖의 장소에서 마주쳤을 때)
2. Long time no see! (오랜만이야! / 반가운 재회)
3. I'm actually on my way to work. (나 사실 지금 출근하는 길이야)

💡 핵심 패턴 훈련
- I'm on my way to + 장소 (나 ~로 가는 길이야)
  * I'm on my way to work. (출근하는 길이야)
  * I'm on my way home. (퇴근하는 길이야)
- It's been so long since + 과거 (정말 오랜만이야)

🧠 뉘앙스 영문법: be동사는 등호(=)다!
- be동사는 '이다/있다'가 아니라 주어와 뒤를 연결하는 수학의 equality sign(=)입니다.
- I = happy (I am happy), He = a doctor (He is a doctor)
- I'm worry (X) ➔ I = worried (O, I'm worried)

오늘 출근길도 기분 좋게 완주하세요! 화이팅! 🎧"""
    },

    # 2. 2026-10-01 (목): Day 2
    "2026-10-01": {
        "type": "audio",
        "day": 2,
        "filename": "Day2_출퇴근영어라디오.mp3",
        "title": "Day 2: 약속 제안 & 정중한 거절",
        "performer": "Antigravity 출퇴근 영어 라디오 (21분)",
        "caption": "🚗 [Day 2] 출근길 차 안에서 귀로 배우는 21분 영어 라디오\n\n오늘의 핵심: 현재진행형은 실시간으로 돌아가는 '비디오 카메라'입니다!",
        "card": """🚗 [출퇴근 영어 라디오 — Day 2] 약속 제안 & 정중한 거절

좋은 아침입니다! 2일차 출퇴근 영어 라디오입니다.
오늘은 친구와의 약속을 부담 없이 제안하고, 곤란할 때 얼굴 붉히지 않고 정중하게 거절하는 원어민 황금 표현을 배웁니다.

━━━━━━━━━━━━━━━━━━━━
📌 오늘의 핵심 표현 3개
1. Are you free this Friday? Want to grab dinner? (이번 주 금요일에 시간 돼? 저녁 먹을래?)
2. I'd love to, but I'm tied up with work. (정말 그러고 싶은데, 일 때문에 꼼짝을 못 해)
3. Can I take a rain check? (다음에 하면 안 될까? / 정중한 다음 약속 기약)

💡 핵심 패턴 훈련
- Are you free + 시간? (너 ~에 시간 괜찮아?)
- I'd love to, but + 사유 (정말 그러고 싶은데 ~때문에 안 되겠어)

🧠 뉘앙스 영문법: 현재진행형은 라이브 비디오 카메라!
- 현재진행형(~ing)은 지금 이 순간 카메라 렌즈가 비추고 있는 생생한 동작입니다.
- be tied up (밧줄에 꽁꽁 묶인 듯 일에 얽매여 꼼짝달싹 못 하는 생생한 그림)
- 정중한 거절의 기술: 긍정적 의사 표현(I'd love to) + 사유(tied up) + 대안 제안(rain check)!

오늘도 안전 운전하시며 큰 소리로 따라 해보세요! 🎧"""
    },

    # 3. 2026-10-02 (금): Day 3
    "2026-10-02": {
        "type": "audio",
        "day": 3,
        "filename": "Day3_출퇴근영어라디오.mp3",
        "title": "Day 3: 카페 주문 & 일상 습관",
        "performer": "Antigravity 출퇴근 영어 라디오 (21분)",
        "caption": "🚗 [Day 3] 출근길 차 안에서 귀로 배우는 21분 영어 라디오\n\n오늘의 핵심: 단순현재는 지금이 아니라 늘 돌아가는 '시계태엽'입니다!",
        "card": """🚗 [출퇴근 영어 라디오 — Day 3] 카페 주문 & 일상 습관

불금 아침입니다! 3일차 방송을 배달해 드립니다.
오늘 출근길 카페에서 커피 주문할 때 바로 써먹을 수 있는 만능 회화와, 학창 시절 가장 큰 오해를 낳았던 단순현재의 진짜 감각을 마스터합니다.

━━━━━━━━━━━━━━━━━━━━
📌 오늘의 핵심 표현 3개
1. What do you usually get here? (여기서 보통 뭐 마셔? / 단골 메뉴 물어보기)
2. Can I get an iced vanilla latte, please? (아이스 바닐라 라떼 한 잔 주시겠어요? / 만능 주문 패턴)
3. I stop by every day before work. (출근 전에 매일 들러 / 규칙적인 일상 동선)

💡 핵심 패턴 훈련
- Can I get + 메뉴 + please? (주문할 때 이것만 쓰셔도 100점!)
- I usually + 동사원형 (난 보통 ~하곤 해 / 일상 습관)

🧠 뉘앙스 영문법: 단순현재 vs 현재진행형
- 단순현재는 '지금'이 아니라 어제도 오늘도 내일도 돌아가는 [시계태엽 습관]!
- What do you do? (평소 늘 하는 일 = 직업이 뭐예요?)
- What are you doing? (지금 카메라로 찍는 장면 = 지금 뭐 해?)
- I drive to work (평소 차로 출근해) vs I'm driving right now (지금 운전 중이야)

커피 한잔의 여유와 함께 즐겁게 청취해 보세요! ☕🎧"""
    },

    # 4. 2026-10-03 (토): 주말 복습 1탄
    "2026-10-03": {
        "type": "review",
        "day": "weekend_1",
        "card": """☕ [주말 영어 복습 1탄] 주중 핵심 표현 9개 총정리 & 3초 즉각 퀴즈

편안한 토요일 아침입니다!
이번 주 수·목·금 동안 차 안에서 익힌 핵심 표현 9개를 침대 속이나 소파에서 편안하게 복습해 보세요.
우리말을 보고 3초 안에 입술 밖으로 소리 내어 뱉어보세요!

━━━━━━━━━━━━━━━━━━━━
🔥 [Day 1 복습 퀴즈]
Q1. 길이나 카페에서 친구를 마주쳤을 때: "여기 웬일이야?"
    👉 정답: What brings you here?
Q2. 반가운 친구에게: "오랜만이야!"
    👉 정답: Long time no see!
Q3. 바쁜 아침: "나 사실 지금 출근하는 길이야."
    👉 정답: I'm actually on my way to work.

━━━━━━━━━━━━━━━━━━━━
🔥 [Day 2 복습 퀴즈]
Q4. 금요일 저녁 제안: "이번 주 금요일에 시간 돼? 저녁 먹을래?"
    👉 정답: Are you free this Friday? Want to grab dinner?
Q5. 정중한 거절: "정말 그러고 싶은데, 일 때문에 꼼짝을 못 해."
    👉 정답: I'd love to, but I'm tied up with work.
Q6. 다음을 기약하며: "다음에 하면 안 될까?"
    👉 정답: Can I take a rain check?

━━━━━━━━━━━━━━━━━━━━
🔥 [Day 3 복습 퀴즈]
Q7. 카페에서 친구에게: "여기서 보통 뭐 마셔?"
    👉 정답: What do you usually get here?
Q8. 카운터 주문: "아이스 바닐라 라떼 한 잔 주시겠어요?"
    👉 정답: Can I get an iced vanilla latte, please?
Q9. 나의 아침 루틴: "출근 전에 매일 들러."
    👉 정답: I stop by every day before work.

소리 내어 한 번씩 읊어보셨나요? 귀에 익은 소리는 결코 사라지지 않습니다. 편안한 주말 보내세요! 🌿"""
    },

    # 5. 2026-10-04 (일): 주말 복습 2탄
    "2026-10-04": {
        "type": "review",
        "day": "weekend_2",
        "card": """📖 [주말 영어 복습 2탄] 기초 영문법 3대 시제 비교 특강 & 주간 루브릭

여유로운 일요일 아침입니다!
내일부터 시작되는 과거 시제(Day 4~5)를 맞이하기 전에, 이번 주에 정복한 3대 기초 시제의 머릿속 그림을 하나로 꿰어드리겠습니다.

━━━━━━━━━━━━━━━━━━━━
🎨 머릿속에 그리는 영문법 3대 시제 지도

1. be동사는 등호(=)다! (Day 1)
   - 상태와 존재를 연결하는 수학의 equality sign.
   - 주어 = 상태 (I = ready, She = happy)
   - 감정 형용사(worried, tired) 앞에 be동사가 왜 필수인지 기억하세요!

2. 현재진행형은 라이브 비디오 카메라! (Day 2)
   - 지금 이 순간 렌즈에 포착되어 움직이고 있는 장면.
   - I'm driving right now (지금 핸들 잡고 운전 중)
   - 일시적인 상태 묘사 (I'm staying in Seoul this week)

3. 단순현재는 늘 돌아가는 시계태엽! (Day 3)
   - 어제도 그랬고, 오늘도 그러하며, 내일도 일어날 변함없는 사실과 습관.
   - I drink coffee every day (매일 마시는 나의 확고한 습관)
   - What do you do? (변함없는 당신의 직업은 무엇인가요?)

━━━━━━━━━━━━━━━━━━━━
🚀 내일(월) Day 4 예고
- 단순과거는 '앨범 속 사진(완결된 사건)'입니다.
- 한국인 최대 치명적 오류: "Did you went?", "I didn't saw"의 통쾌한 교정과,
- 차 고장으로 주말 여행이 어긋난 실전 대화가 펼쳐집니다!

내일 아침 7시 30분에 Day 4 방송으로 찾아뵙겠습니다! 일요일 마무리 잘하세요! ☀️"""
    },

    # 6. 2026-10-05 (월): Day 4
    "2026-10-05": {
        "type": "audio",
        "day": 4,
        "filename": "Day4_출퇴근영어라디오.mp3",
        "title": "Day 4: 주말 활동 & 돌발 상황",
        "performer": "Antigravity 출퇴근 영어 라디오 (21분)",
        "caption": "🚗 [Day 4] 출근길 차 안에서 귀로 배우는 21분 영어 라디오\n\n오늘의 핵심: 단순과거는 앨범 속에 박제된 '사진'입니다! (Did 뒤엔 무조건 동사원형!)",
        "card": """🚗 [출퇴근 영어 라디오 — Day 4] 주말 활동 & 돌발 상황

활기찬 월요일 아침입니다! 4일차 방송을 배달해 드립니다.
주말에 있었던 뜻밖의 돌발 상황을 나누며, 한국인 학습자들이 가장 많이 틀리는 과거 의문문·부정문의 원리를 완벽히 정복합니다.

━━━━━━━━━━━━━━━━━━━━
📌 오늘의 핵심 표현 3개
1. You won't believe what happened. (무슨 일 있었는지 들으면 진짜 안 믿길걸요 / 호기심 유발)
2. Something came up. (갑자기 일이 좀 생겼어 / 구차한 변명 없이 정중하게 사유 전달)
3. It completely slipped my mind. (그걸 까마득하게 잊고 있었어 / 머릿속에서 쏙 빠져나간 생생한 표현)

💡 핵심 패턴 훈련
- Did you + 동사원형? (너 ~했어?)
  * Did you see that movie? (너 그 영화 봤어?)
  * Did you get my message? (너 내 메시지 받았어?)
- I ended up + -ing (의도치 않게 결국 ~하게 되었어)
  * I ended up staying home. (결국 집에 있게 되었어)

🧠 뉘앙스 영문법: Did 뒤에는 왜 가벼운 동사원형일까?
- 도우미 Did / Didn't가 이미 "나 과거야!" 하고 시제 짐을 다 짊어졌습니다.
- Did you went? (X) ➔ Did you go? (O)
- I didn't saw (X) ➔ I didn't see (O)
- 규칙 동사 -ed 3대 소리: 트(/t/), 드(/d/), 이드(/ɪd/) 소리의 손맛!

월요병을 날려버릴 활기찬 영어 섀도잉, 지금 시작하세요! 🎧"""
    },

    # 7. 2026-10-06 (화): Day 5 (피날레)
    "2026-10-06": {
        "type": "audio",
        "day": 5,
        "filename": "Day5_출퇴근영어라디오.mp3",
        "title": "Day 5: 부재중 전화 & 업무 인터럽트 (완주 피날레)",
        "performer": "Antigravity 출퇴근 영어 라디오 (22분)",
        "caption": "🎉 [Day 5 피날레] 5부작 시리즈 완주를 축하합니다!\n\n오늘의 핵심: 과거진행형은 '배경음악', 단순과거는 '날아온 돌멩이'입니다!",
        "card": """🎉 [출퇴근 영어 라디오 — Day 5 피날레] 5부작 전편 완주!

화요일 아침입니다! 대망의 마지막 5일차 방송을 배달해 드립니다.
운전 중 부재중 전화와 업무 중 컴퓨터 다운 상황을 통해 과거진행형의 입체적인 매력과 정중한 부탁의 비결을 배웁니다.

━━━━━━━━━━━━━━━━━━━━
📌 오늘의 핵심 표현 3개
1. Sorry, I was driving when you called. (전화 주셨을 때 운전 중이라 못 받았어요)
2. I was just about to call you! (방금 막 전화하려던 참이었어 / 통하는 반가움)
3. I was wondering if you could help me. (혹시 나 좀 도와줄 수 있을까 해서요 / 극상의 공손함)

💡 핵심 패턴 훈련
- I was ~ing when... (~하고 있던 중 다른 일이 일어났을 때)
  * I was cooking dinner when the phone rang.
- I was wondering if you could + 동사원형 (상대의 부담을 덜어주는 마법의 부탁 패턴)

🧠 뉘앙스 영문법: 과거진행은 배경음악, 단순과거는 날아온 돌멩이!
- 길게 깔려 흐르던 배경 동작(was driving) + 쾅 하고 일어난 단발성 사건(when you called)
- 부탁할 때 왜 과거진행형을 쓸까? "지금 당장 도와달라고 부담 주는 게 아니라, 아까부터 혼자 고민 중이었는데..." 하는 심리적 배려의 쿠션!

━━━━━━━━━━━━━━━━━━━━
🏆 5일 코스 완주를 진심으로 축하드립니다!
Day 1: be동사(=) ➔ Day 2: 현재진행(카메라) ➔ Day 3: 단순현재(시계태엽) ➔ Day 4: 단순과거(사진) ➔ Day 5: 과거진행(배경음악)
매일 아침 차 안에서 큰 소리로 외쳐주신 여러분이 진정한 챔피언입니다! 👏🎧"""
    }
}

def send_telegram_audio(token, chat_id, audio_path, title, performer, caption):
    url = f"https://api.telegram.org/bot{token}/sendAudio"
    print(f"오디오 파일 전송 중: {os.path.basename(audio_path)} ({os.path.getsize(audio_path) / (1024*1024):.2f} MB)...")
    with open(audio_path, "rb") as f:
        files = {"audio": (os.path.basename(audio_path), f, "audio/mpeg")}
        data = {
            "chat_id": chat_id,
            "title": title,
            "performer": performer,
            "caption": caption
        }
        res = requests.post(url, data=data, files=files, timeout=120)
        res_json = res.json()
        if not res_json.get("ok"):
            raise RuntimeError(f"Telegram sendAudio failed: {res_json}")
        print("  -> 오디오 파일 전송 성공!")
        return res_json

def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    print("스터디 카드 텍스트 메시지 전송 중...")
    data = {
        "chat_id": chat_id,
        "text": text
    }
    res = requests.post(url, json=data, timeout=30)
    res_json = res.json()
    if not res_json.get("ok"):
        raise RuntimeError(f"Telegram sendMessage failed: {res_json}")
    print("  -> 텍스트 메시지 전송 성공!")
    return res_json

def run_distribution(target_date_str=None, dry_run=False, force=False):
    if not target_date_str:
        target_date_str = datetime.now().strftime("%Y-%m-%d")

    print("=" * 80)
    print(f"★ Antigravity 25분 출퇴근 영어 라디오 일일 배달기 (실행일: {target_date_str})")
    print("=" * 80)

    content = CONTENT_MAP.get(target_date_str)
    if not content:
        print(f"안내: {target_date_str}에 배정된 정규 스케줄이 없습니다. (5부작 코스 완료 후 대기 상태)")
        return

    c_type = content.get("type")

    if dry_run:
        print(f"[DRY-RUN] 전송 시뮬레이션 모드 (실제 전송 안 함):")
        print(f"  - 타입: {c_type}")
        print(f"  - 대상: {content.get('title', '주말 복습')}")
        if c_type == "audio":
            audio_path = os.path.join(AUDIO_DIR, content["filename"])
            print(f"  - 파일: {audio_path} (존재 여부: {os.path.exists(audio_path)})")
        print(f"  - 텍스트 요약 미리보기:\n{content['card'][:150]}...")
        return

    # 중복 발송 방지 체크
    history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "english_bot_sent_history.json")
    import json
    history = {}
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = {}

    if target_date_str in history and not force:
        print(f"안내: {target_date_str} 배달은 이미 완료되었습니다 ({history[target_date_str]}). 중복 발송을 방지합니다.")
        return

    # 실제 전송 실행
    if c_type == "audio":
        audio_path = os.path.join(AUDIO_DIR, content["filename"])
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"음성 파일을 찾을 수 없습니다: {audio_path}")
        
        # 1. MP3 오디오 파일 전송
        send_telegram_audio(
            TELEGRAM_TOKEN,
            TELEGRAM_CHAT_ID,
            audio_path,
            content["title"],
            content["performer"],
            content["caption"]
        )

        # 2. 상세 학습 카드 메시지 전송
        send_telegram_message(
            TELEGRAM_TOKEN,
            TELEGRAM_CHAT_ID,
            content["card"]
        )
    elif c_type == "review":
        # 주말 복습 카드 전송
        send_telegram_message(
            TELEGRAM_TOKEN,
            TELEGRAM_CHAT_ID,
            content["card"]
        )

    # 이력 기록
    history[target_date_str] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print(f"★★★ {target_date_str} 일일 영어 라디오 텔레그램 배달 완료! ★★★")
    print("=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity 출퇴근 영어 라디오 텔레그램 자동 배달 봇")
    parser.add_argument("--date", type=str, help="특정 날짜 강제 실행 (형식: YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="실제 전송 없이 내용 검증만 수행")
    parser.add_argument("--force", action="store_true", help="중복 발송 검사를 무시하고 강제 재전송")

    args = parser.parse_args()

    run_distribution(target_date_str=args.date, dry_run=args.dry_run, force=args.force)
