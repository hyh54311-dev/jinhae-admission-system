import pandas as pd
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions_latest.xlsx"
xl = pd.ExcelFile(file_path)

all_records = []

# Helper to parse names and numbers from a row
def get_student_info(row):
    student_no = None
    student_name = None
    selected_class_col = None
    for col_idx in range(2, 12):
        cell_val = row.iloc[col_idx]
        if pd.isna(cell_val):
            continue
        cell_str = str(cell_val).strip()
        match = re.match(r'^(\d+)\s*번\s*([^\s]+)$', cell_str)
        if match:
            student_no = int(match.group(1))
            student_name = match.group(2).strip()
            selected_class_col = col_idx - 1 # Col 2 is Class 1, Col 11 is Class 10
            break
    return student_no, student_name, selected_class_col

def clean_timestamp(val):
    if isinstance(val, pd.Timestamp):
        return val
    val_str = str(val).strip()
    val_str = val_str.replace('오전', 'AM').replace('오후', 'PM')
    parts = val_str.split(' ')
    if len(parts) >= 3:
        date_part = "-".join([p.replace('.', '') for p in parts[:3]])
        time_part = " ".join(parts[3:])
        val_str = f"{date_part} {time_part}"
    try:
        return pd.to_datetime(val_str)
    except:
        try:
            return pd.to_datetime(str(val).strip().replace('.', '-'), errors='coerce')
        except:
            return pd.to_datetime(val, errors='coerce')

for sname in xl.sheet_names:
    if '설문지 응답' not in sname:
        continue
    df = xl.parse(sname)
    
    ans_indices = []
    for col_idx, col_name in enumerate(df.columns):
        if any(q in str(col_name) for q in ['16.', '17.', '18.', '19.', '20.']):
            ans_indices.append(col_idx)
            
    if len(ans_indices) != 5:
        if sname == '설문지 응답 시트5':
            ans_indices = [2, 3, 4, 5, 6]
        else:
            ans_indices = [12, 13, 14, 15, 16]
            
    for idx, row in df.iterrows():
        ts = row.iloc[0]
        if pd.isna(ts):
            continue
            
        no, name, deduced_cls = get_student_info(row)
        # Skip if name is not found (corrupt rows with only class/timestamp)
        if not name:
            continue
            
        # Determine class: prefer deduced_cls from name column, fallback to class cell
        cls = deduced_cls
        if not cls:
            class_cell = row.iloc[1]
            if pd.notna(class_cell):
                class_str = str(class_cell).strip()
                class_match = re.search(r'(\d+)\s*반', class_str)
                if class_match:
                    cls = int(class_match.group(1))
                    
        if not cls:
            continue
            
        ans16 = row.iloc[ans_indices[0]]
        ans17 = row.iloc[ans_indices[1]]
        ans18 = row.iloc[ans_indices[2]]
        ans19 = row.iloc[ans_indices[3]]
        ans20 = row.iloc[ans_indices[4]]
        
        all_records.append({
            'timestamp': clean_timestamp(ts),
            'class': cls,
            'no': no,
            'name': name,
            'ans16': ans16,
            'ans17': ans17,
            'ans18': ans18,
            'ans19': ans19,
            'ans20': ans20,
            'sheet': sname,
            'row_idx': idx
        })

print(f"Total valid submission records loaded: {len(all_records)}")

# Group by student (class, no, name) and keep the LATEST submission by timestamp
latest_submissions = {}
for rec in all_records:
    key = (rec['class'], rec['no'], rec['name'])
    if key not in latest_submissions:
        latest_submissions[key] = rec
    else:
        ts_rec = rec['timestamp']
        ts_curr = latest_submissions[key]['timestamp']
        if pd.notna(ts_rec) and pd.notna(ts_curr):
            if ts_rec > ts_curr:
                latest_submissions[key] = rec
        elif pd.notna(ts_rec):
            latest_submissions[key] = rec

print(f"Total unique students submitted: {len(latest_submissions)}")

# Define blank or placeholder values
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
    if len(val_str) == 1 and val_str in ['.', '-', '?', ' ']:
        return True
    return False

# Analysis
q_keys = ['ans16', 'ans17', 'ans18', 'ans19', 'ans20']
q_labels = {
    'ans16': '16번 (세런디피티 개념)',
    'ans17': '17번 (연구 수행자 이름)',
    'ans18': '18번 (플레밍 개발동기 약했던 까닭)',
    'ans19': '19번 (페니실린 박테리아 억제 까닭)',
    'ans20': '20번 (그람 음성균 효과 없는 까닭)'
}

blank_students_per_q = {q: [] for q in q_keys}

for key, sub in latest_submissions.items():
    cls, no, name = key
    for q in q_keys:
        val = sub[q]
        if is_blank(val):
            blank_students_per_q[q].append({
                'class': cls,
                'no': no,
                'name': name,
                'raw_val': str(val).strip() if pd.notna(val) else 'NaN',
                'sheet': sub['sheet'],
                'row': sub['row_idx']
            })

# Print results for each question
for q in q_keys:
    print(f"\n=== {q_labels[q]} 미작성 학생 ({len(blank_students_per_q[q])}명) ===")
    sorted_students = sorted(blank_students_per_q[q], key=lambda x: (x['class'], x['no']))
    for s in sorted_students:
        print(f"  {s['class']}반 {s['no']}번 {s['name']} (입력값: '{s['raw_val']}', Sheet: {s['sheet']}, Row: {s['row']})")

# Students who didn't write answers to ALL 5 questions
all_blank_students = []
for key, sub in latest_submissions.items():
    cls, no, name = key
    all_b = True
    for q in q_keys:
        if not is_blank(sub[q]):
            all_b = False
            break
    if all_b:
        all_blank_students.append({
            'class': cls,
            'no': no,
            'name': name,
            'timestamp': sub['timestamp']
        })

print(f"\n=== 모든 문항 미작성 학생 ({len(all_blank_students)}명) ===")
for s in sorted(all_blank_students, key=lambda x: (x['class'], x['no'])):
    print(f"  {s['class']}반 {s['no']}번 {s['name']} (Timestamp: {s['timestamp']})")
