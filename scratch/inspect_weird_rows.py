import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions_latest.xlsx"
xl = pd.ExcelFile(file_path)
df = xl.parse('설문지 응답 시트6')

rows_to_print = [70, 71, 154, 155, 156, 157]
for r in rows_to_print:
    print(f"\nRow {r}:")
    row = df.iloc[r]
    for c_idx, val in enumerate(row):
        if pd.notna(val) and str(val).strip() != "":
            print(f"  Col {c_idx} ({df.columns[c_idx][:25]}): {val}")
