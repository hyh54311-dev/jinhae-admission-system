import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'
candidate_ids = [
    '1EVwwxdU4rDRuqTHDSB-1cn5Bx85rqA_uo3disf4uVNo',
    '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU',
    '1KgpBoxrQUwiqA86qJr9eB6KAckSNfuC7QJea-m7qiSg',
    '1UkV1Vc_8m_vO7bzhS5JpjE4SwIZu8Ocs24rS7PPX5EE',
    '1eWucmez2c6h1qT7nwuA0by_GwQaJS8N-N8M0wLZ_qAE',
    '1zQNEw9JkZDiEzirjMaVb0xvcqDRb1iLSLCidgU6xOvc',
    '1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY',
    '1VU8Kwa7c5wD0LlFaQaHoAmVt-Il9saOt6e9iGXqQReQ',
    '1UAO-OHKMDtc8J50pNYcB4SGthiLEJtvVFoOZihjwGWw',
    '1JCrVEDhivEJyI4KZD1dt5SRcBECjsHOx0kuD35Usqp4',
    '1zsN8_986W-8Hm2KakhR6jaDhksyp2eJmLcBA6dvJow0',
    '1Qa3IGRd0sfgyWwZTBxdu1K0JO07bI9RPoK3lhbV9gmk',
    '14Wk8jEQadn0r9ImKdxKknTi0Afq88Bry_iQNfZzuKFo',
    '1CYpA22XTSbveouDcSFGYbN_2TUHESNWsA5gQ5mrrbpM',
    '1yIK6_q1g3O83MeC77kUt2cOMKa5sWHy8jH8QX8uhmKs',
    '1yveIiHCja_QnVeNc4NUwNaV3Fu9zftdSiewuY9xT6a8'
]

try:
    creds = Credentials.from_authorized_user_file(token_path)
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    print("Checking Candidate Spreadsheet IDs:")
    for spreadsheet_id in candidate_ids:
        try:
            meta = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            title = meta.get('properties', {}).get('title')
            print(f"ID: {spreadsheet_id} -> Title: {title}")
        except Exception as e:
            print(f"ID: {spreadsheet_id} -> Error: {e}")
            
except Exception as e:
    print("Outer Error:", e)
