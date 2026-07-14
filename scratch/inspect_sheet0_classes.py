import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions.xlsx"
df = pd.read_excel(file_path, sheet_name=0)

print("Sheet index 0 details:")
print("Shape:", df.shape)
print("Unique values in '반을 선택해 주세요.':")
print(df.iloc[:, 1].dropna().value_counts())
print("\nFirst 10 rows:")
print(df.iloc[:10, [0, 1, 2, 3, 4, 11]])
