import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
df = pd.read_excel(file_path, sheet_name='3학년 모의고사 응시인원')

print("Rows around '도움' in '3학년 모의고사 응시인원':")
for r_idx in range(df.shape[0]):
    for c_idx in range(df.shape[1]):
        val = df.iloc[r_idx, c_idx]
        if pd.notna(val) and '도움' in str(val):
            print(f"Row {r_idx}, Col {c_idx}: {val}")
            start_row = max(0, r_idx - 2)
            end_row = min(df.shape[0], r_idx + 6)
            start_col = max(0, c_idx - 1)
            end_col = min(df.shape[1], c_idx + 4)
            print(df.iloc[start_row:end_row, start_col:end_col].to_string())
            print("-" * 50)
