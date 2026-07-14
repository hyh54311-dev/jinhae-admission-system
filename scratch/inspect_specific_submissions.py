import pandas as pd
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions.xlsx"
sub_xl = pd.ExcelFile(file_path)
submitted_list = []

for sheet_name in ['설문지 응답 시트6', '설문지 응답 시트5']:
    if sheet_name not in sub_xl.sheet_names:
        continue
    df = sub_xl.parse(sheet_name)
    for idx, row in df.iterrows():
        class_cell = row.iloc[1]
        if pd.isna(class_cell):
            continue
        class_str = str(class_cell).strip()
        class_match = re.search(r'(\d+)\s*반', class_str)
        if not class_match:
            continue
        cls = int(class_match.group(1))
        
        for cell_val in row.values:
            if pd.isna(cell_val):
                continue
            cell_str = str(cell_val).strip()
            match = re.match(r'^(\d+)\s*번\s*([^\s]+)$', cell_str)
            if match:
                no = int(match.group(1))
                name = match.group(2).strip()
                submitted_list.append((cls, no, name))

# Print submissions for Class 2, 5, 6
for c in [2, 5, 6]:
    print(f"\nSubmissions for Class {c}:")
    c_subs = [s for s in submitted_list if s[0] == c]
    for s in sorted(c_subs, key=lambda x: x[1]):
        print(f"  No. {s[1]}: {s[2]}")
