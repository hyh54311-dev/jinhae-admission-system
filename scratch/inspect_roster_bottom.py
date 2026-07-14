import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
xl = pd.ExcelFile(file_path)
df = xl.parse('학생 명렬')

# Print rows 30 to 45 of '학생 명렬'
print("Rows 30 to 45:")
print(df.iloc[30:45, :16].to_string())
print("-" * 50)
print(df.iloc[30:45, 16:32].to_string())
