import os
import sys
import json
import csv
import datetime
import webview
from dotenv import load_dotenv
import google.generativeai as genai

def get_executable_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = get_executable_dir()
    return os.path.join(base_path, relative_path)

class PortalApi:
    def __init__(self):
        self.exe_dir = get_executable_dir()
        self.csv_path = os.path.join(self.exe_dir, 'students.csv')
        self.json_path = os.path.join(self.exe_dir, 'praises.json')
        load_dotenv(os.path.join(self.exe_dir, '.env'))

    def get_students(self):
        students = []
        if not os.path.exists(self.csv_path):
            try:
                # Create a sample students.csv if it doesn't exist
                with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['학번', '이름', '학부모연락처'])
                    writer.writerow(['10301', '홍길동', '010-1234-5678'])
                    writer.writerow(['10302', '이순신', '010-8765-4321'])
            except Exception as e:
                print("Error creating sample students.csv:", e)
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    students.append({
                        'id': row.get('학번', '').strip(),
                        'name': row.get('이름', '').strip(),
                        'phone': row.get('학부모연락처', '').strip()
                    })
        except Exception as e:
            print("Error reading students.csv:", e)
        return students

    def get_praises(self):
        if not os.path.exists(self.json_path):
            return []
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print("Error reading praises.json:", e)
            return []

    def save_praise(self, student_id, name, phone, content):
        praises = self.get_praises()
        new_praise = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'student_id': student_id,
            'name': name,
            'phone': phone,
            'content': content,
            'status': 'pending'  # pending, sent, failed
        }
        praises.append(new_praise)
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(praises, f, ensure_ascii=False, indent=2)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_praise(self, idx):
        praises = self.get_praises()
        if 0 <= idx < len(praises):
            praises.pop(idx)
            try:
                with open(self.json_path, 'w', encoding='utf-8') as f:
                    json.dump(praises, f, ensure_ascii=False, indent=2)
                return {'success': True}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        return {'success': False, 'error': 'Index out of bounds'}

    def refine_praise(self, brief_text):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return {'success': False, 'error': 'GEMINI_API_KEY not found in .env'}
        
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
역할: 고등학교 담임선생님이 학부모에게 보내는 가정통신 칭찬 알림 문자 작성 전문가.
입력문구: "{brief_text}"

위의 입력문구는 선생님이 바쁜 학교 생활 중에 자녀(학생)의 칭찬할 만한 행동을 아주 짧고 간략하게 기록한 것입니다. 
이를 학부모님이 읽었을 때 자녀에 대해 깊은 자부심과 보람을 느끼고, 담임 선생님의 애정을 느낄 수 있도록 문장을 정중하고 따뜻하며 격식 있는 어조로 다듬어서 확장해 주세요.

조건:
1. 문장은 2~3문장 내외로 너무 길지 않게 다듬어 주세요.
2. 부모님이 자녀를 격려할 수 있는 긍정적인 메시지를 포함해 주세요.
3. 텍스트 본문만 출력하세요 (기타 설명이나 따옴표는 제거).
"""
            response = model.generate_content(prompt)
            return {'success': True, 'refined_text': response.text.strip()}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def verify_password(self, password):
        load_dotenv(os.path.join(self.exe_dir, '.env'))
        correct_password = os.getenv('APP_PASSWORD', 'jinhae1912').strip()
        if password == correct_password:
            return {'success': True}
        return {'success': False, 'error': '올바르지 않은 교직원 비밀번호입니다.'}

    def fetch_neis_meal(self, date_str):
        url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?Type=json&ATPT_OFCDC_SC_CODE=S10&SD_SCHUL_CODE=9380026&MLSV_YMD={date_str}"
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = response.read().decode('utf-8')
                return {'success': True, 'data': json.loads(res_data)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def fetch_neis_schedule(self, from_date, to_date):
        url = f"https://open.neis.go.kr/hub/SchoolSchedule?Type=json&ATPT_OFCDC_SC_CODE=S10&SD_SCHUL_CODE=9380026&AA_FROM_YMD={from_date}&AA_TO_YMD={to_date}"
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = response.read().decode('utf-8')
                return {'success': True, 'data': json.loads(res_data)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def fetch_neis_timetable(self, date_str, grade, class_nm):
        url = f"https://open.neis.go.kr/hub/hisTimetable?Type=json&ATPT_OFCDC_SC_CODE=S10&SD_SCHUL_CODE=9380026&ALL_TI_YMD={date_str}&GRADE={grade}&CLASS_NM={class_nm}"
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = response.read().decode('utf-8')
                return {'success': True, 'data': json.loads(res_data)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    base_dir = get_resource_path('.')
    html_path = os.path.join(base_dir, 'Jinhae_Portal.html')
    
    api = PortalApi()
    
    # Create the webview window pointing to our HTML and binding the API
    window = webview.create_window(
        title='진해고등학교 스마트 통합 PWA 포털',
        url=html_path,
        width=1280,
        height=850,
        min_size=(1000, 700),
        resizable=True,
        js_api=api
    )
    
    # Start webview with the built-in HTTP server enabled
    webview.start(http_server=True)
