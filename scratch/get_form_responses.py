import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'
form_id = '1eWucmez2c6h1qT7nwuA0by_GwQaJS8N-N8M0wLZ_qAE'

try:
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    
    # Discovery service for Forms API requires v1
    # Using 'forms' service
    forms_service = build('forms', 'v1', credentials=creds)
    
    # Get form responses
    print(f"Retrieving responses for Form ID: {form_id}...")
    res = forms_service.forms().responses().list(formId=form_id).execute()
    responses = res.get('responses', [])
    print(f"Total responses in Google Form: {len(responses)}")
    
    if responses:
        print("Last 5 responses in Form:")
        for r in responses[-5:]:
            submit_time = r.get('createTime')
            response_id = r.get('responseId')
            answers = r.get('answers', {})
            # Extract name and class if possible
            print(f"  Response ID: {response_id} at {submit_time}")
            # print some answer keys
            for key, val in list(answers.items())[:2]:
                text_answers = val.get('textAnswers', {}).get('answers', [])
                if text_answers:
                    print(f"    {key}: {text_answers[0].get('value')}")
    else:
        print("No responses found in Form.")
        
except Exception as e:
    print("Error:", e)
