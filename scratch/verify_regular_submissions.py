import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions.xlsx"
sub_xl = pd.ExcelFile(file_path)

names_to_check = ['이승우', '이요한', '박서진', '강수민', '김도현', '최윤혁']

print("Searching for regular unsubmitted students in submissions (any match):")
found_any = False
for sheet_name in ['설문지 응답 시트6', '설문지 응답 시트5']:
    if sheet_name not in sub_xl.sheet_names:
        continue
    df = sub_xl.parse(sheet_name)
    for idx, row in df.iterrows():
        row_str = " ".join([str(val) for val in row.values if pd.notna(val)])
        for name in names_to_check:
            if name in row_str:
                print(f"  Found '{name}' in sheet '{sheet_name}' row {idx}: {row_str}")
                found_any = True

if not found_any:
    print("  None of these students are in the submissions file at all.")
