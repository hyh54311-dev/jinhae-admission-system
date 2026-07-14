import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions_latest.xlsx"
xl = pd.ExcelFile(file_path)

# Let's search for '유형우' in all sheets and print row index, timestamp, and answers
for sname in xl.sheet_names:
    if '설문지 응답' not in sname:
        continue
    df = xl.parse(sname)
    ans_indices = [2, 3, 4, 5, 6] if sname == '설문지 응답 시트5' else [12, 13, 14, 15, 16]
    
    for idx, row in df.iterrows():
        row_str = " ".join([str(val) for val in row.values if pd.notna(val)])
        if '유형우' in row_str:
            print(f"\nFound in sheet '{sname}' Row {idx}:")
            print(f"  Timestamp: {row.iloc[0]}")
            print(f"  Class: {row.iloc[1]}")
            print(f"  Answers:")
            for q_idx, col in enumerate(ans_indices):
                print(f"    Q{16+q_idx}: {row.iloc[col]}")
