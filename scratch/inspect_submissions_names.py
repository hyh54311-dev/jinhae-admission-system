import pandas as pd
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions.xlsx"

# Let's inspect all sheet name-selection values
xl = pd.ExcelFile(file_path)
for sheet_name in xl.sheet_names:
    df = xl.parse(sheet_name)
    print(f"\nSheet '{sheet_name}' row count: {df.shape[0]}")
    
    # Find columns that might contain name selections
    name_cols = [col for col in df.columns if '이름' in str(col)]
    for col in name_cols:
        vals = df[col].dropna().unique()
        print(f"  Col '{col}' unique values ({len(vals)}):")
        print(f"    {vals[:10]}")
