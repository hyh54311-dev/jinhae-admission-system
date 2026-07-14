import pandas as pd
import requests
import io

def test_fetch():
    tickers = ["^KS11", "^GSPC", "USDKRW=X"]
    for ticker in tickers:
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1=946684800&period2=1779110400&interval=1d&events=history&includeAdjustedClose=true"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            res = requests.get(url, headers=headers, verify=False)
            res.raise_for_status()
            df = pd.read_csv(io.StringIO(res.text))
            print(f"Ticker {ticker}: successfully fetched {len(df)} rows!")
            if not df.empty:
                print(df.head(2))
        except Exception as e:
            print(f"Failed to fetch {ticker}: {e}")

if __name__ == "__main__":
    test_fetch()
