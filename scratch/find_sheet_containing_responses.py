import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'
creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
sheets_service = build('sheets', 'v4', credentials=creds)

all_ids = [
    '1cfiC_iNJ2j6SEh-3FTRXX4qzhtPJBwS-1Tq3vSQwId4',
    '1PjHn4e8oju-9otOZjqd4uX5Hl1glcdn3UtV-XaRnFYs',
    '1pdFkUGIBmZyvWwIRJmHH3mXbCgPLOLr6D3zCIfvMfIY',
    '1uwzh7t2K5igDR3UX5OYfQl2-tBqurlD9opzJCjsQuiI',
    '1w8yis9cpjyFW9E8TAdF_s2giChd6yhp9MdBE36N-IL0',
    '1922fyVktC8rL7q6H_HEHALQzrLoSuAV01XdHVwUCCIv',
    '1jpxnsyyg8z4iDxxSz_vLmoSniqc-gV4E_CHAK-RjNLT',
    '1yHEJsvgtQ6crum5H3PuKZzoQzEOxUhs5tT1_WUJzGr8',
    '1kgp-qF7pwekx_VZ_1kVZ4XMbNZGYbL_FlXOJI6E8UeU',
    '1K08vJ8dfulLZV315zAYoBzL6nXXcF8eko3frjZywA88',
    '1NrVqbyfsrEghfM42vIJgW5_ayVhM5jV2x8BIIG4NgNo',
    '1q3BLh2J3pmKm9_Iv1mKdnOy2dI4h4PpYg49NAgEyQFc',
    '1CtFAtJnysSLa1JWExpPXzImvCxvvZcDU4OuiLqV0p10',
    '1cDTH4hXGN0e-ZA3rkBUjStRwjE4GRyyvmKxkBbG7ocM',
    '1irIsLFYCggNyW5WBolfKW0IzA7_pjj7F6nSh7mwrOZc',
    '1d9lwuABtuKW6xAoB7BpJv-MJ8C3OS5mOu35UZVxIpx0',
    '1mo8VwNcAPCOw0julQWpvMFUvHHbtwAVY0DHSFAaQcvk',
    '1h2MeRaFt248SMFZyPZ-RPsL6jgvzMWRdoRRoS5DrmRs',
    '1njSdSIs2jYu74SASzNBJrVVH9KQJ4kDJDyIyHMiZw8A',
    '111IXv4GOBukEUk6c_h8-AMuh0fKF_0Q0bt4okYFt5WA',
    '1UAO-OHKMDtc8J50pNYcB4SGthiLEJtvVFoOZihjwGWw',
    '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU',
    '1UkV1Vc_8m_vO7bzhS5JpjE4SwIZu8Ocs24rS7PPX5EE',
    '1EVwwxdU4rDRuqTHDSB-1cn5Bx85rqA_uo3disf4uVNo',
    '1uXPT8g0wc8-Ryufwk3yTr2RmX5TMraW4v5t9mBxpKYw',
    '144Sj-6EJ8KtIBSJJnaIUZnY3sMVEVNCxs5xa9f555wo',
    '1N2h9VzppwepaU0vLWNlZ8aTHeJ3vu_6Kfvwx7i-51Vk',
    '1zyIRImgmdR-ocr3gqrmqgDR1Nzt92c8jZUd5sZYs_z8',
    '1AdVPqNwz7RA_CUlqn0wvQwNhlRCgRG45KyqHhLbt20c',
    '1C4SmIseUA28iTVmYeYcteukRL9aXBcdcK_NvnuSILDj',
    '1EReikad-ObOGz1eQBRrkcWhAq-ViHL38BmL6uCI7mqc',
    '1iIM8J_tG6-E77bjvkTX5HJpJJnCS6WHl7hwTmTWJync',
    '1QKzh25G-HBDLrlTXZT8T3WbofpRvw468gPamzqBbYd7',
    '1-TMsohbrUwaifTPpnSbrlU72nOjqiPIvYbKluSjLBsk',
    '1ii7mLu_NrjQf5dWslxXC1-mzDB4Z4dx-ipeO9itKZas',
    '19bFs6QW1-F3ec8RDaEvJkNqGW3htaLxracavLA9YXSP',
    '12bXJl_SRj8mVIZBBADWix8ZZ5Rh7XKFodH62iGzDTF8'
]

print("Scanning spreadsheets for '수행평가_응답' sheet...")
for sid in all_ids:
    try:
        meta = sheets_service.spreadsheets().get(spreadsheetId=sid).execute()
        title = meta.get('properties', {}).get('title')
        sheets = [s.get('properties', {}).get('title') for s in meta.get('sheets', [])]
        if '수행평가_응답' in sheets or any('수행평가' in s for s in sheets):
            print(f"MATCH FOUND!")
            print(f"  ID: {sid}")
            print(f"  Title: {title}")
            print(f"  Sheets: {sheets}")
            # check the row count
            for s in sheets:
                if '수행평가_응답' in s or '응답' in s:
                    val_res = sheets_service.spreadsheets().values().get(
                        spreadsheetId=sid, range=f"'{s}'!A:J"
                    ).execute()
                    print(f"    Sheet '{s}' has {len(val_res.get('values', []))} rows")
    except Exception:
        # Not a spreadsheet or no permission
        pass
