import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions_new.xlsx"
xl = pd.ExcelFile(file_path)
print("Sheet Names in downloaded spreadsheet:", xl.sheet_names)

names_to_check = ['이승우', '이요한', '최윤혁', '김도현', '강수민']

for sname in xl.sheet_names:
    df = xl.parse(sname)
    print(f"\nSheet '{sname}' Shape: {df.shape}")
    for idx, row in df.iterrows():
        row_str = " ".join([str(val) for val in row.values if pd.notna(val)])
        for name in names_to_check:
            if name in row_str:
                print(f"  Found '{name}' in sheet '{sname}' row {idx}: {row_str[:200]}")
