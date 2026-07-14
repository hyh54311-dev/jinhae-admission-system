import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
xl = pd.ExcelFile(file_path)
df = xl.parse('학생 명렬')

# Print out unique values in the note columns (columns at index 3, 6, 9, 12, 15, 18, 21, 24, 27, 30)
note_cols = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
print("Note columns in 학생 명렬:")
for col_idx in note_cols:
    col_name = df.columns[col_idx]
    class_name = df.iloc[0, col_idx - 2]
    notes = df.iloc[2:, col_idx].dropna().unique()
    print(f"  Col {col_idx} ({class_name}): {notes}")

print("\nLet's search for any cell containing '도움' in the entire sheet '학생 명렬':")
for r_idx in range(df.shape[0]):
    for c_idx in range(df.shape[1]):
        val = df.iloc[r_idx, c_idx]
        if pd.notna(val) and '도움' in str(val):
            print(f"Row {r_idx}, Col {c_idx} ({df.columns[c_idx]}): {val}")

# Let's search for other sheets that might contain helper class (도움반) information
print("\nSearching for sheets with '도움' in their names:")
for name in xl.sheet_names:
    if '도움' in name:
        print(f"  Found sheet: {name}")
