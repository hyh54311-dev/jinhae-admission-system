import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
xl = pd.ExcelFile(file_path)
df = xl.parse('학생 명렬')

# The header rows are the first 2 rows.
# Row 0 has the class names: '1반' at Unnamed: 1 or similar. Let's see:
print("Row 0:")
print(df.iloc[0].to_dict())
print("Row 1:")
print(df.iloc[1].to_dict())

students = []
# There are 10 classes
# Each class occupies 3 columns:
# Class 1: Unnamed: 1 (번호), Unnamed: 2 (성명), Unnamed: 3 (비고)
# Class 2: Unnamed: 4 (번호), Unnamed: 5 (성명), Unnamed: 6 (비고)
# Class 3: Unnamed: 7 (번호), Unnamed: 8 (성명), Unnamed: 9 (비고)
# Class 4: Unnamed: 10 (번호), Unnamed: 11 (성명), Unnamed: 12 (비고)
# Class 5: Unnamed: 13 (번호), Unnamed: 14 (성명), Unnamed: 15 (비고)
# Class 6: Unnamed: 16 (번호), Unnamed: 17 (성명), Unnamed: 18 (비고)
# Class 7: Unnamed: 19 (번호), Unnamed: 20 (성명), Unnamed: 21 (비고)
# Class 8: Unnamed: 22 (번호), Unnamed: 23 (성명), Unnamed: 24 (비고)
# Class 9: Unnamed: 25 (번호), Unnamed: 26 (성명), Unnamed: 27 (비고)
# Class 10: Unnamed: 28 (번호), Unnamed: 29 (성명), Unnamed: 30 (비고)

# Let's verify the columns and their headers.
for class_idx in range(10):
    start_col = 1 + class_idx * 3
    # Let's inspect the names of these columns or the values in row 0
    c_num = df.columns[start_col]
    c_name = df.columns[start_col + 1]
    c_note = df.columns[start_col + 2]
    print(f"Class {class_idx+1}: {c_num}, {c_name}, {c_note}")

