import openpyxl
import pandas as pd
import os

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026학년도 1학년 전체명렬.xlsx"

try:
    df = pd.read_excel(file_path)
    # Print the columns to check
    cols = df.columns.tolist()
    
    with open("scratch/grade1_roster_parsed.txt", "w", encoding="utf-8") as f:
        f.write("Columns:\n")
        f.write(", ".join(cols) + "\n\n")
        
        # Let's print out the data in a readable form
        for index, row in df.iterrows():
            row_vals = []
            for col in df.columns:
                val = str(row[col]) if pd.notna(row[col]) else ""
                row_vals.append(f"{col}:{val}")
            f.write(f"Row {index}: " + " | ".join(row_vals) + "\n")
            
    print("Done. Check scratch/grade1_roster_parsed.txt")
except Exception as e:
    print("Error:", e)
