import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = "scratch/submissions.xlsx"

try:
    # Read the first sheet by index
    df = pd.read_excel(file_path, sheet_name=0)
    print("Successfully read sheet index 0 with pandas!")
    print("Shape:", df.shape)
    print("Columns:")
    print(df.columns.tolist())
    print("\nFirst 10 rows:")
    print(df.head(10).to_string())
except Exception as e:
    print("Error reading sheet index 0:", e)
