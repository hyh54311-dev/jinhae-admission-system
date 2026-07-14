import urllib3
import requests
from unittest.mock import patch

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# requests.Session.send의 verify 인자를 False로 고정하는 패치
original_send = requests.Session.send
def patched_send(self, request, **kwargs):
    kwargs['verify'] = False
    return original_send(self, request, **kwargs)
requests.Session.send = patched_send

from pykrx import stock

try:
    print("pykrx로 코스피 수급 데이터 수집 시도...")
    df = stock.get_market_net_purchases_of_equities_by_ticker('20260608', '20260608', 'KOSPI')
    print("성공! 데이터프레임 구조:")
    print(df.head())
except Exception as e:
    print("실패! 에러:")
    print(e)
