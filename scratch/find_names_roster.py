import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
xl = pd.ExcelFile(file_path)
df = xl.parse('학생 명렬')

names_to_find = ['김건우', '팽정욱', '문상현', '권해찬', '조현준', '고태경']

print("Searching names in '학생 명렬':")
for name in names_to_find:
    found = False
    for class_idx in range(10):
        start_col = 1 + class_idx * 3
        # col_idx + 1 is the name column
        name_col = df.iloc[2:, start_col + 1] # Row 2 is where students start
        num_col = df.iloc[2:, start_col]
        for idx, val in name_col.items():
            if pd.notna(val) and str(val).strip() == name:
                student_num = num_col.loc[idx]
                print(f"Name '{name}' found in Class {class_idx + 1}, No. {student_num} (Row {idx})")
                found = True
    if not found:
        print(f"Name '{name}' NOT found in '학생 명렬'")
