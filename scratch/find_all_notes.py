import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
df = pd.read_excel(file_path, sheet_name='학생 명렬')

print("Checking student rows with notes in '학생 명렬':")
for class_idx in range(10):
    start_col = 1 + class_idx * 3
    class_name = df.iloc[0, start_col]
    # Rows 2 to 31
    for r_idx in range(2, 32):
        num_val = df.iloc[r_idx, start_col]
        name_val = df.iloc[r_idx, start_col + 1]
        note_val = df.iloc[r_idx, start_col + 2]
        if pd.notna(name_val) or pd.notna(note_val):
            print(f"Row {r_idx}, Class {class_idx+1}: No. {num_val}, Name {name_val}, Note {note_val}")
