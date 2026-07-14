import pandas as pd
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

url = "https://docs.google.com/spreadsheets/d/1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU/export?format=xlsx"
output_file = "scratch/submissions.xlsx"

try:
    print("Downloading Google Sheet...")
    urllib.request.urlretrieve(url, output_file)
    print("Downloaded successfully!")
    
    xl = pd.ExcelFile(output_file)
    print("Google Sheet Sheet names:", xl.sheet_names)
    
    for sname in xl.sheet_names:
        df = xl.parse(sname)
        print(f"Sheet '{sname}' Shape: {df.shape}")
        print("Columns:", df.columns.tolist()[:10])
        print(df.head(5).to_string())
        print("-" * 50)
except Exception as e:
    print("Error:", e)
