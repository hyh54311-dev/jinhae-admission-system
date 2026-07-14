import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
xl = pd.ExcelFile(file_path)

print("Searching for '도움' in all sheets:")
for sheet_name in xl.sheet_names:
    try:
        df = xl.parse(sheet_name)
        for r_idx in range(df.shape[0]):
            for c_idx in range(df.shape[1]):
                val = df.iloc[r_idx, c_idx]
                if pd.notna(val) and ('도움' in str(val) or '특수' in str(val)):
                    # Print sheet, row, col, and the cell value
                    print(f"Sheet '{sheet_name}', Row {r_idx}, Col {c_idx} ({df.columns[c_idx]}): {val}")
    except Exception as e:
        print(f"Error reading sheet '{sheet_name}': {e}")
