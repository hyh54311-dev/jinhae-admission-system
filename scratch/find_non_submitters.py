import pandas as pd
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# Paths
roster_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"
submissions_path = "scratch/submissions.xlsx"

# 1. Parse student roster
roster_xl = pd.ExcelFile(roster_path)
roster_df = roster_xl.parse('학생 명렬')

# Students list: each student is a dict with keys: class, no, name, note, is_helper
students = []
help_class_students = [
    (3, 7, '김승진'),
    (3, 16, '문상현'),
    (4, 2, '권해찬'),
    (4, 11, '박동은'),
    (6, 3, '김건우'),
    (7, 28, '팽정욱')
]

# Set of help class student tuples (class, no, name) for easy lookup
help_class_set = set(help_class_students)

# Iterate through 10 classes
for class_idx in range(10):
    c_num = class_idx + 1
    start_col = 1 + class_idx * 3
    # Student rows are from index 2 to 31 (inclusive)
    for r_idx in range(2, 32):
        num_val = roster_df.iloc[r_idx, start_col]
        name_val = roster_df.iloc[r_idx, start_col + 1]
        note_val = roster_df.iloc[r_idx, start_col + 2]
        
        # If name is nan, skip
        if pd.isna(name_val) or str(name_val).strip() == "":
            continue
            
        name = str(name_val).strip()
        num = int(num_val)
        note = str(note_val).strip() if pd.notna(note_val) else ""
        
        # Check if student is in 도움반
        is_helper = (c_num, num, name) in help_class_set
        
        students.append({
            'class': c_num,
            'no': num,
            'name': name,
            'note': note,
            'is_helper': is_helper
        })

print(f"Loaded {len(students)} students from roster.")

# 2. Parse submissions from Google Sheet
sub_xl = pd.ExcelFile(submissions_path)
submitted_set = set() # Set of tuples (class, no, name)

# We check Sheet 0 ('설문지 응답 시트6') and Sheet 1 ('설문지 응답 시트5')
for sheet_name in ['설문지 응답 시트6', '설문지 응답 시트5']:
    if sheet_name not in sub_xl.sheet_names:
        continue
    df = sub_xl.parse(sheet_name)
    
    # We find class and name for each row
    for idx, row in df.iterrows():
        # Class selection
        class_cell = row.iloc[1]
        if pd.isna(class_cell):
            continue
        
        # Clean class (e.g. '10반' -> 10, '1반' -> 1)
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
                break
        
        if cls and student_no and student_name:
            submitted_set.add((cls, student_no, student_name))

print(f"Loaded {len(submitted_set)} unique student submissions.")

# 3. Handle Exceptions:
# "2반 12번 김한결 자퇴, 3반 4번 김민성 위탁, 5반 17번 이민혁 위탁, 6반 27번 차정환 위탁, 7반 21번 오은석 위탁, 10반 15번 박준용 위탁이야."
# Also, 5반 30번 강민서 is '전출' (transferred) in the note.
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

# Let's count how many students submitted, how many are excluded, and how many are non-submitters
unsubmitted_students = []
submitted_students = []
excluded_students = []

for s in students:
    student_tuple = (s['class'], s['no'], s['name'])
    
    # Check if excluded
    if student_tuple in exclude_set or s['note'] in ['위탁', '전출', '자퇴']:
        # Double check if any note contains these keywords
        excluded_students.append(s)
        continue
        
    # Check if submitted
    # Sometimes there might be a slight mismatch in name, so let's also check by (class, no)
    # or look for the exact match
    is_submitted = False
    for sub_cls, sub_no, sub_name in submitted_set:
        if sub_cls == s['class'] and sub_no == s['no']:
            # Check name similarity or exact match
            if sub_name == s['name']:
                is_submitted = True
                break
            else:
                print(f"Warning: Match found for class {s['class']} no {s['no']} but names differ: Roster='{s['name']}', Submission='{sub_name}'")
                is_submitted = True
                break
                
    if is_submitted:
        submitted_students.append(s)
    else:
        unsubmitted_students.append(s)

print(f"Excluded: {len(excluded_students)} students.")
print(f"Submitted: {len(submitted_students)} students.")
print(f"Unsubmitted: {len(unsubmitted_students)} students.")

# Separate help class students
help_class_submissions = []
regular_unsubmitted = []

for s in unsubmitted_students:
    if s['is_helper']:
        pass
    else:
        regular_unsubmitted.append(s)

# List all help class students and their submission status
help_class_status = []
for h_cls, h_no, h_name in help_class_students:
    # Check if this student submitted
    status = "제출완료"
    for sub_cls, sub_no, sub_name in submitted_set:
        if sub_cls == h_cls and sub_no == h_no:
            status = "제출완료"
            break
    else:
        status = "미제출"
    help_class_status.append({
        'class': h_cls,
        'no': h_no,
        'name': h_name,
        'status': status
    })

print("\n--- 도움반 학생 제출 현황 ---")
for h in help_class_status:
    print(f"{h['class']}반 {h['no']}번 {h['name']}: {h['status']}")

print("\n--- 미제출 학생 명단 (도움반, 예외 학생 제외) ---")
# Group regular_unsubmitted by class
from collections import defaultdict
grouped_unsub = defaultdict(list)
for s in regular_unsubmitted:
    grouped_unsub[s['class']].append(s)

for c in sorted(grouped_unsub.keys()):
    print(f"\n{c}반:")
    for s in sorted(grouped_unsub[c], key=lambda x: x['no']):
        print(f"  {s['no']}번 {s['name']}")
