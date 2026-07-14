import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions.xlsx"
df = pd.read_excel(file_path, sheet_name=0)

# Columns 12 to 16 (0-indexed: 12, 13, 14, 15, 16) are the answers
print("Checking nulls or empty answers in submissions:")
answer_cols = [12, 13, 14, 15, 16]
for c_idx in answer_cols:
    col_name = df.columns[c_idx]
    null_count = df[col_name].isna().sum()
    empty_str_count = (df[col_name].astype(str).str.strip() == '').sum()
    unique_vals = df[col_name].dropna().unique()
    print(f"  Col {c_idx} ({col_name[:20]}...): nulls={null_count}, empty_str={empty_str_count}")
    # Print if there are short answers like '.', '-', ' '
    short_answers = [val for val in unique_vals if len(str(val).strip()) <= 3]
    if short_answers:
        print(f"    Short answers: {short_answers[:15]}")
