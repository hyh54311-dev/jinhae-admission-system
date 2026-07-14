import pandas as pd
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

url = "https://docs.google.com/spreadsheets/d/1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU/export?format=xlsx"
output_file = "scratch/submissions_new.xlsx"

try:
    print("Downloading updated Google Sheet...")
    urllib.request.urlretrieve(url, output_file)
    print("Downloaded successfully!")
    
    # Read sheet 0
    df = pd.read_excel(output_file, sheet_name=0)
    print("New Sheet 0 Shape:", df.shape)
    print("\nLast 8 rows of Sheet 0:")
    print(df.tail(8).to_string())
except Exception as e:
    print("Error:", e)
