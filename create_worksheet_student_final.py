import os
import io
import json
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

FOLDER_ID = '1lxKMH8ssyeHSEv3rI2a24pD8qCT6FXo1'
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return creds

def create_doc(service, title, folder_id, html_content):
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [folder_id]
    }
    encoded_html = html_content.encode('utf-8')
    media = MediaIoBaseUpload(io.BytesIO(encoded_html), mimetype='text/html', resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    print(f"Created: {title}\nLink: {file.get('webViewLink')}\n")
    return file

def load_image_base64(path):
    import urllib.request
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"Failed to load image at {path}: {e}")
        return ""

# The generated images paths
IMG1_PATH = r"C:\Users\admin\.gemini\antigravity\brain\541b9e54-1667-4acf-816f-988959751015\gyuwonga_1775180410420.png"
IMG2_PATH = r"C:\Users\admin\.gemini\antigravity\brain\541b9e54-1667-4acf-816f-988959751015\inhyeon_1775180425634.png"

img1_b64 = load_image_base64(IMG1_PATH)
img2_b64 = load_image_base64(IMG2_PATH)

STUDENT_HTML = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: 'Malgun Gothic', 'Dotum', sans-serif; line-height: 2.2; font-size: 11.5pt; color: #2c3e50; padding: 20px; }}
  h1 {{ text-align: center; color: #000; margin-bottom: 20px; font-size: 15pt; }}
  .header-info {{ text-align: left; font-size: 11pt; font-weight: bold; margin-bottom: 40px; border-bottom: 2px solid #333; padding-bottom: 15px; }}
  h2 {{ color: #2980b9; margin-top: 50px; font-size: 14pt; border-bottom: 2px solid #2980b9; padding-bottom: 10px; margin-bottom: 30px; }}
  h3 {{ color: #8e44ad; font-size: 12pt; border-left: 5px solid #8e44ad; padding-left: 10px; margin-top: 40px; margin-bottom: 20px; }}
  .box {{ border: 1px solid #7f8c8d; padding: 25px; background-color: #f8f9fa; margin-bottom: 30px; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 40px; margin-top: 20px; }}
  th, td {{ border: 1px solid #bdc3c7; padding: 15px; text-align: left; font-size: 11pt; }}
  th {{ background-color: #ecf0f1; text-align: center; font-weight: bold; }}
  .question {{ font-weight: bold; margin-top: 35px; font-size: 11.5pt; color: #34495e; }}
  .answer {{ border-bottom: 1px solid #95a5a6; margin-top: 30px; padding-bottom: 35px; min-height: 40px; }}
  .page-break {{ page-break-before: always; }}
  .img-container {{ text-align: center; margin: 40px 0; }}
  .img-container img {{ max-width: 65%; height: auto; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); border: 2px solid #ddd; }}
  ul, li {{ margin-top: 10px; margin-bottom: 10px; }}
  .space-large {{ height: 60px; }}
</style>
</head>
<body>

  <h1>[?숈뒿吏] 2027 ?섎뒫?밴컯 臾명븰 : 媛덈옒蹂듯빀 05</h1>
  <div class="header-info">
    3?숇뀈 <u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>諛?<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>踰?&nbsp;&nbsp;&nbsp; ?대쫫: __________________
  </div>

  <h2>[1] ?묓뭹 ?꾨꼍 ?대?: ?덈궃?ㅽ뿄, &lt;洹쒖썝媛(?ⓩⓩ춯)&gt;</h2>
  <div class="img-container">
    <img src="data:image/png;base64,{img1_b64}" alt="洹쒖썝媛 ?쇰윭?ㅽ듃">
    <p style="font-size: 9pt; color: #7f8c8d; margin-top: 10px;">(?낆닔怨듬갑???몃줈?怨??쒖쓣 ?щ옒???ъ씤??紐⑥뒿)</p>
  </div>
  
  <div class="box">
    <p>?곕━?섎씪 <strong>理쒖큹???ъ꽦 媛??/strong>濡? 遊됯굔?곸씤 媛遺?μ젣 ?ы쉶 ?띿뿉???⑦렪?먭쾶 踰꾨┝諛쏆? ?ъ꽦??????怨??ы뵒???덉젅?섍쾶 ?몃옒??洹쒕갑 媛?ъ엯?덈떎. ?ㅼ뼇??臾명븰???μ튂(?섏궗踰?? 媛먯젙??蹂??怨쇱젙??以묒떖?쇰줈 媛먯긽?⑸땲??</p>
    <ul>
      <li><strong>媛덈옒:</strong> ?대갑 媛??洹쒕갑 媛??, ?묐컲 媛?? ?쒖젙 媛??/li>
      <li><strong>?깃꺽:</strong> ?먮쭩?? ?좎긽?? ?쒗깂?? 怨좊갚??/li>
    </ul>
  </div>

  <h3>???붿옄???뺤꽌 ?뚯븙怨??쒓컙???먮쫫 (?議?</h3>
  <table>
    <tr>
      <th style="width: 20%;">援щ텇</th>
      <th style="width: 40%;">怨쇨굅 (?됰났/?꾨쫫?ㅼ?)</th>
      <th style="width: 40%;">?꾩옱 (鍮꾩븷/珥덈씪??</th>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: bold;">?듭떖 ?쒖뼱</td>
      <td><strong>?쇱삤?댄뙏 (訝됦틪雅뚦뀵):</strong> 15~16??臾대졄<br><strong>?ㅻ퉰?덈굹 (?らБ窈붼궍):</strong> ?덇컳?????쇰?? 怨좎슫 ?쇨뎬<br><strong>援곗옄?멸뎄 (?쎾춴也썽?:</strong> ?뚮???援곗옄??醫뗭? 吏?/td>
      <td><strong>硫대ぉ媛利?(?®쎅??냾):</strong> ?숈뼱??諛됱궡?ㅻ읇寃?蹂??紐⑥뒿<br><strong>?낆닔怨듬갑 (?ⓨ츍令뷸댛):</strong> 鍮덈갑???濡?吏??br><strong>諛깆삦臾댄븯 (?썹럦?←몧):</strong> ???녿뒗 ?섏쓽 留묒? 留덉쓬</td>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: bold;">?뺤꽌 ?곹깭</td>
      <td>寃고샎 ?꾩쓽 湲곕?媛? ?딆쓬怨??꾨쫫?ㅼ???????먮???/td>
      <td>?몄썡??臾댁긽?? ?⑦렪??????먮쭩, 泥섏???????먯“</td>
    </tr>
  </table>

  <div class="page-break"></div>

  <h3>???듭떖 臾명븰 媛쒕뀗 ?ㅼ?湲? 媛먯젙?댁엯 vs 媛앷????곴?臾?/h3>
  <div class="box">
    <p style="font-weight: bold; color: #e74c3c;">[媛쒕뀗 ?명듃]</p>
    <p>??<strong>媛먯젙?댁엯(Empathy):</strong> ?붿옄??媛먯젙??????먯뿰臾??????댁엯?섏뿬, 洹???곷룄 ?붿옄? 媛숈씠 湲곕퍙?섍굅???ы띁?섎뒗 寃껋쿂???쒗쁽?섎뒗 湲곕쾿?낅땲?? (???= ?붿옄)</p>
    <p>??<strong>媛앷????곴?臾?Objective Correlative):</strong> ?붿옄??媛먯젙??媛꾩젒?곸쑝濡??쒗쁽?섍굅???섍린?쒗궎湲??꾪빐 ?숈썝???щЪ?대굹 諛곌꼍?낅땲?? 媛먯젙???묎컳吏 ?딆븘?? ?붿옄???몃줈????뗫낫?닿쾶 ?섎뒗 ?꾧뎄媛 ?????덉뒿?덈떎.</p>
  </div>
  
  <p>洹쒖썝媛?먯꽌 ?붿옄???몃줈?怨??쒖쓣 洹밸??뷀븯湲??꾪빐 ?곗씤 ?뚯옱?ㅼ쓽 湲곕뒫??援щ퀎??遊낆떆??</p>
  <ul>
    <li><strong>?ㅼ넄 (洹?쒕씪誘? - <span style="color: #c0392b; font-weight:bold;">媛먯젙?댁엯</span>:</strong> "踰쎌삤??利??쒕━???섎━ ?꾩쫱 ?곕뒗 ?덉빞" (?ㅼ넄???ы뵾 ?곕뒗 寃껋쑝濡?臾섏궗??. ???ы뵒???ъ쁺?섏뿬 洹?쒕씪誘몃룄 '?대떎'怨??쒗쁽?덉쑝誘濡?媛먯젙?댁엯?낅땲??</li>
    <li><strong>?밴린湲?(嫄곕Ц怨? - <span style="color: #c0392b; font-weight:bold;">媛앷????곴?臾?/span>:</strong> ?몃텇怨??쒕쫫???щ옒湲??꾪빐 ?곗＜?섎뒗 留ㅺ컻泥댁씠???꾧뎄?대?濡?媛앷????곴?臾쇱엯?덈떎.</li>
  </ul>

  <div class="space-large"></div>

  <h2>[2] ?ㅼ쟾 ?곸슜 臾몄젣 (洹쒖썝媛 ??</h2>
  
  <p class="question">1. '洹쒖썝媛'???붿옄??怨쇨굅 ( A )(15??16???쒖젅)???꾨쫫?ㅼ썱???쇨뎬??吏?붿뿀?쇰굹, ?몄썡???섎윭 ( B )?섍쾶 蹂?대쾭由??먯떊??紐⑥뒿???쒗깂?섍퀬 ?덉뒿?덈떎. 鍮덉뭏??梨꾩슦?쒖삤.</p>
  <p class="answer">( A ): ___________________, ( B ): ___________________</p>

  <p class="question">2. ?섏떎??洹?쒕씪誘??숆낵 ?섎끃湲곌툑(嫄곕Ц怨???以?'媛먯젙?댁엯'???대떦?섎뒗 ?쒖뼱??臾댁뾿?몄? ?곸뼱 蹂댁떆??</p>
  <p class="answer">______________________________________</p>


  <div class="page-break"></div>

  <h2>[3] ?묓뭹 ?꾨꼍 ?대?: ?묒옄 誘몄긽, &lt;?명쁽?뺥썑??餓곲’?뗥릮??&gt;</h2>
  <div class="img-container">
    <img src="data:image/png;base64,{img2_b64}" alt="?명쁽?뺥썑???쇰윭?ㅽ듃">
    <p style="font-size: 9pt; color: #7f8c8d; margin-top: 10px;">(紐⑥쭊 ?쒕젴 ?띿뿉?쒕룄 ?좉탳???뺤꽦???껋? ?딆? ?뺥썑??湲고뭹)</p>
  </div>
  
  <div class="box">
    <p>?숈쥌 ???쇱뼱???명쁽 ?뺥썑???먯쐞? 蹂듭쐞, ?ν씗鍮덉쓽 紐곕씫 ?ш굔????궗???ъ떎??諛뷀깢???먭퀬 李쎌옉??<strong>沅곸쨷 ?ㅺ린(野?쮼) ?뚯꽕</strong>?낅땲??</p>
    <ul>
      <li><strong>媛덈옒:</strong> 援?Ц ?뚯꽕, ??궗 ?뚯꽕, ?ㅺ린 ?뚯꽕</li>
      <li><strong>二쇱젣:</strong> ?명쁽 ?뺥썑??怨좉껐???뺤꽦怨??쒕젴, ?ы븘洹???좎븙???由쎄낵 ?좎쓽 ?밸━)</li>
      <li><strong>?섏쓽:</strong> 議곗꽑 ?쒕? 3? 沅곸쨷 臾명븰 以??섎굹濡? ?밸? ?ъ꽦?ㅼ쓽 ?좉탳???ㅻ━愿(?ш린 湲덉?, ?쒖쥌, ?몃궡)??怨좎뒪???諛섏쁺?⑸땲??</li>
    </ul>
  </div>

  <h3>???몃Ъ 媛꾩쓽 ?由?援ъ“ (??vs ??</h3>
  <table>
    <tr>
      <th>?몃Ъ</th>
      <th>?깃꺽 諛??뱀쭠 (?좉탳???ㅻ━愿 諛섏쁺)</th>
    </tr>
    <tr>
      <td style="font-weight: bold;">?명쁽?뺥썑</td>
      <td>?숈쥌??怨꾨퉬. 吏덊닾?섏? ?딄퀬 ?몃궡?ъ씠 媛뺥븿. ?⑦렪(?????띾컯?먮룄 ?먮쭩?섏? ?딄퀬 ?좉탳??遺??惹?쓿)??吏?? (?좎쓽 ?곸쭠)</td>
    </tr>
    <tr>
      <td style="font-weight: bold;">?ν씗鍮?/td>
      <td>援먮쭔?섍퀬 ?먯슃?ㅻ윭?곕ŉ ?쒕룆?? 紐⑦븿???쇱궪?? (?낆쓽 ?곸쭠)</td>
    </tr>
    <tr>
      <td style="font-weight: bold;">?숈쥌</td>
      <td>?ν씗鍮덉쓽 紐⑦븿???섏뼱媛???몃Ъ濡?媛遺?μ젣 ?ы쉶???덈? 沅뚮젰??</td>
    </tr>
  </table>

  <div class="page-break"></div>

  <h3>???쒖닠?먯쓽 媛쒖엯 (?몄쭛?먯쟻 ?쇳룊)</h3>
  <div class="box" style="background-color: #e8f6f3; border-color: #1abc9c;">
    <p style="font-style: italic;">"媛?⑦븯怨?留앷레?섎떎. ?뺥썑 紐⑥떊 ?쒕??ㅼ씠???ㅼ＝ 留덉쓬??李?뼱吏由ъ슂."</p>
  </div>
  <p>?꾩????묎? ?쒖젏?쇰줈 移섎??섍쾶 ?ш굔???쒖닠?섎떎媛, ?꾩? 媛숈씠 ?쒖닠?먭? <strong>媛묒옄湲??먯떊??媛먯젙???잛븘?닿굅???곹솴??吏곸젒 ?됯?(?쇳룊)</strong>?섎뒗 ?紐⑹씠 ?먯＜ ?깆옣?⑸땲?? ?대뒗 怨좎쟾 ?뚯꽕???꾪삎?곸씤 ?뱀쭠?쇰줈, ?낆옄媛 ?쒖닠?먯쓽 ?쒖꽑???숉솕?섏뼱 二쇱씤怨듭뿉 怨듦컧?섎룄濡?留뚮벊?덈떎.</p>

  <div class="space-large"></div>

  <h2>[4] ?ㅼ쟾 ?곸슜 臾몄젣 (?명쁽?뺥썑????</h2>
  
  <p class="question">3. '?명쁽?뺥썑???먯꽌 ?뺥썑??寃곕갚?④낵 ?믪? ?뺤꽦???곸쭠?섎뒗 ?쒖옄?깆뼱???? A )?숇씪??留먯?, ?섍퇋?먭??숈쓽 ?붿옄媛 蹂몄씤??源⑤걮??留덉쓬?⑤? 鍮꾩쑀???뚮룄 ?깆옣?⑸땲?? 鍮덉뭏??梨꾩슦?쒖삤.</p>
  <p class="answer">( A ): ___________________</p>

  <p class="question">4. 怨좎쟾 ?뚯꽕?먯꽌 ?몃Ъ???됰룞?대굹 ?ш굔??????쒖닠?먭? 吏곸젒 ?깆옣?섏뿬 ?먯떊??媛먯젙?대굹 二쇨????됯?瑜??대━??湲곕쾿??臾댁뾿?대씪怨??⑸땲源?</p>
  <p class="answer">______________________________________</p>


</body>
</html>
"""

def main():
    try:
        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)
        
        print("Uploading V4 Beautiful Worksheets...")
        student_doc = create_doc(service, "[?숈뒿吏] 2027 ?섎뒫?밴컯 臾명븰 : 媛덈옒蹂듯빀 05", FOLDER_ID, STUDENT_HTML)
        print("V4 Documents created successfully!")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == '__main__':
    main()
