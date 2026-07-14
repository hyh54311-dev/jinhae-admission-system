import pandas as pd
import requests
import datetime

def test_fetch_chart():
    tickers = ["^KS11", "^GSPC", "USDKRW=X"]
    # 2000-01-01 to 2026-05-22
    period1 = int(datetime.datetime(2000, 1, 1).timestamp())
    period2 = int(datetime.datetime(2026, 5, 22).timestamp())
    
    for ticker in tickers:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={period1}&period2={period2}&interval=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            res = requests.get(url, headers=headers, verify=False)
            res.raise_for_status()
            data = res.json()
            # Parse JSON
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            close = result['indicators']['quote'][0]['close']
            df = pd.DataFrame({"Date": pd.to_datetime(timestamps, unit='s'), "Close": close})
            df.set_index("Date", inplace=True)
            print(f"Ticker {ticker}: successfully fetched {len(df)} rows using v8/finance/chart!")
            print(df.head(2))
        except Exception as e:
            print(f"Failed to fetch {ticker} chart: {e}")

if __name__ == "__main__":
    test_fetch_chart()
