import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
df = pd.read_excel(file_path, sheet_name='수학여행 숙소')

print("Rows around 108 in '수학여행 숙소':")
print(df.iloc[100:120, :10].to_string())
