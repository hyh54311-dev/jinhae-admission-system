import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions.xlsx"
df = pd.read_excel(file_path, sheet_name='설문지 응답 시트5')

print(df.info())
print(df)
