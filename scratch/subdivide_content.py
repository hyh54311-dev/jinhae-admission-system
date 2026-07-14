# Code.gs, Index.html, 그리고 update_gdoc_template.py에 [2-1] 및 [2-2] 분할 로직을 통합 주입하는 스크립트

import os

# 1. Code.gs 백엔드 수정
code_path = "문학_탐구보고서_웹앱_Code.gs"
with open(code_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1-1. headers 컬럼 정의 수정
target_headers = '"구글 문서 링크", "세특 초안 (AI)", "바이트 수", "처리 상태"'
replacement_headers = '"구글 문서 링크", "세특 초안 (AI)", "바이트 수", "처리 상태"' # 안전성 검증 후 컬럼 삽입

# 컬럼 정의 라인 교체
code = code.replace(
    '      "제출일시", "학년", "반", "번호", "이름", "희망 진로", "대상 작품", \n      "탐구 주제", "탐구 동기", "탐구 내용", "탐구 과정", "결론 및 성장", \n      "구글 문서 링크", "세특 초안 (AI)", "바이트 수", "처리 상태"',
    '      "제출일시", "학년", "반", "번호", "이름", "희망 진로", "대상 작품", \n      "탐구 주제", "탐구 동기", "2-1. 작품 분석", "2-2. 진로/사회 연계", "탐구 과정", "결론 및 성장", \n      "구글 문서 링크", "세특 초안 (AI)", "바이트 수", "처리 상태"'
)

# 1-2. submitReport 내부 변수 추출 교체 (content -> content_literary, content_fusion)
target_extract = """    var motivation = formData.motivation.trim();
    var content = formData.content.trim();
    var process = formData.process.trim();
    var conclusion = formData.conclusion.trim();

    // 빈 입력값 유효성 검사
    if (!ban || !num || !name || !career || !work || !title || !motivation || !content || !process || !conclusion) {
      return { success: false, error: "모든 항목을 입력해 주세요." };
    }"""

replacement_extract = """    var motivation = formData.motivation.trim();
    var content_literary = formData.content_literary.trim();
    var content_fusion = formData.content_fusion.trim();
    var process = formData.process.trim();
    var conclusion = formData.conclusion.trim();

    // 빈 입력값 유효성 검사
    if (!ban || !num || !name || !career || !work || !title || !motivation || !content_literary || !content_fusion || !process || !conclusion) {
      return { success: false, error: "모든 항목을 입력해 주세요." };
    }"""

code = code.replace(target_extract, replacement_extract)

# 1-3. submitReport 오버라이트 기록 로직 수정
target_overwrite = """    if (existingRowIdx > -1) {
      // 기존 제출 내역이 있으면 '최종 제출본'으로 덮어씁니다.
      // 1열: 제출일시(갱신), 6열~13열: 본문 내용 및 문서 링크 갱신
      sheet.getRange(existingRowIdx, 1).setValue(timestamp);
      sheet.getRange(existingRowIdx, 6, 1, 8).setValues([[
        career, work, title, motivation, content, process, conclusion, docUrl
      ]]);
      // 14열~16열: 기존에 자동 생성되었던 세특 초안, 최종 세특, 처리 상태 초기화("대기"로 환원)
      sheet.getRange(existingRowIdx, 14, 1, 3).setValues([["", "", "대기"]]);
    } else {
      // 신규 제출일 경우 신규 행 추가
      sheet.appendRow([
        timestamp, grade, ban, num, name, career, work, 
        title, motivation, content, process, conclusion, 
        docUrl, "", "", "대기"
      ]);
    }

    // 3. 정렬 처리 (학년, 반, 번호 순)
    var updatedLastRow = sheet.getLastRow();
    if (updatedLastRow > 1) {
      var dataRange = sheet.getRange(2, 1, updatedLastRow - 1, 16);
      dataRange.sort([{column: 2, ascending: true}, {column: 3, ascending: true}, {column: 4, ascending: true}]);
    }"""

replacement_overwrite = """    if (existingRowIdx > -1) {
      // 기존 제출 내역이 있으면 '최종 제출본'으로 덮어씁니다.
      // 1열: 제출일시(갱신), 6열~14열(9개 열): 본문 내용 및 문서 링크 갱신
      sheet.getRange(existingRowIdx, 1).setValue(timestamp);
      sheet.getRange(existingRowIdx, 6, 1, 9).setValues([[
        career, work, title, motivation, content_literary, content_fusion, process, conclusion, docUrl
      ]]);
      // 15열~17열: 기존에 자동 생성되었던 세특 초안, 최종 세특, 처리 상태 초기화("대기"로 환원)
      sheet.getRange(existingRowIdx, 15, 1, 3).setValues([["", "", "대기"]]);
    } else {
      // 신규 제출일 경우 신규 행 추가 (총 17개 열)
      sheet.appendRow([
        timestamp, grade, ban, num, name, career, work, 
        title, motivation, content_literary, content_fusion, process, conclusion, 
        docUrl, "", "", "대기"
      ]);
    }

    // 3. 정렬 처리 (학년, 반, 번호 순)
    var updatedLastRow = sheet.getLastRow();
    if (updatedLastRow > 1) {
      var dataRange = sheet.getRange(2, 1, updatedLastRow - 1, 17);
      dataRange.sort([{column: 2, ascending: true}, {column: 3, ascending: true}, {column: 4, ascending: true}]);
    }"""

code = code.replace(target_overwrite, replacement_overwrite)

# 1-4. createProgrammaticReportDoc 함수 내 문서 구조 변경
target_doc_generation = """  appendSection(body, "1. 탐구 동기 (수업 연계성)", data.motivation, false);
  appendSection(body, "2. 탐구 내용 및 결과", data.content, false);
  appendSection(body, "3. 탐구 과정 및 심화 노력 (도서/논문 등 독서 성과)", data.process, false);"""

replacement_doc_generation = """  appendSection(body, "1. 탐구 동기 (수업 연계성)", data.motivation, false);
  appendSection(body, "2-1. 작품 속 탐구 장면/시어의 문학적 분석", data.content_literary, false);
  appendSection(body, "2-2. 희망 진로 학문 및 현대 사회 사례 연계 분석", data.content_fusion, false);
  appendSection(body, "3. 탐구 과정 및 심화 노력 (도서/논문 등 독서 성과)", data.process, false);"""

code = code.replace(target_doc_generation, replacement_doc_generation)

# 1-5. AI 피드백 템플릿 내 2-1 및 2-2 적용
target_feedback_prompt = """- 1. 탐구 동기: ${formData.motivation}
- 2. 탐구 내용 및 결과: ${formData.content}
- 3. 탐구 과정 및 심화 노력: ${formData.process}"""

replacement_feedback_prompt = """- 1. 탐구 동기: ${formData.motivation}
- 2-1. 작품 속 탐구 장면/시어 분석: ${formData.content_literary}
- 2-2. 진로 학문 및 사회 연계 분석: ${formData.content_fusion}
- 3. 탐구 과정 및 심화 노력: ${formData.process}"""

code = code.replace(target_feedback_prompt, replacement_feedback_prompt)

with open(code_path, "w", encoding="utf-8") as f:
    f.write(code)
print("Successfully modified 백엔드 Code.gs!")


# 2. Index.html 프론트엔드 수정
html_path = "문학_탐구보고서_웹앱_Index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 2-1. textarea 교체 (content -> content_literary, content_fusion)
target_textareas = """      <div class="form-group">
        <label for="content">2. 탐구 내용 및 결과</label>
        <textarea id="content" name="content" placeholder="주제에 대해 스스로 탐구하고 도출해 낸 사실, 핵심 주장, 혹은 현대 사회 사례의 비교 분석 내용을 작성해 주세요." required></textarea>
        <button type="button" class="tip-toggle-btn" onclick="toggleTip(this)">💡 작성 팁 및 예시 보기</button>
        <div class="tip-content-panel">
          <h5>탐구 내용 작성 팁:</h5>
          <p>본인의 분석 결과와 핵심 논증입니다. 작품 분석에 그치지 않고 현대 정부의 복지 통계나 공학 이론, 윤리 기준 등 전문성 있는 배경 지식을 연계하여 서술합니다.</p>
          <div class="example-title">🩺 의학/보건 계열 예시:</div>
          <div class="example-text">1950년대의 민간 편향적 보건 인프라의 한계를 도출함. 나아가 현대 한국 보건의료실태조사 데이터를 활용해 여전히 도서·산간 필수 진료(치과, 소아과 등) 접근성이 결여되는 '의료 사막화' 문제를 공공보건 사각지대 관점에서 실증 비교함.</div>
          <div class="example-title">💻 공학/IT/AI 계열 예시:</div>
          <div class="example-text">시 속 폭설의 소통 단절 속성을 현대 빅데이터 환경의 '필터 버블(Filter Bubble)' 및 안면인식 기술의 남용에 대입함. 정보 독점 및 알고리즘적 감시가 작동하여 개인이 의식하지 못한 채 생각을 제한받는 '디지털 백색 계엄령'의 작동 구조를 규명함.</div>
        </div>
      </div>"""

replacement_textareas = """      <div class="form-group">
        <label for="content_literary">2-1. 작품 속 탐구 장면/시어의 문학적 분석</label>
        <textarea id="content_literary" name="content_literary" placeholder="작품 속에서 본인의 진로 및 사회 문제와 연결하고 싶은 구체적인 장면, 갈등 상황, 은유 또는 시어의 의미를 분석하여 서술해 주세요." required></textarea>
        <button type="button" class="tip-toggle-btn" onclick="toggleTip(this)">💡 작성 팁 및 예시 보기</button>
        <div class="tip-content-panel">
          <h5>작품 문학 분석 작성 팁:</h5>
          <p>작품 자체의 갈등 구조나 핵심 소재의 은유를 문학적인 관점에서 충실하게 먼저 분석해야 세특의 문학 교과 신뢰성이 보장됩니다.</p>
          <div class="example-title">🩺 의학/보건 계열 예시:</div>
          <div class="example-text">『오발탄』 속 주인공 철호가 극심한 치통을 앓으면서도 치료비가 없어 뽑지 못하고 참는 모습은, 단순 개인 질환이 아니라 한국전쟁 전후 한국 사회 서민들의 극심한 경제적 빈곤과 생존 위기를 육체적 고통을 통해 시각적으로 형상화한 것임을 분석함.</div>
          <div class="example-title">💻 공학/IT/AI 계열 예시:</div>
          <div class="example-text">「대설주의보」에서 소통을 단절시키고 세상을 통제하는 '폭설'의 속성을 분석함. 폭설이 단순 자연 현상을 넘어 군사 독재 시절의 감시와 억압을 상징하는 '백색 계엄령'의 은유적 매개체로 기능하여 정보와 생각을 통제하고 있음을 도출함.</div>
        </div>
      </div>

      <div class="form-group">
        <label for="content_fusion">2-2. 희망 진로 학문 및 현대 사회 사례 연계 분석</label>
        <textarea id="content_fusion" name="content_fusion" placeholder="위에서 분석한 문학적 상황을 본인의 희망 진로(전공 개념/이론) 또는 현대 사회의 제도, 법률, 과학 기술, 통계 수치 등과 융합하여 서술해 주세요." required></textarea>
        <button type="button" class="tip-toggle-btn" onclick="toggleTip(this)">💡 작성 팁 및 예시 보기</button>
        <div class="tip-content-panel">
          <h5>진로/사회 융합 작성 팁:</h5>
          <p>2-1의 장면 분석을 나의 전공 학술 이론이나 현대 사회 실제 데이터, 정책 제도와 연계하여 분석함으로써 주도성과 비판적 사고력을 보여줍니다.</p>
          <div class="example-title">🩺 의학/보건 계열 예시:</div>
          <div class="example-text">소설 속 치통을 현대 사회복지학 및 예방의학의 '사회적 질병 모델'에 대입함. 나아가 현대 한국 보건의료실태조사 통계 자료를 연계하여 산간·도서 등 의료 취약 지역의 필수 진료 접근성 상실 현상을 분석하고 공공보건의료망 강화 제도의 당위성을 역설함.</div>
          <div class="example-title">💻 공학/IT/AI 계열 예시:</div>
          <div class="example-text">시 속 폭설의 정보 통제 양상을 현대 IT 환경의 '디지털 판옵티콘' 및 빅데이터 감시 기술에 대입함. 사용자 행동을 무의식중에 제한하는 알고리즘적 통제(필터 버블) 현상과 대조 분석하여, 개발 과정의 인공지능 윤리 가이드라인 설계 의무를 공학적으로 성찰함.</div>
        </div>
      </div>"""

html = html.replace(target_textareas, replacement_textareas)

# 2-2. JS getFormData() 획득 부분 수정
target_js_formdata = """    var content = document.getElementById("content").value;
    var process = document.getElementById("process").value;
    var conclusion = document.getElementById("conclusion").value;

    var workSelect = document.getElementById("workSelect").value;
    var work = workSelect;
    if (workSelect === "custom") {
      work = document.getElementById("customWork").value;
    }

    var method = document.getElementById("submitMethod").value;
    
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
      conclusion: conclusion,"""

replacement_js_formdata = """    var content_literary = document.getElementById("content_literary").value;
    var content_fusion = document.getElementById("content_fusion").value;
    var process = document.getElementById("process").value;
    var conclusion = document.getElementById("conclusion").value;

    var workSelect = document.getElementById("workSelect").value;
    var work = workSelect;
    if (workSelect === "custom") {
      work = document.getElementById("customWork").value;
    }

    var method = document.getElementById("submitMethod").value;
    
    // 파일 업로드 방식일 경우 서술 텍스트 빈 공간으로 설정
    if (method === "file") {
      motivation = "(파일 제출 완료)";
      content_literary = "(파일 제출 완료)";
      content_fusion = "(파일 제출 완료)";
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
      content_literary: content_literary,
      content_fusion: content_fusion,
      process: process,
      conclusion: conclusion,"""

html = html.replace(target_js_formdata, replacement_js_formdata)

# 2-3. JS submitReportForm 유효성 검사부분 수정
target_js_validation = """    // 전체 항목 유효성 체크
    if (!data.ban || !data.num || !data.name || !data.career || !data.work || !data.title || !data.motivation || !data.content || !data.process || !data.conclusion) {
      alert("모든 입력란을 작성해 주세요. (누락된 부분이 있습니다.)");
      return;
    }"""

replacement_js_validation = """    // 전체 항목 유효성 체크
    if (!data.ban || !data.num || !data.name || !data.career || !data.work || !data.title || !data.motivation || !data.content_literary || !data.content_fusion || !data.process || !data.conclusion) {
      alert("모든 입력란을 작성해 주세요. (누락된 부분이 있습니다.)");
      return;
    }"""

html = html.replace(target_js_validation, replacement_js_validation)

# 2-4. JS requestFeedback() 유효성 검사부분 수정
target_feedback_validation = """    // 최소 입력 확인
    if (!data.career || !data.work || !data.title || !data.motivation) {
      alert("진로, 작품, 주제, 탐구 동기 항목을 먼저 작성해 주셔야 AI가 구체적인 피드백을 드릴 수 있습니다.");
      return;
    }"""

replacement_feedback_validation = """    // 최소 입력 확인
    if (!data.career || !data.work || !data.title || !data.motivation || !data.content_literary) {
      alert("진로, 작품, 주제, 탐구 동기와 [2-1. 작품 분석] 항목을 먼저 적어주셔야 AI 피드백이 작동합니다.");
      return;
    }"""

html = html.replace(target_feedback_validation, replacement_feedback_validation)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Successfully modified 프론트엔드 Index.html!")


# 3. update_gdoc_template.py 스크립트 수정
# 구글 문서 양식 자체도 2-1 및 2-2 분할하여 생성하도록 갱신
gdoc_script_path = "scratch/update_gdoc_template.py"
with open(gdoc_script_path, "r", encoding="utf-8") as f:
    gdoc_script = f.read()

target_gdoc_text = """            "2. 탐구 내용 및 결과\\n"
            "----------------------------------------------------------------------------------------\\n"
            "💡 [안내문] 주제에 대해 스스로 탐구하고 도출해 낸 결과나 현대 사회적 비평 사례를 서술하세요. (관련 보건 통계나 공학 이론 등을 연계하면 신뢰도가 높아집니다.)\\n"
            "----------------------------------------------------------------------------------------\\n"
            "\\n"
            " 여기에 탐구 내용 및 결과를 작성해 주세요.\\n"
            "\\n\\n"
            "3. 탐구 과정 및 심화 노력 (도서/논문 등 독서)\\n" """

replacement_gdoc_text = """            "2-1. 작품 속 탐구 장면/시어의 문학적 분석\\n"
            "----------------------------------------------------------------------------------------\\n"
            "💡 [안내문] 작품 속에서 본인의 진로 및 사회 문제와 연결하고 싶은 구체적인 장면, 갈등 상황, 은유 또는 시어의 의미를 분석하여 서술해 주세요.\\n"
            "----------------------------------------------------------------------------------------\\n"
            "\\n"
            " 여기에 작품 분석 내용을 작성해 주세요.\\n"
            "\\n\\n"
            "2-2. 희망 진로 학문 및 현대 사회 사례 연계 분석\\n"
            "----------------------------------------------------------------------------------------\\n"
            "💡 [안내문] 위에서 분석한 문학적 상황을 본인의 희망 진로(전공 개념/이론) 또는 현대 사회의 실제 제도, 법률, 과학 기술, 통계 수치 등과 비교·융합하여 비판적으로 서술해 주세요.\\n"
            "----------------------------------------------------------------------------------------\\n"
            "\\n"
            " 여기에 진로/사회 융합 분석 내용을 작성해 주세요.\\n"
            "\\n\\n"
            "3. 탐구 과정 및 심화 노력 (도서/논문 등 독서)\\n" """

gdoc_script = gdoc_script.replace(target_gdoc_text, replacement_gdoc_text)

with open(gdoc_script_path, "w", encoding="utf-8") as f:
    f.write(gdoc_script)
print("Successfully modified update_gdoc_template.py!")
