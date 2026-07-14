import pandas as pd
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions_new.xlsx"
xl = pd.ExcelFile(file_path)
df = xl.parse('설문지 응답 시트6')

# 1. Parse all submissions
submissions = []
# Col 1: Class selection
# Cols 2 to 11: Name selections
# Cols 12 to 16: Answers for 16, 17, 18, 19, 20

for idx, row in df.iterrows():
    # Class
    class_cell = row.iloc[1]
    if pd.isna(class_cell):
        continue
    class_str = str(class_cell).strip()
    class_match = re.search(r'(\d+)\s*반', class_str)
    if not class_match:
        continue
    cls = int(class_match.group(1))
    
    # Name and No
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
            break
            
    if cls and no and name:
        # Get answers (col 12 to 16)
        ans16 = row.iloc[12]
        ans17 = row.iloc[13]
        ans18 = row.iloc[14]
        ans19 = row.iloc[15]
        ans20 = row.iloc[16]
        
        submissions.append({
            'class': cls,
            'no': no,
            'name': name,
            'ans16': ans16,
            'ans17': ans17,
            'ans18': ans18,
            'ans19': ans19,
            'ans20': ans20
        })

print(f"Total parsed active submissions: {len(submissions)}")

# Unique submissions (remove duplicates, keeping the latest one by index/timestamp)
# Since submissions list is chronological, we keep the last one for each student (class, no, name)
unique_submissions = {}
for sub in submissions:
    key = (sub['class'], sub['no'], sub['name'])
    unique_submissions[key] = sub

print(f"Total unique students submitted: {len(unique_submissions)}")

# Define what constitutes blank or placeholder
placeholders = {
    '.', '-', '?', 'x', 'X', 'ㄴ', 'ㅇ', 'ㄴㄴ', '모름', '모르겠음', 
    '못적음', '못작성', '미작성', '서술 안함', '서술안함', '정답 안적음', '정답안적음'
}

def is_blank(val):
    if pd.isna(val):
        return True
    val_str = str(val).strip()
    if val_str == "":
        return True
    if val_str in placeholders:
        return True
    # If it's just spaces or very short meaningless characters
    if len(val_str) == 1 and val_str in ['.', '-', '?', ' ']:
        return True
    return False

# Analysis
q_labels = {
    'ans16': '16번 (세런디피티 개념)',
    'ans17': '17번 (연구 수행자 이름)',
    'ans18': '18번 (플레밍 개발동기 약했던 까닭)',
    'ans19': '19번 (페니실린 박테리아 억제 까닭)',
    'ans20': '20번 (그람 음성균 효과 없는 까닭)'
}

blank_students_per_q = {q: [] for q in q_labels.keys()}

for key, sub in unique_submissions.items():
    cls, no, name = key
    for q in q_labels.keys():
        val = sub[q]
        if is_blank(val):
            blank_students_per_q[q].append({
                'class': cls,
                'no': no,
                'name': name,
                'raw_val': str(val).strip() if pd.notna(val) else 'NaN'
            })

# Print results
for q, students in blank_students_per_q.items():
    print(f"\n=== {q_labels[q]} 미작성 학생 ({len(students)}명) ===")
    # Sort by class, number
    sorted_students = sorted(students, key=lambda x: (x['class'], x['no']))
    for s in sorted_students:
        print(f"  {s['class']}반 {s['no']}번 {s['name']} (입력값: '{s['raw_val']}')")

# Also find students who didn't write answers to ALL 5 questions
all_blank_students = []
for key, sub in unique_submissions.items():
    cls, no, name = key
    all_b = True
    raw_vals = []
    for q in q_labels.keys():
        if not is_blank(sub[q]):
            all_b = False
            break
        raw_vals.append(str(sub[q]).strip() if pd.notna(sub[q]) else 'NaN')
    if all_b:
        all_blank_students.append({
            'class': cls,
            'no': no,
            'name': name,
            'vals': raw_vals
        })

print(f"\n=== 모든 문항 미작성 학생 ({len(all_blank_students)}명) ===")
for s in sorted(all_blank_students, key=lambda x: (x['class'], x['no'])):
    print(f"  {s['class']}반 {s['no']}번 {s['name']}")
