/**
 * 2학년 문학 수행평가 '현대적 관점으로 고전시가 비평하기' 시스템 - 백엔드
 * * 제작: Antigravity
 * 기능: 
 * 1. 학생 제출용 웹앱 화면 서빙 (doGet)
 * 2. 명렬 시트의 학급별 학생 명단 로드 (getRoster)
 * 3. 수행평가 비평 답안 수집 및 시트 기록 (submitLiteratureAnswer)
 * 4. Gemini 2.5 Pro 모델을 활용한 생기부 세특 초안 5명 단위 배치 생성 (generateSeteukInBatches)
 * 5. 1명 대상 테스트 생성 (generateSingleTestSeteuk)
 */

const CONFIG = {
  MODEL_NAME: "gemini-2.5-pro",  // 추론 능력, 지시 이행력, 작문 품질이 가장 우수한 최신 안정화 프로 모델
  BATCH_SIZE: 5,                  // 호출 실패 및 할루시네이션 방지를 위한 배치 크기
  RESPONSE_SHEET_NAME: "수행평가_응답",
  ROSTER_SHEET_NAME: "Sheet1"     // 선생님 스프레드시트의 학급 명렬 탭 이름
};

/**
 * 웹앱 배포 시 브라우저 접속을 처리합니다.
 */
function doGet() {
  // 프론트엔드 HTML 파일 이름과 동일하게 맞춰주세요. (기본값: Index)
  return HtmlService.createTemplateFromFile('Index')
      .evaluate()
      .setTitle('2학년 문학 수행평가 - 현대적 관점으로 고전시가 비평하기')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * 스프레드시트가 열릴 때 메뉴를 추가합니다.
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('📝 문학 세특 자동화')
    .addItem('🔑 Gemini API 키 설정', 'promptApiKey')
    .addSeparator()
    .addItem('🧪 테스트 생성 (1명만)', 'generateSingleTestSeteuk')
    .addItem('🤖 세특 초안 생성 (5명씩)', 'generateSeteukInBatches')
    .addItem('🛑 자동 생성 작업 중단 (트리거 해제)', 'menuStopBatch')
    .addToUi();
}

/**
 * 자동 생성을 강제로 중단합니다. (트리거 해제)
 */
function menuStopBatch() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  deleteActiveTriggers();
  ss.toast("백그라운드 자동 세특 생성 트리거가 해제되었습니다.", "작업 중단 완료");
}

/**
 * 'generateSeteukInBatches'에 대한 기존 트리거가 있는지 확인합니다.
 */
function getActiveTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'generateSeteukInBatches') {
      return triggers[i];
    }
  }
  return null;
}

/**
 * 'generateSeteukInBatches'에 대한 기존 트리거를 모두 제거합니다.
 */
function deleteActiveTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'generateSeteukInBatches') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
}

/**
 * 트리거를 생성합니다.
 */
function createBatchTrigger() {
  if (!getActiveTrigger()) {
    ScriptApp.newTrigger('generateSeteukInBatches')
      .timeBased()
      .everyMinutes(1)
      .create();
  }
}

/**
 * 사용자에게 Gemini API 키를 입력받아 스크립트 속성(ScriptProperties)에 저장합니다.
 */
function promptApiKey() {
  var ui = SpreadsheetApp.getUi();
  var response = ui.prompt('Gemini API 키 입력', 'Google AI Studio에서 발급받은 API 키를 입력해 주세요:', ui.ButtonSet.OK_CANCEL);
  
  if (response.getSelectedButton() == ui.Button.OK) {
    var apiKey = response.getResponseText().trim();
    if (apiKey) {
      PropertiesService.getScriptProperties().setProperty('GEMINI_API_KEY', apiKey);
      ui.alert('설정 완료', 'Gemini API 키가 안전하게 저장되었습니다.', ui.ButtonSet.OK);
    } else {
      ui.alert('경고', '올바른 API 키를 입력해 주세요.', ui.ButtonSet.OK);
    }
  }
}

/**
 * 'Sheet1' 시트에서 가로로 배치된 반별 명단(1열: 1반 번호, 2열: 1반 이름, 3열: 2반 번호, 4열: 2반 이름... )을 로드합니다.
 */
function getRoster() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.ROSTER_SHEET_NAME);
    if (!sheet) {
      return { success: false, error: `'${CONFIG.ROSTER_SHEET_NAME}' 시트를 찾을 수 없습니다.` };
    }
    
    var lastRow = sheet.getLastRow();
    if (lastRow < 2) {
      return { success: true, roster: {} };
    }
    
    var data = sheet.getRange(2, 1, lastRow - 1, 20).getValues();
    var roster = {};
    
    for (var b = 1; b <= 10; b++) {
      roster[b] = [];
    }
    
    for (var i = 0; i < data.length; i++) {
      var row = data[i];
      for (var b = 1; b <= 10; b++) {
        var numColIdx = (b - 1) * 2;     
        var nameColIdx = (b - 1) * 2 + 1; 
        
        var num = parseInt(row[numColIdx]);
        var name = row[nameColIdx] ? row[nameColIdx].toString().trim() : "";
        
        if (!isNaN(num) && name && !/^\d+\s*명$/.test(name) && !name.includes("인원") && !name.includes("계")) {
          roster[b].push({
            num: num,
            name: name
          });
        }
      }
    }
    
    for (var b = 1; b <= 10; b++) {
      roster[b].sort(function(x, y) {
        return x.num - y.num;
      });
    }
    
    return { success: true, roster: roster };
  } catch (e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * 학생들이 제출한 수행평가 비평 답안을 '수행평가_응답' 시트에 누적 기록합니다.
 */
function submitLiteratureAnswer(formData) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000);
  } catch (e) {
    return { success: false, error: "서버가 혼잡하여 제출 처리가 실패했습니다. 잠시 후 다시 시도해 주세요." };
  }
  
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
    
    var headers = [
      "제출일시", "반", "번호", "이름", 
      "1. 작품 및 저자", "2. 관점 주제(질문)", "3. 선정 이유", 
      "4. 현대사회 사례", "5. 화자 태도 생각", "6. 극복 노력", "7. 성장 부분",
      "세특 초안 (AI)", "총 글자수", "처리 상태"
    ];

    if (!sheet) {
      sheet = ss.insertSheet(CONFIG.RESPONSE_SHEET_NAME);
      sheet.appendRow(headers);
      sheet.getRange("A1:N1").setFontWeight("bold").setBackground("#f1f5f9");
    } else {
      var lastCol = sheet.getLastColumn();
      if (lastCol > 0 && lastCol <= 12) {
        sheet.getRange(1, 1, 1, 14).setValues([headers]).setFontWeight("bold").setBackground("#f1f5f9");
      }
    }
    
    var timestamp = new Date();
    var ban = parseInt(formData.ban);
    var num = parseInt(formData.num);
    var name = formData.name.trim();
    var q1 = formData.q1 ? formData.q1.trim() : "";
    var q2 = formData.q2 ? formData.q2.trim() : "";
    var q3 = formData.q3 ? formData.q3.trim() : "";
    var q4 = formData.q4 ? formData.q4.trim() : "";
    var q5 = formData.q5 ? formData.q5.trim() : "";
    var q6 = formData.q6 ? formData.q6.trim() : "";
    var q7 = formData.q7 ? formData.q7.trim() : "";
    
    if (isNaN(ban) || isNaN(num) || !name || !q1 || !q2 || !q3 || !q4 || !q5 || !q6 || !q7) {
      return { success: false, error: "제출한 데이터의 필수값이 유효하지 않습니다." };
    }
    
    sheet.appendRow([
      timestamp,
      ban,
      num,
      name,
      q1,
      q2,
      q3,
      q4,
      q5,
      q6,
      q7,
      "", 
      "", 
      "대기" 
    ]);
    
    return { success: true, message: `${name} 학생의 비평문 답안이 성공적으로 제출되었습니다.` };
  } catch (e) {
    return { success: false, error: e.toString() };
  } finally {
    lock.releaseLock();
  }
}

/**
 * '수행평가_응답' 시트에서 '대기' 상태인 첫 번째 학생을 선택해 1명에 대해 세특을 생성 및 팝업으로 보여줍니다.
 */
function generateSingleTestSeteuk() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
  var ui = SpreadsheetApp.getUi();
  
  if (!sheet) {
    ui.alert("경고", `'${CONFIG.RESPONSE_SHEET_NAME}' 시트를 찾을 수 없습니다. 학생들이 먼저 답안을 제출해야 합니다.`, ui.ButtonSet.OK);
    return;
  }
  
  var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
  if (!apiKey) {
    ui.alert("API 키 누락", "메뉴의 '🔑 Gemini API 키 설정'을 통해 먼저 API 키를 입력해 주세요.", ui.ButtonSet.OK);
    return;
  }
  
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    ui.alert("알림", "시트에 데이터가 없습니다. 임의로 데이터를 입력하거나 학생들이 제출한 뒤에 테스트해 주세요.", ui.ButtonSet.OK);
    return;
  }
  
  var range = sheet.getRange(2, 1, lastRow - 1, 14);
  var data = range.getValues();
  
  var targetRowIdx = -1;
  var targetRowData = null;
  
  for (var i = 0; i < data.length; i++) {
    var rowData = data[i];
    var status = rowData[13]; 
    var draft = rowData[11]; 
    var hasData = rowData[4] && rowData[10]; 
    if ((status === "대기" || !status) && !draft && hasData) {
      targetRowIdx = i + 2;
      targetRowData = rowData;
      break;
    }
  }
  
  // 데이터 덮어쓰기 방지: 대기 학생이 없을 경우 경고 후 중단
  if (targetRowIdx === -1) {
    ui.alert("알림", "현재 '대기' 상태인 답안이 없습니다. 이미 모든 학생의 세특 초안이 생성되었습니다.", ui.ButtonSet.OK);
    return;
  }
  
  var studentName = targetRowData[3];
  var q1 = targetRowData[4];
  var q2 = targetRowData[5];
  var q3 = targetRowData[6];
  var q4 = targetRowData[7];
  var q5 = targetRowData[8];
  var q6 = targetRowData[9];
  var q7 = targetRowData[10];
  
  ui.alert("테스트 시작", `${studentName} 학생의 답변으로 AI 세특 생성을 테스트합니다. 잠시만 기다려 주세요.`, ui.ButtonSet.OK);
  
  try {
    var rawDraft = callGeminiApi(studentName, q1, q2, q3, q4, q5, q6, q7, apiKey);
    var cleanDraft = cleanApiResponse(rawDraft);
    var byteCount = calculateByte(cleanDraft);
    
    sheet.getRange(targetRowIdx, 12).setValue(cleanDraft);
    sheet.getRange(targetRowIdx, 13).setValue(`${cleanDraft.length}자 (${byteCount}B)`);
    sheet.getRange(targetRowIdx, 14).setValue("완료").setBackground("#dcfce7"); // 시각적으로 뚜렷하게 표시
    
    ui.alert("테스트 완료", `[생성된 세특 초안]\n\n${cleanDraft}\n\n시트에 성공적으로 기록되었습니다.`, ui.ButtonSet.OK);
  } catch (err) {
    ui.alert("오류 발생", "세특 생성 도중 에러가 발생했습니다: " + err.toString(), ui.ButtonSet.OK);
  }
}

/**
 * '수행평가_응답' 시트에서 '대기' 상태인 학생들을 찾아 5명 단위로 세특을 일괄 자동 생성합니다.
 */
function generateSeteukInBatches() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
  var ui = SpreadsheetApp.getUi();
  
  if (!sheet) {
    var isTriggerActive = getActiveTrigger();
    if (isTriggerActive) {
      console.warn("시트를 찾을 수 없어 백그라운드 작업을 중단합니다.");
      deleteActiveTriggers();
    } else {
      ui.alert("경고", `'${CONFIG.RESPONSE_SHEET_NAME}' 시트를 찾을 수 없습니다. 학생들이 먼저 답안을 제출해야 합니다.`, ui.ButtonSet.OK);
    }
    return;
  }
  
  var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
  if (!apiKey) {
    var isTriggerActive = getActiveTrigger();
    if (isTriggerActive) {
      console.warn("API 키가 누락되어 작업을 중단합니다.");
      deleteActiveTriggers();
    } else {
      ui.alert("API 키 누락", "메뉴의 '🔑 Gemini API 키 설정'을 통해 먼저 API 키를 입력해 주세요.", ui.ButtonSet.OK);
    }
    return;
  }
  
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    var isTriggerActive = getActiveTrigger();
    if (isTriggerActive) {
      deleteActiveTriggers();
    } else {
      ss.toast("처리할 데이터가 없습니다.", "알림");
    }
    return;
  }
  
  var range = sheet.getRange(2, 1, lastRow - 1, 14);
  var data = range.getValues();
  
  var processedCount = 0;
  var hasMoreQueue = false; 
  
  for (var i = 0; i < data.length; i++) {
    var rowData = data[i];
    var status = rowData[13]; 
    var draft = rowData[11]; 
    var hasData = rowData[4] && rowData[10]; 
    
    var isPending = (status === "대기" || !status) && !draft && hasData;
    
    if (isPending) {
      if (processedCount < CONFIG.BATCH_SIZE) {
        var rowIdx = i + 2;
        var studentName = rowData[3]; 
        var q1 = rowData[4]; 
        var q2 = rowData[5]; 
        var q3 = rowData[6]; 
        var q4 = rowData[7]; 
        var q5 = rowData[8]; 
        var q6 = rowData[9]; 
        var q7 = rowData[10]; 
        
        ss.toast(`${studentName} 학생 문학 세특 분석 중...`, "Gemini API 연동");
        
        try {
          var rawDraft = callGeminiApi(studentName, q1, q2, q3, q4, q5, q6, q7, apiKey);
          var cleanDraft = cleanApiResponse(rawDraft);
          var byteCount = calculateByte(cleanDraft);
          
          sheet.getRange(rowIdx, 12).setValue(cleanDraft); 
          sheet.getRange(rowIdx, 13).setValue(`${cleanDraft.length}자 (${byteCount}B)`); 
          sheet.getRange(rowIdx, 14).setValue("완료").setBackground("#dcfce7"); 
          
          processedCount++;
        } catch (err) {
          console.error(`행 ${rowIdx} 오류: ` + err.toString());
          sheet.getRange(rowIdx, 12).setValue("오류 발생: " + err.toString());
          sheet.getRange(rowIdx, 14).setValue("실패").setBackground("#fee2e2");
          processedCount++;
        }
        Utilities.sleep(2000);
      } else {
        hasMoreQueue = true;
        break;
      }
    }
  }
  
  SpreadsheetApp.flush();
  var activeTrigger = getActiveTrigger();
  
  if (processedCount > 0) {
    if (hasMoreQueue) {
      createBatchTrigger();
      ss.toast(`${processedCount}명 완료. 대기자가 있어 1분 뒤 다음 배치가 자동으로 시작됩니다. (스프레드시트를 닫으셔도 백그라운드에서 실행됩니다.)`, "자동 처리 등록");
    } else {
      if (activeTrigger) {
        deleteActiveTriggers();
        ss.toast("모든 대기 학생의 세특 생성이 완료되어 자동화 작업을 종료합니다.", "자동 처리 완료");
      } else {
        ss.toast(`${processedCount}명의 비평문에 대한 생기부 초안이 생성/기록되었습니다.`, "작업 완료");
      }
    }
  } else {
    if (activeTrigger) {
      deleteActiveTriggers();
      ss.toast("모든 작업이 완료되어 백그라운드 작업을 중단합니다.", "자동 처리 완료");
    } else {
      ui.alert("작업 완료", "대기 중인 처리 항목이 없습니다. 모든 학생의 생기부 초안이 작성 완료되었습니다.", ui.ButtonSet.OK);
    }
  }
}

/**
 * Gemini API를 호출하여 2022 개정 교육과정 국어과 역량을 연계하고 기재 금지 요소를 완벽히 배제한 세특 초안을 생성합니다.
 */
function callGeminiApi(studentName, q1, q2, q3, q4, q5, q6, q7, apiKey) {
  var url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.MODEL_NAME}:generateContent?key=${apiKey}`;
  
  var prompt = `
[학생 제출 정보]
- 학생 이름: ${studentName}
- 1. 작품 및 저자: ${q1}
- 2. 관점 주제(질문): ${q2}
- 3. 선정 이유: ${q3}
- 4. 현대사회 사례: ${q4}
- 5. 화자 태도 생각: ${q5}
- 6. 극복 노력: ${q6}
- 7. 성장 부분: ${q7}

[문학 교육과정 성취기준 연계 가이드]
- [12문학01-06]: 문학 작품의 내용과 형식적 요소가 긴밀하게 연관되어 있음을 이해하고 작품을 감상한다.
- [12문학01-10]: 작품 속 인물 및 화자의 성격과 태도 등을 자신과 비교하며 감상한다.
(학생이 제출한 관점 비평(2번), 선정이유(3번), 현대사회사례와의 연결(4번), 화자 태도 분석(5번)이 고전시가에 대한 현대적 해석의 타당성과 어떻게 긴밀하게 연계되는지 정리하고, 어려움 극복노력(6번) 및 성장 과정(7번)을 유기적으로 엮어 세특에 반영하십시오.)

[2022 개정 교육과정 국어과 6대 교과 역량 정의]
1. 비판적·창의적 사고 역량: 다양한 텍스트와 담화를 비판적으로 이해·평가하고, 새로운 의미를 창의적으로 생성하는 역량
2. 디지털·미디어 역량: 디지털·다매체 환경에서 정보를 주체적으로 수용·생산하고, 디지털 기술을 윤리적으로 활용하는 역량
3. 의사소통 역량: 대면·비대면 등 다양한 상황에서 타인과 의미를 공유하고 협력적으로 소통하는 역량
4. 공동체·대인 관계 역량: 공동체의 구성원으로서 타인을 존중·배려하며, 공동체의 문제를 국어 활동을 통해 해결하려는 역량
5. 문화 향유 역량: 국어 문화를 주체적으로 향유하고 가치를 창조하여 삶의 질을 높이는 역량
6. 자기 성찰·계발 역량: 자신의 언어생활을 성찰하고 점검하여 국어 사용 능력을 스스로 발전시켜 나가는 역량

[학교생활기록부 기재 금지 사항 규칙 - 절대 언급 금지]
아래 명시된 정보나 이를 암시하는 내용은 세특 초안에 절대로 기재하지 마십시오.
1. 부모 및 친인척의 사회·경제적 지위 정보: 특정 직업명, 직장명, 직위명, 전문직 명칭(의사, 교수, 변호사 등) 기재 금지.
2. 모든 형태의 교외 활동 실적: 사설 학원, 사교육 기관, 교외 봉사단체, 어학연수, 외부 기관 주관 활동 등 학교 밖 실적 기재 금지.
3. 교내외 수상 경력 언급 금지: 교내 대회 참가 여부, 대회 준비 사실, 모의고사/수능 성적, 수상 사실 언급 금지. (정규 수행평가 과정 및 수업 내 탐구 활동으로 서술할 것)
4. 자격증 명칭 및 지식재산권 정보: 특정 자격증명 기재, 특허/실용신안/상표/디자인 등의 출원 및 등록 사실 기재 금지.
5. 장학금 수혜 내역 및 장학생 선정 여부 기재 금지.
6. 사설 학원이나 특정 사설 단체 상호명 기재 금지.

[세특 초안 작성 지침]
1. **부드럽고 자연스러운 도입**: 딱딱한 기호나 대괄호 키워드로 시작하지 마십시오. 학생의 비평 탐구 활동에 대한 관심과 참여 모습을 묘사하며 자연스럽고 부드럽게 문장을 시작해 주십시오. (예: "문학 시간에 고전시가를 학습한 후..." 또는 "고전시가 속 화자의 정서와 태도에 깊은 관심을 느끼고...")
2. **구체적 사안에 근거한 긍정적 평가**: 학생이 작성한 현대사회의 사례(4번) 분석력과 화자 태도에 대한 분석적 성찰(5번)을 바탕으로, 비평적 사고력과 주체적인 수용 태도를 구체적이고 격려 어린 어조로 작성하십시오.
3. **교과 역량 및 성장 서술**: 6번(어려움 극복)과 7번(배운점/성장)의 구체적인 서술을 적극 녹여내어, 이 활동을 통해 학생이 어떠한 자기 주도적 문제해결력과 국어과 교과 역량의 성장을 보였는지 생생하게 서술해 주십시오.
4. **사실 기반 서술 (할루시네이션 배제)**: 반드시 학생이 실제 답변한 1~7번 텍스트 내용만을 토대로 서술하십시오. 비평문에 전혀 언급되지 않은 성취는 임의로 작성하지 마십시오.
5. **종결 및 호흡 스타일**: 문장을 불필요하게 늘려 쓰지 말고 짧고 명료한 문체로 작성해 주십시오. 문장의 끝은 생활기록부 규격에 맞춰 반드시 '~함.', '~임.', '~서술함.', '~비평함.', '~평가함.' 등 명사형 및 음절형 종결 어미로 조화롭게 끝맺어 주십시오.
6. **글자 수**: 공백 포함 한글 **330자 ~ 370자 내외** (나이스 기준 350자 내외)로 압축도 높게 작성해 주십시오.
7. **출력 형식**: 반드시 아래의 JSON 형식으로만 응답하십시오. 마크다운 기호(\`\`\`)나 다른 설명글은 절대로 포함하지 마십시오.
{ "seteuk": "여기에 세특 내용을 입력하세요." }
`;

  var payload = {
    "contents": [
      {
        "parts": [{ "text": prompt }]
      }
    ],
    "generationConfig": {
      "temperature": 0.4, 
      "maxOutputTokens": 8192,
      "responseMimeType": "application/json",
      "responseSchema": {
        "type": "OBJECT",
        "properties": {
          "seteuk": {
            "type": "STRING",
            "description": "330자에서 370자 내외로 작성된 문학 수행평가 생활기록부 세특 초안"
          }
        },
        "required": ["seteuk"]
      }
    },
    "safetySettings": [
      { "category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE" },
      { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE" },
      { "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE" },
      { "category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE" }
    ]
  };

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  var response = UrlFetchApp.fetch(url, options);
  var responseCode = response.getResponseCode();
  var responseText = response.getContentText();
  
  if (responseCode !== 200) {
    throw new Error(`Gemini API 호출 에러 (HTTP ${responseCode}): ${responseText}`);
  }
  
  var json = JSON.parse(responseText);
  if (json.candidates && json.candidates.length > 0) {
    var candidate = json.candidates[0];
    if (candidate.finishReason && candidate.finishReason !== "STOP") {
      var reasonMsg = `AI 생성 실패 (종료 사유: ${candidate.finishReason}).`;
      if (candidate.finishReason === "SAFETY") {
        reasonMsg += " 입력한 비평문에 유해하거나 부적절한 표현이 포함되어 안전 필터링에 의해 제한되었습니다.";
      } else if (candidate.finishReason === "MAX_TOKENS") {
        reasonMsg += " 출력 가능한 최대 글자수(토큰) 한계를 초과했습니다. maxOutputTokens 설정 값이 충분하지 않거나 AI 모델의 답변 루프 현상일 수 있습니다.";
      } else if (candidate.finishReason === "RECITATION") {
        reasonMsg += " 저작권/인용구 차단 정책에 의해 중단되었습니다.";
      }
      throw new Error(reasonMsg);
    }
    if (candidate.content && candidate.content.parts && candidate.content.parts.length > 0 && candidate.content.parts[0].text) {
      return candidate.content.parts[0].text;
    }
  }
  throw new Error("API 응답 형식이 올바르지 않거나 텍스트를 찾을 수 없습니다.");
}

/**
 * API에서 반환한 텍스트에서 JSON 객체를 안전하게 추출하고 세특 본문만 반환합니다.
 */
function cleanApiResponse(text) {
  if (!text) return "[생성 실패: 빈 응답]";
  
  var cleanText = text.trim();
  // 마크다운 코드 블록 제거 및 보호 처리 강화
  cleanText = cleanText.replace(/^```json/i, '').replace(/^```/, '').replace(/```$/, '').trim();
  
  try {
    var parsed = JSON.parse(cleanText);
    return (parsed.seteuk || parsed.draft || cleanText).trim();
  } catch (e) {
    // JSON 파싱 실패 시 정규식으로 안전하게 추출 시도
    var match = cleanText.match(/"seteuk"\s*:\s*"([\s\S]*?)"/);
    if (match && match[1]) {
      return match[1].replace(/\\"/g, '"').replace(/\\n/g, ' ').trim();
    }
    return cleanText;
  }
}

/**
 * 나이스(NEIS) 규격 맞춤 바이트 수 계산 (한글 3byte 기준)
 */
function calculateByte(str) {
  if (!str) return 0;
  var byteLength = 0;
  for (var i = 0; i < str.length; i++) {
    var code = str.charCodeAt(i);
    if (code === 10) { 
      byteLength += 2; // 개행문자는 보통 2바이트로 처리
    } else if (code === 13) { 
      // CR 무시
    } else if (code > 127) {
      byteLength += 3; // 한글/특수문자는 3바이트
    } else {
      byteLength += 1; // 영문/숫자/공백은 1바이트
    }
  }
  return byteLength;
}

/**
 * 학생이 실시간으로 비평 조언을 요청할 때 호출되는 API 함수입니다.
 */
function getLiteratureFeedback(q1, q2, q3, q4, q5, q6, q7) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000);
  } catch (e) {
    return { success: false, error: "서버 동시 접속자가 많아 대기 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요." };
  }
  
  try {
    var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
    if (!apiKey) {
      return { success: false, error: "교사용 스프레드시트 메뉴에서 Gemini API 키를 먼저 설정해야 합니다." };
    }

    var feedback = callGeminiFeedbackApi(q1, q2, q3, q4, q5, q6, q7, apiKey);
    return { success: true, feedback: feedback };
  } catch (e) {
    return { success: false, error: e.toString() };
  } finally {
    lock.releaseLock();
  }
}

function callGeminiFeedbackApi(q1, q2, q3, q4, q5, q6, q7, apiKey) {
  var modelName = "gemini-2.5-flash"; 
  var url = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${apiKey}`;

  var prompt = `
당신은 고등학교 국어 교사이자 다정한 문학 비평 지도 교사입니다. 
학생이 고전시가 비평 수행평가를 위해 7개 문항에 작성한 초안 답변들을 분석하고, 학생이 스스로 글을 더 고차원적으로 다듬고 깊이 있게 완성할 수 있도록 맞춤형 종합 조언을 주십시오.

[학생의 작성 정보]
- 1. 작품 및 저자: ${q1}
- 2. 관점 주제(질문): ${q2}
- 3. 선정 이유: ${q3}
- 4. 현대사회 사례: ${q4}
- 5. 화자 태도 생각: ${q5}
- 6. 극복 노력: ${q6}
- 7. 성장 부분: ${q7}

[피드백 가이드라인]
1. **친근하고 격려하는 어조**: 고등학교 교사의 따뜻한 조언처럼, 칭찬으로 자신감을 부여하고 부드럽고 다정하게 교정할 지점을 짚어 주십시오. (나이스 규격 세특이 아니므로 명사형 종결어미가 아닌, 자연스러운 어조로 작성해 주십시오.)
2. **개별 문항 검토**: 
   - 3번 선정 이유가 구체적인지, 글자 수 규정(10자~50자)에 알맞은 깊이가 있는지 조언해 주십시오.
   - 4~5번의 현대사회 사례와 화자 태도 성찰이 얼마나 타당하고 유기적인지 피드백해 주십시오.
   - 6~7번의 어려움 극복 및 본인의 배운점이 피상적인 말에 그치지 않고 본인의 주체적 노력과 변화 과정이 잘 기술되었는지 검토해 주십시오.
3. **개선 방향 조언**: 구체적인 작성 예시나 팁을 1~2가지 곁들여서 더 좋은 답변이 될 수 있도록 격려해 주십시오.
4. **글의 형식**: 보기 편하게 줄바꿈과 이모티콘(💡, 📝, ✨ 등)을 사용하여 3~4개의 짧은 단락 또는 불릿 기호로 깔끔하게 구성해 주십시오.

출력:`;

  var payload = {
    "contents": [
      {
        "parts": [{ "text": prompt }]
      }
    ],
    "generationConfig": {
      "temperature": 0.6,
      "maxOutputTokens": 1024
    }
  };

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  var response = UrlFetchApp.fetch(url, options);
  var responseCode = response.getResponseCode();
  var responseText = response.getContentText();

  if (responseCode !== 200) {
    throw new Error(`Gemini API 호출 에러 (HTTP ${responseCode}): ${responseText}`);
  }

  var json = JSON.parse(responseText);
  if (json.candidates && json.candidates.length > 0 && json.candidates[0].content && json.candidates[0].content.parts.length > 0) {
    return json.candidates[0].content.parts[0].text.trim();
  }
  throw new Error("피드백 응답을 가져올 수 없습니다.");
}
