import pandas as pd
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# Load roster
roster_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
roster_xl = pd.ExcelFile(roster_path)
roster_df = roster_xl.parse('학생 명렬')

students = []
help_class_students = [
    (3, 7, '김승진'),
    (3, 16, '문상현'),
    (4, 2, '권해찬'),
    (4, 11, '박동은'),
    (6, 3, '김건우'),
    (7, 28, '팽정욱')
]
help_class_set = set(help_class_students)

for class_idx in range(10):
    c_num = class_idx + 1
    start_col = 1 + class_idx * 3
    for r_idx in range(2, 32):
        num_val = roster_df.iloc[r_idx, start_col]
        name_val = roster_df.iloc[r_idx, start_col + 1]
        note_val = roster_df.iloc[r_idx, start_col + 2]
        
        if pd.isna(name_val) or str(name_val).strip() == "":
            continue
            
        name = str(name_val).strip()
        num = int(num_val)
        note = str(note_val).strip() if pd.notna(note_val) else ""
        
        is_helper = (c_num, num, name) in help_class_set
        
        students.append({
            'class': c_num,
            'no': num,
            'name': name,
            'note': note,
            'is_helper': is_helper
        })

# Load submissions
file_path = "scratch/submissions_new.xlsx"
xl = pd.ExcelFile(file_path)
df = xl.parse('설문지 응답 시트6')

submitted_keys = set()
for idx, row in df.iterrows():
    class_cell = row.iloc[1]
    if pd.isna(class_cell):
        continue
    class_str = str(class_cell).strip()
    class_match = re.search(r'(\d+)\s*반', class_str)
    if not class_match:
        continue
    cls = int(class_match.group(1))
    
    no = None
    name = None
    for cell_val in row.values:
        if pd.isna(cell_val):
            continue
        cell_str = str(cell_val).strip()
        match = re.match(r'^(\d+)\s*번\s*([^\s]+)$', cell_str)
        if match:
            no = int(match.group(1))
            name = match.group(2).strip()
            submitted_keys.add((cls, no, name))

# Check exclusions
exceptions_to_exclude = [
    (2, 12, '김한결', '자퇴'),
    (3, 4, '김민성', '위탁'),
    (5, 17, '이민혁', '위탁'),
    (6, 27, '차정환', '위탁'),
    (7, 21, '오은석', '위탁'),
    (10, 15, '박준용', '위탁'),
    (5, 30, '강민서', '전출')
]
exclude_set = set((c, n, name) for c, n, name, reason in exceptions_to_exclude)

# Find who hasn't submitted
unsubmitted = []
for s in students:
    student_tuple = (s['class'], s['no'], s['name'])
    if student_tuple in exclude_set or s['note'] in ['위탁', '전출', '자퇴']:
        continue
        
    # Check if this student is in submitted_keys
    is_sub = False
    for sub_cls, sub_no, sub_name in submitted_keys:
        if sub_cls == s['class'] and sub_name == s['name']:
            is_sub = True
            break
        elif sub_cls == s['class'] and sub_no == s['no']:
            # Double check if names match (with some flexibility, e.g. name is in roster)
            # In our previous check we had some duplicate numbers, but they are resolved.
            is_sub = True
            break
            
    if not is_sub:
        unsubmitted.append(s)

print(f"Roster active students count: {len(students) - len(exclude_set)}")
print(f"Unsubmitted count: {len(unsubmitted)}")
print("Unsubmitted list:")
for u in unsubmitted:
    print(f"  {u['class']}반 {u['no']}번 {u['name']} (Helper: {u['is_helper']})")
