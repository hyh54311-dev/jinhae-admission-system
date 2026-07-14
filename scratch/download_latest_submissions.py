import pandas as pd
import sys
import urllib.request
import re

sys.stdout.reconfigure(encoding='utf-8')

url = "https://docs.google.com/spreadsheets/d/1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU/export?format=xlsx"
output_file = "scratch/submissions_latest.xlsx"

try:
    print("Downloading latest Google Sheet...")
    urllib.request.urlretrieve(url, output_file)
    print("Downloaded successfully!")
    
    xl = pd.ExcelFile(output_file)
    all_submissions = set()
    
    # Let's search for 박서진 and 유형우 in all sheets
    for sname in xl.sheet_names:
        if '설문지 응답' not in sname:
            continue
        df = xl.parse(sname)
        print(f"\nProcessing '{sname}' (shape: {df.shape})...")
        for idx, row in df.iterrows():
            class_cell = row.iloc[1]
            if pd.isna(class_cell):
                continue
            class_str = str(class_cell).strip()
            class_match = re.search(r'(\d+)\s*반', class_str)
            if not class_match:
                continue
            cls = int(class_match.group(1))
            
            no = None
            name = None
            for cell_val in row.values:
                if pd.isna(cell_val):
                    continue
                cell_str = str(cell_val).strip()
                match = re.match(r'^(\d+)\s*번\s*([^\s]+)$', cell_str)
                if match:
                    no = int(match.group(1))
                    name = match.group(2).strip()
                    break
            if cls and no and name:
                all_submissions.add((cls, no, name))
                if name in ['박서진', '유형우']:
                    print(f"  Found '{name}' in sheet '{sname}' row {idx}: Class {cls}, No {no}, Name {name}")
                    
    print(f"\nTotal unique student submissions: {len(all_submissions)}")
    
except Exception as e:
    print("Error:", e)
