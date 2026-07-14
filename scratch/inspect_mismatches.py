import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
df = pd.read_excel(file_path, sheet_name='학생 명렬')

def print_class_roster(c):
    print(f"\n--- Class {c} Roster ---")
    start_col = 1 + (c - 1) * 3
    for r in range(2, 33):
        num = df.iloc[r, start_col]
        name = df.iloc[r, start_col + 1]
        note = df.iloc[r, start_col + 2]
        if pd.notna(name) or pd.notna(num):
            print(f"Row {r}: No. {num}, Name '{name}' (Note: {note})")

print_class_roster(2)
print_class_roster(5)
print_class_roster(6)
