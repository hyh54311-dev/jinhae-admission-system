import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']

def main():
    creds = None
    token_path = 'token_tasks.json'
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("理쒖큹 ?몄쬆???꾪빐 釉뚮씪?곗? 李쎌씠 ?대┰?덈떎. Google 怨꾩젙?쇰줈 濡쒓렇?명빐二쇱꽭??")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('tasks', 'v1', credentials=creds)
        
        # Call the Tasks API
        results = service.tasklists().list(maxResults=10).execute()
        items = results.get('items', [])
        
        if not items:
            print('No task lists found.')
            return
            
        print('--- 援ш? ?쒖뒪??????紐⑸줉) ?뺤씤 ?꾨즺 ---')
        for item in items:
            print(f"\n[ Task List: {item['title']} ]")
            # Fetch tasks in this list
            tasks_result = service.tasks().list(tasklist=item['id'], showHidden=False).execute()
            tasks = tasks_result.get('items', [])
            if not tasks:
                print("  ???쇱씠 ?놁뒿?덈떎.")
            for task in tasks:
                status = "[x]" if task.get('status') == 'completed' else "[ ]"
                due = task.get('due', '')
                due_str = f" (吏꾪뻾 湲고븳: {due[:10]})" if due else ""
                print(f"  {status} {task['title']}{due_str}")
                
    except Exception as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()
