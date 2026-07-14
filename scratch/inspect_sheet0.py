import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
xl = pd.ExcelFile(file_path)

# Let's inspect the first sheet (index 0)
df = xl.parse(xl.sheet_names[0])
print("Sheet 0 Name:", xl.sheet_names[0])
print("Sheet 0 Shape:", df.shape)
print("Sheet 0 Head:")
print(df.head(10).to_string())

# Also let's print sheet names in hex representation of their UTF-8/CP949 bytes if we suspect encoding issues, 
# or just print them using repr() to see unicode escape sequences.
print("\nAll Sheet Names (repr):")
for i, name in enumerate(xl.sheet_names):
    print(f"{i}: {repr(name)}")
