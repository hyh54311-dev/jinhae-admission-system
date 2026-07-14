# Index.html의 파일 업로드 컨테이너에 양식 다운로드 링크 카드 및 CONFIG 변수를 추가하는 스크립트

import os

html_path = "문학_탐구보고서_웹앱_Index.html"

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. 파일 업로드 컨테이너 내용물 교체 (양식 파일 다운로드 버튼 카드 주입)
target_upload_container = """      <div class="form-group" id="fileUploadContainer" style="display: none; background: #f8fafc; border: 2px dashed #cbd5e1; padding: 18px; border-radius: 10px; text-align: center; animation: fadeIn 0.3s ease;">
        <label for="reportFile" style="cursor: pointer; display: block; margin-bottom: 8px; color: var(--primary-light);">
          📂 보고서 파일 선택 (PDF, HWP, HWPX, DOCX)
        </label>
        <input type="file" id="reportFile" accept=".pdf,.hwp,.hwpx,.docx,.doc" onchange="handleFileSelected(this)" style="border: none; padding: 4px; font-size: 14px; background: none;">
        <span class="help-text" style="margin-top: 6px;">용량 제한: 최대 15MB 이하의 완성된 문서 파일</span>
      </div>"""

replacement_upload_container = """      <div class="form-group" id="fileUploadContainer" style="display: none; background: #f8fafc; border: 2px dashed #cbd5e1; padding: 18px; border-radius: 10px; text-align: center; animation: fadeIn 0.3s ease;">
        
        <!-- 양식 다운로드 카드 배치 -->
        <div style="background: #f1f5f9; padding: 14px; border-radius: 8px; margin-bottom: 18px; border: 1px solid var(--border); text-align: left;">
          <span style="font-size: 13.5px; font-weight: 700; color: var(--primary); display: block; margin-bottom: 8px; text-align: center;">📋 보고서 작성 표준 양식 내려받기</span>
          <div style="display: flex; gap: 8px; justify-content: center;">
            <a id="hwpTemplateLink" href="#" target="_blank" class="btn" style="flex: 1; min-height: 38px; padding: 6px 10px; font-size: 12.5px; background: #fef2f2; color: #b91c1c; border: 1px solid #fca5a5; font-weight: 700; text-decoration: none; border-radius: 6px; display: inline-flex; justify-content: center; align-items: center; gap: 4px;">
              📥 한글(.hwp) 양식 받기
            </a>
            <a id="docsTemplateLink" href="#" target="_blank" class="btn" style="flex: 1; min-height: 38px; padding: 6px 10px; font-size: 12.5px; background: #f0f9ff; color: #0369a1; border: 1px solid #7dd3fc; font-weight: 700; text-decoration: none; border-radius: 6px; display: inline-flex; justify-content: center; align-items: center; gap: 4px;">
              📥 구글 문서 복사본 만들기
            </a>
          </div>
          <span class="help-text" style="margin-top: 8px; font-size: 11.5px; text-align: center; display: block; color: var(--text-muted);">
            ※ 양식을 다운로드하여 내용을 작성한 뒤, PDF 또는 한글 파일로 컴퓨터/태블릿에 저장해 업로드하세요.
          </span>
        </div>

        <label for="reportFile" style="cursor: pointer; display: block; margin-bottom: 8px; color: var(--primary-light); font-weight: 700;">
          📂 내 컴퓨터에서 보고서 파일 선택
        </label>
        <input type="file" id="reportFile" accept=".pdf,.hwp,.hwpx,.docx,.doc" onchange="handleFileSelected(this)" style="border: none; padding: 4px; font-size: 14px; background: none; margin: 0 auto; display: block;">
        <span class="help-text" style="margin-top: 6px; text-align: center; display: block;">용량 제한: 최대 15MB 이하의 완성된 문서 파일</span>
      </div>"""

if "hwpTemplateLink" not in html:
    html = html.replace(target_upload_container, replacement_upload_container)

# 2. CONFIG 설정 변수 및 링크 설정 스크립트 추가
# 스크립트 시작 부분에 CONFIG 변수 선언 및 DOMContentLoaded에 리스너 바인딩
js_vars_target = """  // 제출 방식 토글 기능"""

js_vars_replacement = """  // [선생님 설정용] 구글 드라이브에 올리신 보고서 한글(HWP) 파일 다운로드 링크와 구글 문서(Docs) 사본 만들기 공유 링크를 지정하세요.
  var CONFIG_TEMPLATE_HWP = "https://docs.google.com/document/d/1KgpBoxrQUwiqA86qJr9eB6KAckSNfuC7QJea-m7qiSg/export?format=docx"; // 예시용
  var CONFIG_TEMPLATE_DOCS = "https://docs.google.com/document/d/1KgpBoxrQUwiqA86qJr9eB6KAckSNfuC7QJea-m7qiSg/copy"; // 예시용 (/copy를 뒤에 붙이면 자동 복사 팝업이 뜹니다)

  // 제출 방식 토글 기능"""

if "CONFIG_TEMPLATE_HWP" not in html:
    html = html.replace(js_vars_target, js_vars_replacement)

# 3. DOMContentLoaded 내부 명렬 로드 시점에 양식 링크 바인딩 추가
dom_loaded_target = """  // 페이지 로드 시 구글 앱스 스크립트에서 명렬표 자동 수신
  window.addEventListener('DOMContentLoaded', function() {
    showLoading("학급 명렬표를 스프레드시트에서 로드하고 있습니다...");"""

dom_loaded_replacement = """  // 페이지 로드 시 구글 앱스 스크립트에서 명렬표 자동 수신
  window.addEventListener('DOMContentLoaded', function() {
    // 양식 파일 다운로드 링크 연동
    document.getElementById("hwpTemplateLink").href = CONFIG_TEMPLATE_HWP;
    document.getElementById("docsTemplateLink").href = CONFIG_TEMPLATE_DOCS;

    showLoading("학급 명렬표를 스프레드시트에서 로드하고 있습니다...");"""

if "hwpTemplateLink" not in html or "docsTemplateLink" not in html:
    # double replacement safety
    if "document.getElementById(\"hwpTemplateLink\").href" not in html:
        html = html.replace(dom_loaded_target, dom_loaded_replacement)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully updated 문학_탐구보고서_웹앱_Index.html with template download links!")
