# Code.gs와 Index.html에 파일 업로드 및 워드 파일 다운로드 기능을 주입하는 스크립트

import os

# 1. 백엔드 Code.gs 파일 업데이트
code_path = "문학_탐구보고서_웹앱_Code.gs"

with open(code_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1-1. submitReport 함수 업데이트
# submitReport 함수 안에서 파일 데이터를 처리할 수 있도록 분기 추가
target_submit_func = """    // 1. 제출함 구글 드라이브 폴더 생성/조회 및 구글 문서 생성
    var folderId = prepareSubmissionFolder();
    var docUrl = createProgrammaticReportDoc(folderId, formData);

    // 2. 스프레드시트 기록
    var lastRow = sheet.getLastRow();
    sheet.appendRow([
      timestamp, grade, ban, num, name, career, work, 
      title, motivation, content, process, conclusion, 
      docUrl, "", "", "대기"
    ]);"""

replacement_submit_func = """    var folderId = prepareSubmissionFolder();
    var docUrl = "";
    var downloadUrl = "";

    if (formData.fileData && formData.fileName) {
      // 파일 업로드 방식 처리
      var decodedFile = Utilities.base64Decode(formData.fileData);
      var blob = Utilities.newBlob(decodedFile, getMimeType(formData.fileName), formData.fileName);
      
      var folder = DriveApp.getFolderById(folderId);
      
      // 파일명 형식 지정: [문학 보고서제출] 반_번호_이름_주제.확장자
      var ext = formData.fileName.split('.').pop();
      var newFileName = "[문학 보고서제출] " + formData.ban + "반_" + formData.num + "번_" + formData.name + "_" + formData.title + "." + ext;
      blob.setName(newFileName);
      
      var uploadedFile = folder.createFile(blob);
      uploadedFile.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      docUrl = uploadedFile.getUrl();
      downloadUrl = docUrl; // 파일 업로드는 동일 URL로 노출
    } else {
      // 직접 입력 방식 처리 (기존 구글 문서 자동 빌드)
      var docResult = createProgrammaticReportDoc(folderId, formData);
      docUrl = docResult.url;
      downloadUrl = docResult.downloadUrl;
    }

    // 2. 스프레드시트 기록
    var lastRow = sheet.getLastRow();
    sheet.appendRow([
      timestamp, grade, ban, num, name, career, work, 
      title, motivation, content, process, conclusion, 
      docUrl, "", "", "대기"
    ]);"""

code = code.replace(target_submit_func, replacement_submit_func)

# 1-2. submitReport 반환값에 downloadUrl 추가
target_return = """    return { success: true, docUrl: docUrl, name: name };"""
replacement_return = """    return { success: true, docUrl: docUrl, downloadUrl: downloadUrl, name: name, isFile: !!(formData.fileData) };"""

code = code.replace(target_return, replacement_return)

# 1-3. createProgrammaticReportDoc 함수 반환값 객체화 (url, downloadUrl 반환)
target_doc_create = """  // 공유 권한 설정 (링크가 있는 모든 사용자가 읽을 수 있도록 허용)
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);

  return file.getUrl();
}"""

replacement_doc_create = """  // 공유 권한 설정 (링크가 있는 모든 사용자가 읽을 수 있도록 허용)
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);

  var viewUrl = file.getUrl();
  var dlUrl = viewUrl.replace("/edit", "/export?format=docx"); // 구글 문서 다운로드 링크 트릭

  return { url: viewUrl, downloadUrl: dlUrl };
}"""

code = code.replace(target_doc_create, replacement_doc_create)

# 1-4. 파일 마임타입 헬퍼 함수 추가
mime_helper = """
/**
 * 파일 확장자명에 맞는 MIME-Type을 추출합니다.
 */
function getMimeType(fileName) {
  var ext = fileName.split('.').pop().toLowerCase();
  switch (ext) {
    case 'pdf': return 'application/pdf';
    case 'hwp': return 'application/x-hwp';
    case 'hwpx': return 'application/haansofthwpx';
    case 'docx': return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
    case 'doc': return 'application/msword';
    default: return 'application/octet-stream';
  }
}
"""

if "getMimeType" not in code:
    code += mime_helper

with open(code_path, "w", encoding="utf-8") as f:
    f.write(code)
print("Successfully updated 백엔드 Code.gs 파일!")


# 2. 프론트엔드 Index.html 파일 업데이트
html_path = "문학_탐구보고서_웹앱_Index.html"

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 2-1. 인적 사항 하단에 제출 방식 선택 탭 및 파일 선택창 주입
target_html_career = """      <div class="form-group">
        <label for="career">희망 진로 및 관심 분야</label>
        <input type="text" id="career" name="career" placeholder="예: 의예과, 컴퓨터공학과, 생명과학연구원 등" required>
        <span class="help-text">구체적인 학과명이나 진로 키워드를 적어주면 세특 작성 시 보다 상세하게 연결됩니다.</span>
      </div>"""

replacement_html_career = """      <div class="form-group">
        <label for="career">희망 진로 및 관심 분야</label>
        <input type="text" id="career" name="career" placeholder="예: 의예과, 컴퓨터공학과, 생명과학연구원 등" required>
        <span class="help-text">구체적인 학과명이나 진로 키워드를 적어주면 세특 작성 시 보다 상세하게 연결됩니다.</span>
      </div>

      <!-- 제출 방식 선택 및 파일 입력창 -->
      <div class="section-title">제출 방식 설정</div>
      <div class="form-group">
        <div style="display: flex; background: #e2e8f0; padding: 4px; border-radius: 10px; margin-bottom: 12px;">
          <button type="button" id="methodTextBtn" class="btn" style="flex: 1; border-radius: 8px; font-size: 13.5px; padding: 8px 12px; background: white; color: var(--primary); box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height: 36px;" onclick="switchMethod('text')">
            ✍️ 웹 폼 직접 기입
          </button>
          <button type="button" id="methodFileBtn" class="btn" style="flex: 1; border-radius: 8px; font-size: 13.5px; padding: 8px 12px; background: none; color: var(--text-muted); box-shadow: none; min-height: 36px;" onclick="switchMethod('file')">
            📁 PDF/한글 파일 업로드
          </button>
        </div>
        <input type="hidden" id="submitMethod" name="submitMethod" value="text">
      </div>

      <div class="form-group" id="fileUploadContainer" style="display: none; background: #f8fafc; border: 2px dashed #cbd5e1; padding: 18px; border-radius: 10px; text-align: center; animation: fadeIn 0.3s ease;">
        <label for="reportFile" style="cursor: pointer; display: block; margin-bottom: 8px; color: var(--primary-light);">
          📂 보고서 파일 선택 (PDF, HWP, HWPX, DOCX)
        </label>
        <input type="file" id="reportFile" accept=".pdf,.hwp,.hwpx,.docx,.doc" onchange="handleFileSelected(this)" style="border: none; padding: 4px; font-size: 14px; background: none;">
        <span class="help-text" style="margin-top: 6px;">용량 제한: 최대 15MB 이하의 완성된 문서 파일</span>
      </div>"""

if "submitMethod" not in html:
    html = html.replace(target_html_career, replacement_html_career)

# 2-2. 텍스트 입력창 영역 전체를 wrap하여 숨길 수 있도록 수정
target_html_textareas = """      <!-- 섹션 3: 보고서 본문 작성 -->
      <div class="section-title">보고서 본문 서술</div>"""

replacement_html_textareas = """      <!-- 섹션 3: 보고서 본문 작성 -->
      <div id="textAreaSection" style="animation: fadeIn 0.3s ease;">
      <div class="section-title">보고서 본문 서술</div>"""

if "textAreaSection" not in html:
    html = html.replace(target_html_textareas, replacement_html_textareas)

# 2-3. 서술부 마감 태그 수정 (Form-group 마감 다음 div 닫기)
target_html_end_textarea = """      <!-- 실시간 AI 피드백 영역 -->
      <div class="feedback-box" id="feedbackBox">
        <h4>💡 국어 선생님의 실시간 AI 조언</h4>
        <div class="feedback-content" id="feedbackContent"></div>
      </div>"""

replacement_html_end_textarea = """      <!-- 실시간 AI 피드백 영역 -->
      <div class="feedback-box" id="feedbackBox">
        <h4>💡 국어 선생님의 실시간 AI 조언</h4>
        <div class="feedback-content" id="feedbackContent"></div>
      </div>
      </div> <!-- textAreaSection 마감 -->"""

if "textAreaSection" not in html:
    html = html.replace(target_html_end_textarea, replacement_html_end_textarea)

# 2-4. 모달 안내 창에 워드 다운로드 단추 추가
target_html_modal = """    <div class="link-box">
      <a id="docLink" href="#" target="_blank" style="color: var(--primary-light); font-weight: 700; text-decoration: underline;">
        생성된 보고서 구글 문서 보기 ↗
      </a>
    </div>"""

replacement_html_modal = """    <div class="link-box">
      <a id="docLink" href="#" target="_blank" style="color: var(--primary-light); font-weight: 700; text-decoration: underline;">
        생성된 보고서 구글 문서 보기 ↗
      </a>
    </div>
    <div id="downloadLinkContainer" style="margin-bottom: 20px; display: none;">
      <a id="downloadDocLink" href="#" target="_blank" class="btn btn-secondary" style="width: 100%; display: flex; justify-content: center; align-items: center; gap: 6px; font-weight: 700;">
        💾 워드(.docx) 파일로 다운로드
      </a>
    </div>"""

if "downloadDocLink" not in html:
    html = html.replace(target_html_modal, replacement_html_modal)

# 2-5. JavaScript 비즈니스 로직 추가 (제출 전환, 파일 로드 및 다운로드 연동)
js_vars = """  // Roster 데이터 캐시
  var globalRoster = {};
  var fileData = null;
  var fileName = "";

  // 제출 방식 토글 기능
  function switchMethod(method) {
    document.getElementById("submitMethod").value = method;
    var textBtn = document.getElementById("methodTextBtn");
    var fileBtn = document.getElementById("methodFileBtn");
    var textSection = document.getElementById("textAreaSection");
    var fileContainer = document.getElementById("fileUploadContainer");
    var feedbackBtn = document.getElementById("feedbackBtn");

    if (method === "text") {
      textBtn.style.background = "white";
      textBtn.style.color = "var(--primary)";
      textBtn.style.boxShadow = "0 2px 4px rgba(0,0,0,0.05)";
      
      fileBtn.style.background = "none";
      fileBtn.style.color = "var(--text-muted)";
      fileBtn.style.boxShadow = "none";

      textSection.style.display = "block";
      fileContainer.style.display = "none";
      feedbackBtn.style.display = "inline-flex";
    } else {
      fileBtn.style.background = "white";
      fileBtn.style.color = "var(--primary)";
      fileBtn.style.boxShadow = "0 2px 4px rgba(0,0,0,0.05)";
      
      textBtn.style.background = "none";
      textBtn.style.color = "var(--text-muted)";
      textBtn.style.boxShadow = "none";

      textSection.style.display = "none";
      fileContainer.style.display = "block";
      feedbackBtn.style.display = "none";
    }
  }

  // 모바일 파일 업로드 FileReader 리더
  function handleFileSelected(input) {
    var file = input.files[0];
    if (!file) {
      fileData = null;
      fileName = "";
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      alert("업로드 용량 한도(15MB)를 초과했습니다. 다시 확인해 주세요.");
      input.value = "";
      fileData = null;
      fileName = "";
      return;
    }

    showLoading("파일을 업로드 대기열에 변환하여 등록하는 중입니다...");
    var reader = new FileReader();
    reader.onload = function(e) {
      hideLoading();
      fileData = e.target.result.split(',')[1];
      fileName = file.name;
    };
    reader.onerror = function() {
      hideLoading();
      alert("파일 읽기 도중 오류가 발생했습니다.");
    };
    reader.readAsDataURL(file);
  }"""

if "fileData" not in html:
    html = html.replace("  // Roster 데이터 캐시\n  var globalRoster = {};", js_vars)

# 2-6. getFormData 및 submitReportForm 수정 (파일 데이터 포함)
target_form_collect = """    return {
      grade: grade,
      ban: ban,
      num: num,
      name: name,
      career: career,
      theme: theme,
      work: work,
      title: title,
      motivation: motivation,
      content: content,
      process: process,
      conclusion: conclusion
    };"""

replacement_form_collect = """    var method = document.getElementById("submitMethod").value;
    
    // 파일 업로드 방식일 경우 서술 텍스트 빈 공간으로 설정
    if (method === "file") {
      motivation = "(파일 제출 완료)";
      content = "(파일 제출 완료)";
      process = "(파일 제출 완료)";
      conclusion = "(파일 제출 완료)";
    }

    return {
      grade: grade,
      ban: ban,
      num: num,
      name: name,
      career: career,
      theme: theme,
      work: work,
      title: title,
      motivation: motivation,
      content: content,
      process: process,
      conclusion: conclusion,
      fileData: method === "file" ? fileData : null,
      fileName: method === "file" ? fileName : null
    };"""

html = html.replace(target_form_collect, replacement_form_collect)

# 2-7. submitReportForm 유효성 체크 및 성공 모달 핸들러 수정
target_validate_submit = """    // 전체 항목 유효성 체크
    if (!data.ban || !data.num || !data.name || !data.career || !data.work || !data.title || !data.motivation || !data.content || !data.process || !data.conclusion) {
      alert("모든 입력란을 작성해 주세요. (누락된 부분이 있습니다.)");
      return;
    }"""

replacement_validate_submit = """    var method = document.getElementById("submitMethod").value;
    
    // 인적 사항 필수값 유효성 체크
    if (!data.ban || !data.num || !data.name || !data.career || !data.work || !data.title) {
      alert("기본 인적 사항과 작품, 주제는 반드시 입력해야 합니다.");
      return;
    }
    
    // 방식에 따른 개별 데이터 유효성 체크
    if (method === "file") {
      if (!fileData) {
        alert("업로드할 한글 또는 PDF 파일을 선택해 주세요.");
        return;
      }
    } else {
      if (!data.motivation || !data.content || !data.process || !data.conclusion) {
        alert("보고서 서술형 문항들을 성실히 기입해 주세요.");
        return;
      }
    }"""

html = html.replace(target_validate_submit, replacement_validate_submit)

# 2-8. 제출 성공 핸들러의 모달 처리 업데이트 (다운로드 버튼 보이기 및 제목 변경)
target_success_modal_handling = """        if (response.success) {
            document.getElementById("successStudentName").innerText = response.name;
            document.getElementById("docLink").href = response.docUrl;
            
            // 모달 오픈
            document.getElementById("successModal").classList.add("active");"""

replacement_success_modal_handling = """        if (response.success) {
            document.getElementById("successStudentName").innerText = response.name;
            
            var docLink = document.getElementById("docLink");
            var dlContainer = document.getElementById("downloadLinkContainer");
            var dlDocLink = document.getElementById("downloadDocLink");
            
            docLink.href = response.docUrl;
            
            if (response.isFile) {
              // 파일 업로드일 경우 구글 드라이브 문서 뷰 링크만 표시
              docLink.innerText = "업로드된 보고서 원본 보기 ↗";
              dlContainer.style.display = "none";
            } else {
              // 웹 폼 기입일 경우 문서 뷰와 워드(.docx) 다운로드 모두 노출
              docLink.innerText = "생성된 보고서 구글 문서 보기 ↗";
              dlDocLink.href = response.downloadUrl;
              dlContainer.style.display = "block";
            }
            
            // 모달 오픈
            document.getElementById("successModal").classList.add("active");"""

html = html.replace(target_success_modal_handling, replacement_success_modal_handling)

# 2-9. 모달 닫기 시 리셋 핸들러 수정
target_close_modal_reset = """  // 모달 닫기 및 폼 리셋
  function closeModal() {
    document.getElementById("successModal").classList.remove("active");
    // 리셋 처리
    document.getElementById("reportForm").reset();
    document.getElementById("customWorkContainer").style.display = "none";
    document.getElementById("feedbackBox").style.display = "none";
    document.getElementById("name").disabled = true;
    document.getElementById("name").innerHTML = '<option value="" disabled selected>반을 먼저 선택하세요</option>';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }"""

replacement_close_modal_reset = """  // 모달 닫기 및 폼 리셋
  function closeModal() {
    document.getElementById("successModal").classList.remove("active");
    // 리셋 처리
    document.getElementById("reportForm").reset();
    document.getElementById("customWorkContainer").style.display = "none";
    document.getElementById("feedbackBox").style.display = "none";
    document.getElementById("name").disabled = true;
    document.getElementById("name").innerHTML = '<option value="" disabled selected>반을 먼저 선택하세요</option>';
    
    // 파일 업로드 상태 초기화
    fileData = null;
    fileName = "";
    switchMethod("text"); // 텍스트 기입식 기본값으로 리셋
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }"""

html = html.replace(target_close_modal_reset, replacement_close_modal_reset)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Successfully updated 프론트엔드 Index.html 파일!")
