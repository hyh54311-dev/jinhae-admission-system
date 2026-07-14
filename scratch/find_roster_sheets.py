import pandas as pd
import sys

# Set output encoding to utf-8 just in case
sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\OneDrive - 경상남도컴퓨터\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
# Fix path: "D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"

xl = pd.ExcelFile(file_path)

for sheet_name in xl.sheet_names:
    try:
        # read first 5 rows
        df = xl.parse(sheet_name, nrows=5)
        # Check if any column or cell contains student-like headers
        has_student_info = False
        cols_str = str(df.columns.tolist())
        first_rows_str = str(df.values.tolist())
        
        keywords = ['반', '번호', '성명', '이름', '학번', '도움']
        matches = [kw for kw in keywords if kw in cols_str or kw in first_rows_str]
        
        if len(matches) >= 2:
            print(f"Sheet: {sheet_name}")
            print(f"  Shape: {df.shape}")
            print(f"  Matches: {matches}")
            print("  Columns:", df.columns.tolist()[:10])
            print("  First 2 rows:")
            print(df.head(2).to_string())
            print("-" * 50)
    except Exception as e:
        print(f"Error reading sheet {sheet_name}: {e}")
