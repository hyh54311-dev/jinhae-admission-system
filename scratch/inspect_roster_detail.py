import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
xl = pd.ExcelFile(file_path)

df = xl.parse('학생 명렬')
print("Shape of '학생 명렬':", df.shape)
print("Columns:")
print(df.columns.tolist())
print("\nFirst 15 rows of '학생 명렬':")
print(df.head(15).to_string())

# Let's see if there are any other columns or non-null values that might represent special education (도움반)
# Or let's see if there's any column that has help class (도움반) in its name or content.
for col in df.columns:
    col_str = str(col)
    unique_vals = df[col].dropna().unique()
    if len(unique_vals) < 20:
        print(f"Col {col} unique values: {unique_vals}")
