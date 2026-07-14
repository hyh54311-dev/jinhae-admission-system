import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
df = pd.read_excel(file_path, sheet_name='학생 명렬')

print("Searching '현준' in '학생 명렬':")
for r_idx in range(df.shape[0]):
    for c_idx in range(df.shape[1]):
        val = df.iloc[r_idx, c_idx]
        if pd.notna(val) and ('현준' in str(val) or '조현' in str(val)):
            print(f"Row {r_idx}, Col {c_idx} ({df.columns[c_idx]}): {val}")
