import os

TARGET = "daily_news.py"

with open(TARGET, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
c1 = "import requests\n# import notebooklm_auto (NLM ?먮룞??以묐떒)"
r1 = """import requests
import markdown
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
# import notebooklm_auto (NLM ?먮룞??以묐떒)"""
content = content.replace(c1, r1)

# 2. Def upload_to_gdoc
c2 = "def send_telegram_alert(file_name, file_path, is_weekend=False):"
r2 = """def upload_to_gdoc(md_path):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    FOLDER_ID = "1aXM_giZCkZVKnFrDK6tRQZly6e2JvTUX"
    creds = None
    token_path = os.path.join(BASE_DIR, 'token.json')
    if os.path.exists(token_path):
        cr = Credentials.from_authorized_user_file(token_path, SCOPES)
        if cr and cr.expired and cr.refresh_token:
            cr.refresh(Request())
            with open(token_path, 'w') as token:
                token.write(cr.to_json())
        creds = cr
    if not creds:
        log_message("?좑툘 援ш? ?쒕씪?대툕 ?몄쬆 ?뺣낫(token.json)媛 ?놁뒿?덈떎.")
        return None

    try:
        drive_service = build('drive', 'v3', credentials=creds)
        with open(md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
            
        try:
            html_text = markdown.markdown(md_text, extensions=['extra'])
        except Exception as me:
            log_message(f"Markdown ?뚯떛 ?ㅻ쪟, ?쇰컲 ?띿뒪?몃줈 ?쒕룄?⑸땲?? {me}")
            html_text = md_text

        html_path = md_path.replace('.md', '.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_text)
            
        file_metadata = {
            'name': os.path.basename(md_path).replace('.md', ''),
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [FOLDER_ID]
        }
        media = MediaFileUpload(html_path, mimetype='text/html', resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='webViewLink').execute()
        return file.get('webViewLink')
    except Exception as e:
        log_message(f"?좑툘 援ш? 臾몄꽌 ?낅줈???ㅽ뙣: {e}")
        return None

def send_telegram_alert(file_name, file_path, is_weekend=False, doc_link=None):"""
content = content.replace(c2, r2)

# 3. Message format
c3 = """        prefix = "二쇰쭚 湲濡쒕쾶 寃쎌젣 ?댁뒪" if is_weekend else "寃쎌젣 ?댁뒪"
        text = f"?벐 [{prefix} ?띿뒪??異붿텧 ?꾨즺]\\n\\n?ㅻ뒛??嫄곗떆寃쎌젣 ?띿뒪???뚯씪({file_name}) 異붿텧???꾨즺?섏뿀?듬땲??\\n吏곸젒 NotebookLM???낅줈?쒗븯???ㅻ뵒??酉곕? ?앹꽦??二쇱꽭??""""
r3 = """        prefix = "二쇰쭚 湲濡쒕쾶 寃쎌젣 ?댁뒪" if is_weekend else "寃쎌젣 ?댁뒪"
        link_text = f"\\n\\n?뵕 援ш? 臾몄꽌 留곹겕:\\n{doc_link}" if doc_link else ""
        text = f"?벐 [{prefix} ?앹꽦 ?꾨즺]\\n\\n?ㅻ뒛??嫄곗떆寃쎌젣 臾몄꽌({file_name})媛 援ш? ?쒕씪?대툕????λ릺?덉뒿?덈떎.{link_text}\\n吏곸젒 NotebookLM???댁슜??蹂듭궗?섏뿬 ?ㅻ뵒??由щ럭瑜??앹꽦??二쇱꽭??" """
content = content.replace(c3, r3)

# 4. generate_daily_news call
c4 = """    # ?쨼 NotebookLM ?곕룞? 以묐떒?⑸땲??(?섎룞 ?묒뾽???꾪빐 ?뚯씪 ?앹꽦 ?뚮┝留??꾩넚)
    # ?붾젅洹몃옩 ?뚮┝ ?꾩넚
    send_telegram_alert(file_name, file_path)"""
r4 = """    # 援ш? 臾몄꽌濡??낅줈??    doc_link = upload_to_gdoc(file_path)

    # ?쨼 NotebookLM ?곕룞? 以묐떒?⑸땲??(?섎룞 ?묒뾽???꾪빐 ?뚯씪 ?앹꽦 ?뚮┝留??꾩넚)
    # ?붾젅洹몃옩 ?뚮┝ ?꾩넚
    send_telegram_alert(file_name, file_path, doc_link=doc_link)"""
content = content.replace(c4, r4)

# 5. generate_weekend_news call
c5 = """    # ?쨼 NotebookLM ?곕룞? 以묐떒?⑸땲??    send_telegram_alert(file_name, file_path, is_weekend=True)"""
r5 = """    # 援ш? 臾몄꽌濡??낅줈??    doc_link = upload_to_gdoc(file_path)

    # ?쨼 NotebookLM ?곕룞? 以묐떒?⑸땲??    send_telegram_alert(file_name, file_path, is_weekend=True, doc_link=doc_link)"""
content = content.replace(c5, r5)

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully.")
