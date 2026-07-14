# Index.html의 테마 8종 확장 + 직접입력 추가 및 대표 교과 작품 10종 리스트 확장을 처리하는 스크립트

import os

html_path = "문학_탐구보고서_웹앱_Index.html"

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. 테마 선택 및 작품 선택 폼 부분 교체
target_form_section = """      <!-- 섹션 2: 탐구 대상 설정 -->
      <div class="section-title">탐구 대상 문학 및 테마</div>
      <div class="form-row">
        <div class="form-group">
          <label for="theme">탐구 테마 분류</label>
          <select id="theme" name="theme" required>
            <option value="1">① 문학 작품의 현대적 재해석 및 진로 융합 탐구</option>
            <option value="2">② 사회학적 문학 비평 (문학과 사회의 연결)</option>
            <option value="3">③ 원작 소설과 미디어 믹스 비교 분석</option>
            <option value="4">④ 작가 중심의 상호텍스트성 탐구</option>
          </select>
        </div>
        <div class="form-group">
          <label for="workSelect">탐구 대상 문학 작품</label>
          <select id="workSelect" onchange="handleWorkSelection(this)" required>
            <option value="">작품 선택</option>
            <option value="오발탄 (이범선)">오발탄 (이범선)</option>
            <option value="대설주의보 (최승호)">대설주의보 (최승호)</option>
            <option value="새들도 세상을 뜨는구나 (황지우)">새들도 세상을 뜨는구나 (황지우)</option>
            <option value="원미동 사람들 (양귀자)">원미동 사람들 (양귀자)</option>
            <option value="광장 (최인훈)">광장 (최인훈)</option>
            <option value="아홉 켤레의 구두로 남은 사내 (윤흥길)">아홉 켤레의 구두로 남은 사내 (윤흥길)</option>
            <option value="custom">직접 입력</option>
          </select>
        </div>
      </div>

      <div class="form-group custom-work-container" id="customWorkContainer">
        <label for="customWork">작품 정보 직접 입력</label>
        <input type="text" id="customWork" placeholder="예: 소설명 (작가명)">
      </div>"""

replacement_form_section = """      <!-- 섹션 2: 탐구 대상 설정 -->
      <div class="section-title">탐구 대상 문학 및 테마</div>
      <div class="form-row">
        <div class="form-group">
          <label for="theme">탐구 테마 분류</label>
          <select id="theme" name="theme" onchange="handleThemeSelection(this)" required>
            <option value="" disabled selected>테마 분류 선택</option>
            <option value="문학 작품과 진로·전공 학문 융합 탐구">① 문학 작품과 진로·전공 학문 융합 탐구</option>
            <option value="사회학적 문학 비평 및 시대상 비교 분석">② 사회학적 문학 비평 및 시대상 비교 분석</option>
            <option value="심리학적 비평 (인물 심리 및 내면 분석)">③ 심리학적 비평 (인물 심리 및 내면 분석)</option>
            <option value="비교문학 및 미디어 믹스 (원작과 매체 변화 분석)">④ 비교문학 및 미디어 믹스 (원작과 매체 변화 분석)</option>
            <option value="생태학적·환경학적 문학 비평">⑤ 생태학적·환경학적 문학 비평</option>
            <option value="윤리학적·인권적 가치 중심 비평">⑥ 윤리학적·인권적 가치 중심 비평</option>
            <option value="상호텍스트성 및 작가 중심 탐구">⑦ 상호텍스트성 및 작가 중심 탐구</option>
            <option value="문학적 표현 기법 및 구조주의적 비평">⑧ 문학적 표현 기법 및 구조주의적 비평</option>
            <option value="custom">직접 입력</option>
          </select>
        </div>
        <div class="form-group">
          <label for="workSelect">탐구 대상 문학 작품</label>
          <select id="workSelect" onchange="handleWorkSelection(this)" required>
            <option value="" disabled selected>작품 선택</option>
            <option value="오발탄 (이범선)">오발탄 (이범선) - 소설</option>
            <option value="대설주의보 (최승호)">대설주의보 (최승호) - 시</option>
            <option value="새들도 세상을 뜨는구나 (황지우)">새들도 세상을 뜨는구나 (황지우) - 시</option>
            <option value="원미동 사람들 (양귀자)">원미동 사람들 (양귀자) - 소설</option>
            <option value="광장 (최인훈)">광장 (최인훈) - 소설</option>
            <option value="아홉 켤레의 구두로 남은 사내 (윤흥길)">아홉 켤레의 구두로 남은 사내 (윤흥길) - 소설</option>
            <option value="태평천하 (채만식)">태평천하 (채만식) - 소설</option>
            <option value="동백꽃 (김유정)">동백꽃 (김유정) - 소설</option>
            <option value="춘향전 (작자 미상)">춘향전 (작자 미상) - 고전 소설</option>
            <option value="진달래꽃 (김소월)">진달래꽃 (김소월) - 시</option>
            <option value="custom">직접 입력</option>
          </select>
        </div>
      </div>

      <!-- 테마 직접 입력창 -->
      <div class="form-group" id="customThemeContainer" style="display: none; animation: fadeIn 0.3s ease; margin-top: 8px;">
        <label for="customTheme">테마 분류 직접 입력</label>
        <input type="text" id="customTheme" placeholder="예: 문학 속 생태주의 비평과 현대 탄소 중립 해결 과제">
      </div>

      <!-- 작품 직접 입력창 -->
      <div class="form-group custom-work-container" id="customWorkContainer" style="display: none; animation: fadeIn 0.3s ease; margin-top: 8px;">
        <label for="customWork">작품 정보 직접 입력</label>
        <input type="text" id="customWork" placeholder="예: 소설명 (작가명) 또는 시제목 (시인명)">
      </div>"""

if "customThemeContainer" not in html:
    html = html.replace(target_form_section, replacement_form_section)

# 2. JavaScript 직접 입력 토글 함수 추가 (handleThemeSelection)
js_toggle_target = """  // 직접 입력 처리 함수
  function handleWorkSelection(selectElement) {
    var container = document.getElementById("customWorkContainer");
    var input = document.getElementById("customWork");
    if (selectElement.value === "custom") {
      container.style.display = "block";
      input.required = true;
      input.focus();
    } else {
      container.style.display = "none";
      input.required = false;
      input.value = "";
    }
  }"""

js_toggle_replacement = """  // 테마 직접 입력 토글 처리 함수
  function handleThemeSelection(selectElement) {
    var container = document.getElementById("customThemeContainer");
    var input = document.getElementById("customTheme");
    if (selectElement.value === "custom") {
      container.style.display = "block";
      input.required = true;
      input.focus();
    } else {
      container.style.display = "none";
      input.required = false;
      input.value = "";
    }
  }

  // 작품 직접 입력 토글 처리 함수
  function handleWorkSelection(selectElement) {
    var container = document.getElementById("customWorkContainer");
    var input = document.getElementById("customWork");
    if (selectElement.value === "custom") {
      container.style.display = "block";
      input.required = true;
      input.focus();
    } else {
      container.style.display = "none";
      input.required = false;
      input.value = "";
    }
  }"""

if "handleThemeSelection" not in html:
    html = html.replace(js_toggle_target, js_toggle_replacement)

# 3. getFormData() 내부에서 theme 직접 입력 값 수집 처리
target_getformdata = """    var career = document.getElementById("career").value;
    var theme = document.getElementById("theme").value;
    var title = document.getElementById("title").value;"""

replacement_getformdata = """    var career = document.getElementById("career").value;
    var themeSelect = document.getElementById("theme").value;
    var theme = themeSelect;
    if (themeSelect === "custom") {
      theme = document.getElementById("customTheme").value;
    }
    var title = document.getElementById("title").value;"""

if "themeSelect" not in html:
    html = html.replace(target_getformdata, replacement_getformdata)

# 4. closeModal() 내부 리셋 로직 보완 (customThemeContainer 숨기기 및 값 초기화)
target_closemodal = """    document.getElementById("customWorkContainer").style.display = "none";
    document.getElementById("feedbackBox").style.display = "none";"""

replacement_closemodal = """    document.getElementById("customThemeContainer").style.display = "none";
    document.getElementById("customWorkContainer").style.display = "none";
    document.getElementById("feedbackBox").style.display = "none";"""

if "customThemeContainer" in html:
    html = html.replace(target_closemodal, replacement_closemodal)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully expanded selections in 문학_탐구보고서_웹앱_Index.html!")
