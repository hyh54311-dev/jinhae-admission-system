import pandas as pd
import os

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2학년 명렬.xlsx"

print("File exists:", os.path.exists(file_path))

try:
    df = pd.read_excel(file_path)
    cols = df.columns.tolist()
    
    with open("scratch/grade2_roster_parsed.txt", "w", encoding="utf-8") as f:
        f.write("Columns:\n")
        f.write(", ".join(cols) + "\n\n")
        
        for index, row in df.iterrows():
            row_vals = []
            for col in df.columns:
                val = str(row[col]) if pd.notna(row[col]) else ""
                row_vals.append(f"{col}:{val}")
            f.write(f"Row {index}: " + " | ".join(row_vals) + "\n")
            
    print("Done. Check scratch/grade2_roster_parsed.txt")
except Exception as e:
    print("Error:", e)
