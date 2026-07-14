import pandas as pd
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions_new.xlsx"
xl = pd.ExcelFile(file_path)

all_submissions = set()

for sname in xl.sheet_names:
    if '설문지 응답' not in sname:
        continue
    df = xl.parse(sname)
    print(f"\nProcessing '{sname}' (shape: {df.shape})...")
    
    # We find class and name for each row
    for idx, row in df.iterrows():
        # Class selection (look at col 1)
        class_cell = row.iloc[1]
        if pd.isna(class_cell):
            continue
        class_str = str(class_cell).strip()
        class_match = re.search(r'(\d+)\s*반', class_str)
        if not class_match:
            continue
        cls = int(class_match.group(1))
        
        # Name selection: search all cells in the row for 'X번 YYY'
        student_no = None
        student_name = None
        
        for cell_val in row.values:
            if pd.isna(cell_val):
                continue
            cell_str = str(cell_val).strip()
            # Match pattern like '21번 정선우' or '2번 강윤태'
            match = re.match(r'^(\d+)\s*번\s*([^\s]+)$', cell_str)
            if match:
                student_no = int(match.group(1))
                student_name = match.group(2).strip()
                # Print to see
                break
        
        if cls and student_no and student_name:
            all_submissions.add((cls, student_no, student_name))
            # Let's print first 3 matches for each sheet to verify
            if len(all_submissions) <= 3 or idx < 3:
                print(f"  Row {idx}: Class {cls}, No {student_no}, Name {student_name}")

print(f"\nTotal unique student submissions across ALL sheets: {len(all_submissions)}")

# Print if 유형우 (10반 17번) and 박서진 (7반 11번) are in all_submissions
print("\nChecking specific students:")
print("  (10, 17, '유형우') in all_submissions:", (10, 17, '유형우') in all_submissions)
print("  (7, 11, '박서진') in all_submissions:", (7, 11, '박서진') in all_submissions)
