import pandas as pd
import sys

try:
    df = pd.read_excel(r'D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무(장학금 및 입학홍보)\1. 입학\전년도 진학결과\대학 진학 현황.xlsx', header=None)
    with open('excel_content.txt', 'w', encoding='utf-8') as f:
        f.write(df.to_string())
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
