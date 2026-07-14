import os
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes for Google Tasks API
def add_google_task(title, due_time=None):
    """Adds a task to the default Google Tasks list.
    Args:
        title (str): Task title.
        due_time (str, optional): RFC3339 timestamp, e.g., '2026-07-08T08:30:00+09:00'
    """
    # Ensure credentials file exists
    creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    if not os.path.exists(creds_path):
        raise FileNotFoundError('Google API credentials.json not found at {}'.format(creds_path))

    flow = InstalledAppFlow.from_client_secrets_file(creds_path, ['https://www.googleapis.com/auth/tasks'])
    creds = flow.run_local_server(port=0)
    service = build('tasks', 'v1', credentials=creds)

    task_body = {'title': title}
    if due_time:
        task_body['due'] = due_time

    result = service.tasks().insert(tasklist='@default', body=task_body).execute()
    print('Task created: {}'.format(result.get('title')))

if __name__ == '__main__':
    # Task for continuing work on next Monday at 08:30
    add_google_task('Continue 2학년 문학 수행평가 웹앱 작업', due_time='2026-07-08T08:30:00+09:00')
