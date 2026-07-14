import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions.xlsx"
df0 = pd.read_excel(file_path, sheet_name=0)
df1 = pd.read_excel(file_path, sheet_name=1)

print("Sheet 0 shape:", df0.shape)
print("Sheet 1 shape:", df1.shape)

# Check sheet names from ExcelFile
xl = pd.ExcelFile(file_path)
print("Pandas sheet names list:")
for i, s in enumerate(xl.sheet_names):
    print(f"  {i}: {s}")

# Check columns for name in sheet 0 and sheet 1
# In sheet 0, column index 1 is "반을 선택해 주세요."
# Let's extract (timestamp, class, name) for both sheets
def extract_submissions(df):
    records = []
    # Columns 2 to 11 are "자신의 이름을 선택해 주세요.", "자신의 이름을 선택해 주세요. 2", ...
    # We find the non-null value among these columns for each row
    for idx, row in df.iterrows():
        ts = row.iloc[0]
        cls = row.iloc[1]
        name_val = None
        for col_idx in range(2, 12):
            val = row.iloc[col_idx]
            if pd.notna(val) and str(val).strip() != "":
                name_val = str(val).strip()
                break
        records.append({'timestamp': ts, 'class': cls, 'name_raw': name_val})
    return pd.DataFrame(records)

rec0 = extract_submissions(df0)
rec1 = extract_submissions(df1)

print("\nSample records from Sheet 0:")
print(rec0.head(5))
print("\nSample records from Sheet 1:")
print(rec1.head(5))

# Check if there are any records in Sheet 1 (df1) that are NOT in Sheet 0 (df0)
# We can check by timestamp
ts0 = set(rec0['timestamp'].dropna())
ts1 = set(rec1['timestamp'].dropna())

diff = ts1 - ts0
print(f"\nTimestamps in Sheet 1 but not in Sheet 0 (count: {len(diff)}):")
print(list(diff)[:10])

# Check if there are any records in Sheet 1 that have class and name not in Sheet 0
rec0_set = set(rec0.apply(lambda r: (str(r['class']).strip(), str(r['name_raw']).strip()), axis=1))
rec1_set = set(rec1.apply(lambda r: (str(r['class']).strip(), str(r['name_raw']).strip()), axis=1))
diff_names = rec1_set - rec0_set
print(f"\nClass/Names in Sheet 1 but not in Sheet 0 (count: {len(diff_names)}):")
print(diff_names)
