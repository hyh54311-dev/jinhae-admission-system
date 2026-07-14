import openpyxl
import pandas as pd

file_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 출석부\2026. 3학년부 명렬표.xlsx"

try:
    xl = pd.ExcelFile(file_path)
    print("Sheet names:", xl.sheet_names)
except Exception as e:
    print("Error reading with pandas:", e)
    try:
        wb = openpyxl.load_workbook(file_path, read_only=True)
        print("Sheet names (openpyxl):", wb.sheetnames)
    except Exception as e2:
        print("Error reading with openpyxl:", e2)
