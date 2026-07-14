# 문학_탐구보고서_웹앱_Index.html에 아코디언 가이드 및 작성 팁 예시를 추가하는 스크립트

import os

html_path = "문학_탐구보고서_웹앱_Index.html"

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. CSS 스타일 정의 및 주입
css_styles = """
    /* 작성 팁 및 예시 아코디언 스타일 */
    .tip-toggle-btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: none;
      border: none;
      color: var(--primary-light);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      margin-top: 6px;
      padding: 4px 8px;
      border-radius: 6px;
      transition: background 0.2s ease;
    }

    .tip-toggle-btn:hover {
      background: #eff6ff;
      color: var(--primary);
    }

    .tip-content-panel {
      display: none;
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px;
      margin-top: 8px;
      font-size: 13px;
      line-height: 1.5;
      color: var(--text-muted);
      animation: fadeIn 0.3s ease;
    }

    .tip-content-panel h5 {
      font-size: 13px;
      font-weight: 700;
      color: var(--primary);
      margin-bottom: 6px;
    }

    .tip-content-panel .example-title {
      font-weight: 700;
      color: #334155;
      margin-top: 10px;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .tip-content-panel .example-text {
      background: white;
      border-left: 3px solid #cbd5e1;
      padding: 8px 12px;
      margin-top: 4px;
      border-radius: 4px;
      font-family: inherit;
      color: #0f172a;
      white-space: pre-wrap;
    }
  </style>"""

html = html.replace("  </style>", css_styles)

# 2. JavaScript 토글 함수 주입
js_function = """<script>
  // 아코디언 가이드 토글 함수
  function toggleTip(button) {
    var panel = button.nextElementSibling;
    if (panel.style.display === "block") {
      panel.style.display = "none";
      button.innerHTML = "💡 작성 팁 및 예시 보기";
    } else {
      panel.style.display = "block";
      button.innerHTML = "🔒 가이드 접기";
    }
  }

  // Roster 데이터 캐시"""

html = html.replace("<script>\n  // Roster 데이터 캐시", js_function)

# 3. 각 입력 문항에 토글 가이드 추가

# 3-1. 탐구 주제
title_target = """      <div class="form-group">
        <label for="title">탐구 주제 (제목)</label>
        <input type="text" id="title" name="title" placeholder="의미 있는 연구 주제 제목을 매력적으로 지어주세요." required>
        <span class="help-text">예: 『오발탄』 속 주인공 철호의 치통 분석을 통한 전후 한국의 의료 소외 실태와 현대 공공의료 보완 대안 탐구</span>
      </div>"""

title_replacement = """      <div class="form-group">
        <label for="title">탐구 주제 (제목)</label>
        <input type="text" id="title" name="title" placeholder="의미 있는 연구 주제 제목을 매력적으로 지어주세요." required>
        <button type="button" class="tip-toggle-btn" onclick="toggleTip(this)">💡 작성 팁 및 예시 보기</button>
        <div class="tip-content-panel">
          <h5>제목 작명 팁:</h5>
          <p>선택한 문학 작품의 갈등 요소나 시어와 본인의 희망 진로(의학/공학 등) 또는 현대 사회적 키워드를 명확하게 드러내어 구체적으로 작성합니다.</p>
          <div class="example-title">🩺 의학/보건 계열 예시:</div>
          <div class="example-text">『오발탄』 속 주인공 철호의 치통 분석을 통한 전후 한국의 의료 소외 실태와 현대 공공의료/지역간 의료 격차 개선 방안 탐구</div>
          <div class="example-title">💻 공학/IT/AI 계열 예시:</div>
          <div class="example-text">「대설주의보」의 '백색 계엄령' 은유를 바탕으로 본 현대 빅데이터/AI 감시 사회의 통제 메커니즘과 윤리적 기술 제어 방안 분석</div>
        </div>
      </div>"""

html = html.replace(title_target, title_replacement)

# 3-2. 1. 탐구 동기
motivation_target = """      <div class="form-group">
        <label for="motivation">1. 탐구 동기 (수업 시간 배운 내용과의 연계)</label>
        <textarea id="motivation" name="motivation" placeholder="수업 시간 중 어떤 대목, 개념, 시어 등에서 질문이 시작되었는지 동기를 논리적으로 적어주세요." required></textarea>
      </div>"""

motivation_replacement = """      <div class="form-group">
        <label for="motivation">1. 탐구 동기 (수업 시간 배운 내용과의 연계)</label>
        <textarea id="motivation" name="motivation" placeholder="수업 시간 중 어떤 대목, 개념, 시어 등에서 질문이 시작되었는지 동기를 논리적으로 적어주세요." required></textarea>
        <button type="button" class="tip-toggle-btn" onclick="toggleTip(this)">💡 작성 팁 및 예시 보기</button>
        <div class="tip-content-panel">
          <h5>탐구 동기 작성 팁:</h5>
          <p>교과서 지문 설명이나 교사의 판서 중 의문이 들었거나 호기심이 생긴 지점을 본인의 진로 고민과 연결하여 유기적인 논리로 서술합니다.</p>
          <div class="example-title">🩺 의학/보건 계열 예시:</div>
          <div class="example-text">『오발탄』 철호가 극심한 치통에도 치료비가 없어 방치하는 장면에서, 사회 안전망의 부재가 개인의 신체적·정신적 붕괴를 유발함을 목격하고 현대 국가 의료 보장 제도의 실제 역할에 대해 깊이 있는 의문을 품게 되어 탐구를 설계함.</div>
          <div class="example-title">💻 공학/IT/AI 계열 예시:</div>
          <div class="example-text">「대설주의보」 수업 중 폭설이 도로를 막고 사람들을 통제·고립시키는 '백색 계엄령' 은유를 배우며, 현대 정보통신 사회에서 알고리즘과 빅데이터 수집 권력이 개인의 정보와 생각을 통제하는 구조와 유사함을 포착하고 그 기술적 인과관계를 밝히고자 탐구함.</div>
        </div>
      </div>"""

html = html.replace(motivation_target, motivation_replacement)

# 3-3. 2. 탐구 내용 및 결과
content_target = """      <div class="form-group">
        <label for="content">2. 탐구 내용 및 결과</label>
        <textarea id="content" name="content" placeholder="주제에 대해 스스로 탐구하고 도출해 낸 사실, 핵심 주장, 혹은 현대 사회 사례의 비교 분석 내용을 작성해 주세요." required></textarea>
      </div>"""

content_replacement = """      <div class="form-group">
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

html = html.replace(content_target, content_replacement)

# 3-4. 3. 탐구 과정 및 심화 노력
process_target = """      <div class="form-group">
        <label for="process">3. 탐구 과정 및 심화 노력 (도서/논문 등 독서)</label>
        <textarea id="process" name="process" placeholder="의문을 해결하기 위해 스스로 추가로 읽은 논문 제목, 도서 제목과, 어려운 개념을 극복하기 위해 기울인 노력을 서술해 주세요." required></textarea>
        <span class="help-text">예: RISS에서 '~' 논문을 검색해 발췌독함, 도서관에서 '~' 책을 대출해 정독하고 개념을 분석함 등</span>
      </div>"""

process_replacement = """      <div class="form-group">
        <label for="process">3. 탐구 과정 및 심화 노력 (도서/논문 등 독서)</label>
        <textarea id="process" name="process" placeholder="의문을 해결하기 위해 스스로 추가로 읽은 논문 제목, 도서 제목과, 어려운 개념을 극복하기 위해 기울인 노력을 서술해 주세요." required></textarea>
        <button type="button" class="tip-toggle-btn" onclick="toggleTip(this)">💡 작성 팁 및 예시 보기</button>
        <div class="tip-content-panel">
          <h5>심화 노력 작성 팁:</h5>
          <p>지적 호기심을 해소하기 위한 자발적 독서(도서명) 및 논문 분석(논문명) 이력과, 탐구 중 마주한 수준 높은 학술적 장벽을 학교 교사 피드백이나 토론으로 극복해 나간 과정이 생생히 기술되어야 세특의 신뢰도가 수직 상승합니다.</p>
          <div class="example-title">🩺 의학/보건 계열 예시:</div>
          <div class="example-text">학술 논문 「한국전쟁기 보건의료체계의 한계」를 찾아 분석하고, 도서 『아픔이 길이 되려면』(김승섭 저)을 완독하여 빈곤이 만성 신체 질환으로 이어지는 생리학적 메커니즘을 밝힘. 어려운 공공보건 법안 조항은 담당 선생님께 면담을 요청해 조언을 받음.</div>
          <div class="example-title">💻 공학/IT/AI 계열 예시:</div>
          <div class="example-text">미셸 푸코의 『감시와 처벌』 및 IEEE의 '인공지능 윤리적 설계 국제표준' 문헌을 분석해 참고함. 복잡한 알고리즘과 빅데이터 흐름 모델을 보고서 내에 데이터 흐름도(DFD)로 직접 도식화하여 표현하는 공학적 시각화 노력을 기울임.</div>
        </div>
      </div>"""

html = html.replace(process_target, process_replacement)

# 3-5. 4. 결론 및 성장
conclusion_target = """      <div class="form-group">
        <label for="conclusion">4. 결론 및 느낀 점 (인식의 변화와 학업적 성장)</label>
        <textarea id="conclusion" name="conclusion" placeholder="'재밌었다'와 같은 감상이 아닌, 이 탐구를 통해 나의 시각이나 문학을 바라보는 관점이 어떻게 성장했는지를 중심으로 기술하세요." required></textarea>
      </div>"""

conclusion_replacement = """      <div class="form-group">
        <label for="conclusion">4. 결론 및 느낀 점 (인식의 변화와 학업적 성장)</label>
        <textarea id="conclusion" name="conclusion" placeholder="'재밌었다'와 같은 감상이 아닌, 이 탐구를 통해 나의 시각이나 문학을 바라보는 관점이 어떻게 성장했는지를 중심으로 기술하세요." required></textarea>
        <button type="button" class="tip-toggle-btn" onclick="toggleTip(this)">💡 작성 팁 및 예시 보기</button>
        <div class="tip-content-panel">
          <h5>결론 및 성장 작성 팁:</h5>
          <p>문학이 과거의 기록이 아닌 현재의 거울임을 자각한 문학관의 성숙과, 자신의 진로 분야에서 어떤 지향점을 가지고 배움을 지속할 것인지 학업 소명감 위주로 매듭짓습니다.</p>
          <div class="example-title">🩺 의학/보건 계열 예시:</div>
          <div class="example-text">문학이 인간 고통의 사회적 지표임을 자각하고, 향후 단순히 세포와 질병을 치료하는 임상의에 머무르지 않고, 사회적 복지와 의료 안전망의 사각지대까지 따뜻하게 살피는 공공의료 분야의 의학 전문가가 되겠다는 사명감을 기름.</div>
          <div class="example-title">💻 공학/IT/AI 계열 예시:</div>
          <div class="example-text">코드 한 줄의 편향이 인권을 침해하는 폭설이 될 수 있음을 직시하고, 효율성만 쫓는 개발자가 아닌, 개인의 생각과 사생활을 침해하지 않도록 윤리적 가이드라인을 준수하고 투명성을 설계하는 '윤리적 인공지능 엔지니어'가 되겠다고 다짐함.</div>
        </div>
      </div>"""

html = html.replace(conclusion_target, conclusion_replacement)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully added interactive guide toggles and samples to 문학_탐구보고서_웹앱_Index.html!")
