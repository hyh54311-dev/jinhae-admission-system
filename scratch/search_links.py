import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

roster_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
submissions_path = "scratch/submissions.xlsx"

def search_links(file_path):
    print(f"Searching for links in {file_path}:")
    try:
        xl = pd.ExcelFile(file_path)
        for sname in xl.sheet_names:
            df = xl.parse(sname)
            for r_idx in range(df.shape[0]):
                for c_idx in range(df.shape[1]):
                    val = df.iloc[r_idx, c_idx]
                    if pd.notna(val) and ('form' in str(val) or 'http' in str(val)):
                        print(f"  [{sname}] Row {r_idx}, Col {c_idx}: {val}")
    except Exception as e:
        print("Error:", e)

search_links(roster_path)
search_links(submissions_path)
