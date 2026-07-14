import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# 스프레드시트 ID
SPREADSHEET_ID = "1KgpBoxrQUwiqA86qJr9eB6KAckSNfuC7QJea-m7qiSg"

def get_credentials():
    token_files = ["token.json", "token_calendar.json", "token_tasks.json", "token_gmail.json"]
    for token_file in token_files:
        if os.path.exists(token_file):
            try:
                creds = Credentials.from_authorized_user_file(token_file)
                if creds and creds.valid:
                    return creds
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    return creds
            except Exception as e:
                pass
    return None

def main():
    creds = get_credentials()
    if not creds:
        print("No valid credentials found.")
        return
        
    try:
        service = build("sheets", "v4", credentials=creds)
        # Sheet1 A3:T45 범위 (번호와 성명)
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="'Sheet1'!A3:T45"
        ).execute()
        
        values = result.get("values", [])
        
        roster = {}
        for b in range(1, 11):
            roster[b] = []
            
        for row in values:
            for b in range(1, 11):
                num_col = (b - 1) * 2
                name_col = (b - 1) * 2 + 1
                
                if num_col < len(row) and name_col < len(row):
                    num_val = row[num_col]
                    name_val = row[name_col]
                    
                    if num_val and name_val:
                        try:
                            num = int(num_val)
                            name = str(name_val).strip()
                            if name and "인원" not in name and "계" not in name:
                                roster[b].append({
                                    "num": num,
                                    "name": name
                                })
                        except ValueError:
                            pass
        
        # 반별로 번호 정렬
        for b in range(1, 11):
            roster[b].sort(key=lambda x: x["num"])
            
        # JSON 파일로 저장
        with open("scratch/roster.json", "w", encoding="utf-8") as out:
            json.dump(roster, out, ensure_ascii=False, indent=2)
            
        print("Successfully saved roster to scratch/roster.json")
        print(f"Total classes parsed: {len(roster)}")
        for b in range(1, 11):
            print(f"Class {b}: {len(roster[b])} students")
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
