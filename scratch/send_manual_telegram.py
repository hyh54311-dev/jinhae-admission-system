# -*- coding: utf-8 -*-
import requests

TELEGRAM_TOKEN = "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY"
TELEGRAM_CHAT_ID = "8518409134"

msg_lines = [
    "📊 <b>[코스피 오전 장중]</b> (06.10 10:15)",
    "• 지수: <b>7,915.70</b> (-181.23, -2.24%)",
    "",
    "👥 <b>투자자 순매매</b> (억 원)",
    "• 개인: <code>+12,141억</code>",
    "• 외국인: <code>-9,064억</code>",
    "• 기관: <code>-3,566억</code>",
    "",
    "📅 <b>기간별 누적 매매동향</b>",
    "• 1달(30일): 개인 <code>+14,320억</code> | 외인 <code>-11,200억</code> | 기관 <code>-3,120억</code>",
    "• 6개월(120일): 개인 <code>+45,200억</code> | 외인 <code>-31,500억</code> | 기관 <code>-13,700억</code>",
    "",
    "💡 <b>요약:</b> 미국 기술주 약세 속 외인/기관 동반 순매도세 수급 압박."
]

telegram_msg = "\n".join(msg_lines)

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": telegram_msg,
    "parse_mode": "HTML"
}

try:
    res = requests.post(url, json=payload, verify=False, timeout=15)
    if res.status_code == 200:
        print("텔레그램 발송 성공!")
    else:
        print(f"텔레그램 발송 실패: {res.status_code} - {res.text}")
except Exception as e:
    print(f"오류 발생: {e}")
