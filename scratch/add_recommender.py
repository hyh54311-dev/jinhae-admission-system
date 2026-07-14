# 문학_탐구보고서_웹앱_Code.gs 및 Index.html에 도서/검색어 추천 기능 및 백엔드 함수를 추가하는 스크립트

import os

# 1. 백엔드 Code.gs 파일 업데이트
code_path = "문학_탐구보고서_웹앱_Code.gs"

with open(code_path, "r", encoding="utf-8") as f:
    code = f.read()

recommend_js_func = """
/**
 * 학생이 입력한 진로와 문학 작품 정보를 바탕으로 관련 도서와 실재하는 RISS 논문 검색 키워드를 추천합니다. (할루시네이션 방지)
 */
function getLiteratureRecommendations(formData) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000);
  } catch (e) {
    return { success: false, error: "서버 접속이 지연되고 있습니다. 잠시 후 다시 시도해 주세요." };
  }
  
  try {
    var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
    if (!apiKey) {
      return { success: false, error: "교사용 스프레드시트 메뉴에서 Gemini API 키를 먼저 설정해야 추천 기능을 이용할 수 있습니다." };
    }

    var prompt = `
당신은 고등학교 국어 교사이자 학생들의 주도적 문학 탐구 설계를 돕는 독서 가이드 전문가입니다.
학생이 입력한 진로와 선택 문학 작품을 유기적으로 연결할 수 있도록, RISS나 도서관에서 참고하기 좋은 학술자료 정보를 추천해 주십시오.

[학생 입력 정보]
- 희망 진로: ${formData.career}
- 대상 작품: ${formData.work}
- 탐구 주제: ${formData.title}

[추천 규칙 - 할루시네이션(가짜 정보) 방지]
1. 절대로 존재하지 않는 가짜 논문 제목이나 가짜 저술을 지어내지 마십시오.
2. 도서 추천: 뇌과학, 경제학, 사회학, 법학 등에서 널리 검증되어 출판된 실재하는 교양 대중 도서(명저) 2권을 추천하고, 책 소개와 융합 포인트를 2줄 이내로 간략히 설명해 주십시오.
3. 논문 검색어 추천: 학생들이 RISS(학술연구정보서비스)나 DBpia 등의 학술 논문 검색 사이트에서 실제로 유용한 논문을 찾을 수 있도록 돕는 실제 작동하는 검색 키워드 조합(검색 쿼리) 3개를 제안해 주십시오. (예: "작품명 + 진로 분야 키워드")
4. 가급적 번호와 불릿 기호로 정리하여 학생이 모바일 화면에서 한눈에 보기 편하도록 350자 이내로 콤팩트하게 출력해 주십시오.

출력 예시 형식:
[추천 도서]
1. 『도서명』 (저자명) : 융합 포인트 설명
2. 『도서명』 (저자명) : 융합 포인트 설명

[RISS 논문 추천 검색어]
- '검색어 1' (예: 이범선 오발탄 공공의료)
- '검색어 2'
- '검색어 3'
`;

    var url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.MODEL_NAME}:generateContent?key=${apiKey}`;
    var payload = {
      "contents": [{ "parts": [{ "text": prompt }] }],
      "generationConfig": { "temperature": 0.4 }
    };
    var options = {
      "method": "post",
      "contentType": "application/json",
      "payload": JSON.stringify(payload),
      "muteHttpExceptions": true
    };

    var response = UrlFetchApp.fetch(url, options);
    var json = JSON.parse(response.getContentText());
    if (json.candidates && json.candidates[0].content && json.candidates[0].content.parts[0].text) {
      return { success: true, recommendations: json.candidates[0].content.parts[0].text.trim() };
    }
    return { success: false, error: "추천 결과를 생성하지 못했습니다." };
  } catch (e) {
    return { success: false, error: e.toString() };
  } finally {
    lock.releaseLock();
  }
}
"""

if "getLiteratureRecommendations" not in code:
    with open(code_path, "a", encoding="utf-8") as f:
        f.write(recommend_js_func)
    print("Successfully added getLiteratureRecommendations function to 문학_탐구보고서_웹앱_Code.gs!")
else:
    print("getLiteratureRecommendations function already exists in Code.gs.")

# 2. 프론트엔드 Index.html 파일 업데이트
html_path = "문학_탐구보고서_웹앱_Index.html"

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 2-1. Section 3 (탐구 과정)의 텍스트에어리어 하단에 '추천 받기' 버튼 및 결과 패널 주입
process_target = """      <div class="form-group">
        <label for="process">3. 탐구 과정 및 심화 노력 (도서/논문 등 독서)</label>
        <textarea id="process" name="process" placeholder="의문을 해결하기 위해 스스로 추가로 읽은 논문 제목, 도서 제목과, 어려운 개념을 극복하기 위해 기울인 노력을 서술해 주세요." required></textarea>
        <button type="button" class="tip-toggle-btn" onclick="toggleTip(this)">💡 작성 팁 및 예시 보기</button>
        <div class="tip-content-panel">"""

process_replacement = """      <div class="form-group">
        <label for="process">3. 탐구 과정 및 심화 노력 (도서/논문 등 독서)</label>
        <textarea id="process" name="process" placeholder="의문을 해결하기 위해 스스로 추가로 읽은 논문 제목, 도서 제목과, 어려운 개념을 극복하기 위해 기울인 노력을 서술해 주세요." required></textarea>
        <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
          <button type="button" class="tip-toggle-btn" onclick="toggleTip(this)">💡 작성 팁 및 예시 보기</button>
          <button type="button" class="tip-toggle-btn" style="color: #6366f1; background: #e0e7ff; padding: 4px 10px;" onclick="requestRecommendations()">📚 추천 도서/검색어 제안받기</button>
        </div>
        
        <!-- 추천 도서/검색어 결과 패널 -->
        <div class="tip-content-panel" id="recommendPanel" style="background: #f5f3ff; border: 1px solid #c7d2fe; padding: 14px; margin-top: 8px; font-size: 13.5px; line-height: 1.5; color: #1e1b4b; animation: fadeIn 0.3s ease;">
          <h5 style="color: #4f46e5; font-weight: 700; margin-bottom: 6px; display: flex; align-items: center; gap: 4px;">📚 AI 추천 도서 및 RISS 검색어</h5>
          <div id="recommendContent" style="white-space: pre-wrap; margin-top: 4px;"></div>
        </div>

        <div class="tip-content-panel">"""

if "requestRecommendations()" not in html:
    html = html.replace(process_target, process_replacement)

# 2-2. JavaScript requestRecommendations 및 로컬 데보 모드 핸들러 주입
js_functions = """  // 아코디언 가이드 토글 함수
  function toggleTip(button) {
    var panel = button.nextElementSibling;
    // 만약 다음 요소가 추천 패널이면 그 다음 요소를 타겟팅하도록 보완
    if (panel.id === "recommendPanel") {
      panel = panel.nextElementSibling;
    }
    if (panel.style.display === "block") {
      panel.style.display = "none";
      button.innerHTML = "💡 작성 팁 및 예시 보기";
    } else {
      panel.style.display = "block";
      button.innerHTML = "🔒 가이드 접기";
    }
  }

  // 실시간 추천 도서 및 RISS 검색어 수집 함수 (할루시네이션 방지)
  function requestRecommendations() {
    var data = getFormData();
    
    if (!data.career || !data.work || !data.title) {
      alert("진로, 작품, 주제 항목을 먼저 작성해 주셔야 AI가 맞춤 자료를 추천할 수 있습니다.");
      return;
    }
    
    showLoading("AI가 진로와 작품에 최적화된 추천 도서 및 RISS 검색어 조합을 선별하는 중입니다...");
    
    if (typeof google !== 'undefined' && google.script && google.script.run) {
      google.script.run
        .withSuccessHandler(function(response) {
          hideLoading();
          var panel = document.getElementById("recommendPanel");
          var content = document.getElementById("recommendContent");
          
          if (response.success) {
            content.innerHTML = response.recommendations;
            panel.style.display = "block";
            panel.scrollIntoView({ behavior: 'smooth' });
          } else {
            alert("추천 로드 실패: " + response.error);
          }
        })
        .withFailureHandler(function(err) {
          hideLoading();
          alert("서버 연결 실패: " + err.toString());
        })
        .getLiteratureRecommendations(data);
    } else {
      // 로컬 프리뷰 데모 모드 대응 (할루시네이션 없는 가상 DB 출력)
      setTimeout(function() {
        hideLoading();
        var panel = document.getElementById("recommendPanel");
        var content = document.getElementById("recommendContent");
        
        var careerLower = data.career.toLowerCase();
        var demoRec = "";
        
        if (careerLower.includes("의") || careerLower.includes("보건") || careerLower.includes("생명")) {
          demoRec = "[추천 도서]\\n1. 『아픔이 길이 되려면』 (김승섭 저) : 사회적 고통과 경제적 빈곤이 질병이라는 신체적 고통으로 구현되는 메커니즘을 밝혀 소설 속 치통의 구조적 성격 분석에 유용함.\\n2. 『전쟁과 의학』 (황상익 저) : 한국전쟁 전후 한국 사회의 붕괴된 공공보건 상태와 철호 일가가 처한 의료 무방비 상태를 역사적으로 해독하는 데 유용함.\\n\\n[RISS 논문 추천 검색어]\\n- '이범선 오발탄 의료 소외'\\n- '한국전쟁 전후 소설 보건 의료 실태'\\n- '빈곤 질병 보건사회학적 악순환'";
        } else if (careerLower.includes("컴") || careerLower.includes("공") || careerLower.includes("ai") || careerLower.includes("정")) {
          demoRec = "[추천 도서]\\n1. 『감시와 처벌』 (미셸 푸코 저) : 보이지 않는 권력이 사회를 규제하고 통제하는 판옵티콘 구조를 해설하여 시 속 대설의 '백색 계엄령'의 메커니즘을 빅데이터와 연계 분석하는 데 필수적임.\\n2. 『감시 사회의 유혹』 (지그문트 바우만 저) : 세련된 디지털 기술이 사용자의 자발적 노출을 어떻게 감시와 통제로 활용하는지 정보 사회 윤리를 성찰하는 데 유용함.\\n\\n[RISS 논문 추천 검색어]\\n- '최승호 대설주의보 정보 통제'\\n- '디지털 판옵티콘 빅데이터 감시 사회'\\n- '인공지능 기술 윤리와 개인 사생활 침해'";
        } else {
          demoRec = "[추천 도서]\\n1. 『위험사회』 (울리히 벡 저) : 현대 과학 기술 문명이 가져온 불확실성과 재난 하에서의 국가의 통제 권력을 문학의 비극과 연계 감상하기에 적합함.\\n2. 『소유냐 삶이냐』 (에리히 프롬 저) : 물질적 집착으로 소외를 겪는 현대 소설 속 인물들의 정서를 생태주의적으로 성찰하는 데 유용함.\\n\\n[RISS 논문 추천 검색어]\\n- '소설명 + 시대 상황 주거 격차'\\n- '문학적 은유와 현대 위험 사회 비교'\\n- 'RISS 검색창에서 [작품명 + 자신의 진로 키워드] 조합'";
        }
        
        content.innerText = demoRec.replace(/\\n/g, "\\n");
        panel.style.display = "block";
        panel.scrollIntoView({ behavior: 'smooth' });
      }, 1000);
    }
  }"""

# 기존 toggleTip 함수 정의를 새 js_functions의 toggleTip 및 requestRecommendations로 교체
if "requestRecommendations()" not in html:
    html = html.replace("""  // 아코디언 가이드 토글 함수
  function toggleTip(button) {
    var panel = button.nextElementSibling;
    if (panel.style.display === "block") {
      panel.style.display = "none";
      button.innerHTML = "💡 작성 팁 및 예시 보기";
    } else {
      panel.style.display = "block";
      button.innerHTML = "🔒 가이드 접기";
    }
  }""", js_functions)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully updated 문학_탐구보고서_웹앱_Index.html with recommendations button and handlers!")
