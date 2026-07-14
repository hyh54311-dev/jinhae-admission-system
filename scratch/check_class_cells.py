import pandas as pd
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions_latest.xlsx"
xl = pd.ExcelFile(file_path)
df = xl.parse('설문지 응답 시트6')

print("Inspecting rows in '설문지 응답 시트6' with empty/weird class cells:")
count = 0
for idx, row in df.iterrows():
    class_cell = row.iloc[1]
    class_str = str(class_cell).strip() if pd.notna(class_cell) else ""
    class_match = re.search(r'(\d+)\s*반', class_str)
    
    # Let's find which name column has a value
    selected_class_from_name = None
    student_no = None
    student_name = None
    
    # Cols 2 to 11 are for class 1 to 10
    for col_idx in range(2, 12):
        val = row.iloc[col_idx]
        if pd.notna(val) and str(val).strip() != "":
            match = re.match(r'^(\d+)\s*번\s*([^\s]+)$', str(val).strip())
            if match:
                selected_class_from_name = col_idx - 1 # Col 2 is Class 1, Col 11 is Class 10
                student_no = int(match.group(1))
                student_name = match.group(2).strip()
                break
                
    if not class_match or (class_match and int(class_match.group(1)) != selected_class_from_name):
        print(f"Row {idx}:")
        print(f"  Class cell in sheet: '{class_str}'")
        print(f"  Deduced Class from name col: {selected_class_from_name}반 ({student_no}번 {student_name})")
        count += 1

print(f"\nTotal rows with class cell mismatch or empty: {count}")
