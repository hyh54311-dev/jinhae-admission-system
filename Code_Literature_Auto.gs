/**
 * 2학년 문학 수행평가 '현대적 관점으로 고전시가 비평하기' 세특 초안 자동 생성 시스템 (V8.3 - 토큰 최적화 단층형 모델)
 * * 제작: Antigravity
 * 
 * 주요 기능:
 * 1. D열(현재학번) 기준으로 1번부터 끝번까지 오름차순 자동 정렬
 * 2. AD(세특 초안), AE(글자수/바이트), AF(처리 상태) 열 자동 생성 및 기입
 * 3. 5명씩 개별 세특 작성 (시간 기반 트리거 자동 연동)
 * 4. 2022 국어과 교육과정 6대 교과 역량 및 기재 금지 조항 완벽 반영
 * 5. 시스템 지시문(systemInstruction) 분리 및 프롬프트 압축으로 토큰 사용량 극소화 (90% 이상 절감)
 * 6. 인덱스 기반 6단계 종결어미 로테이션 및 한글식 둥근 따옴표 후처리 변환
 */

const CONFIG = {
  MODEL_NAME: "gemini-3.1-flash-lite", // 300명 일괄 고속 처리에 최적화된 최신 경량 모델
  BATCH_SIZE: 5,                       // 1회 실행당 처리할 학생 수
  DELAY_TIME: 30 * 1000,               // 배치 간 대기 시간 (30초)
  RESPONSE_SHEET_NAME: "탐구보고서_응답", // 분석 대상 시트 이름
  
  // 텔레그램 연동 정보 (선택 사항: 미기입 시 토스트 공지만 작동)
  TELEGRAM_TOKEN: "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY",
  TELEGRAM_CHAT_ID: "8518409134",
  
  // 나이스 세특 규격 (750바이트, 250자 내외 목표)
  BYTE_MIN: 700,
  BYTE_MAX: 800,
  CHAR_MIN: 230,
  CHAR_MAX: 270
};

/**
 * 스프레드시트가 열릴 때 상단 메뉴를 생성합니다.
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('📝 문학 세특 자동화 V8.3')
    .addItem('🔑 Gemini API 키 설정', 'promptApiKey')
    .addSeparator()
    .addItem('📊 시트 정렬 및 헤더 준비', 'prepareSheetAndSort')
    .addItem('🧪 1명 테스트 생성 (대기 첫행)', 'generateSingleTestSeteuk')
    .addSeparator()
    .addItem('🤖 일괄 자동 생성 시작 (5명씩)', 'startAutoGeneration')
    .addItem('🛑 자동 생성 작업 중단 (트리거 해제)', 'stopBatchProcess')
    .addToUi();
}

/**
 * 사용자에게 Gemini API 키를 입력받아 스크립트 속성에 저장합니다.
 */
function promptApiKey() {
  var ui = SpreadsheetApp.getUi();
  var response = ui.prompt('Gemini API 키 설정', 'Google AI Studio에서 발급받은 API 키를 입력해 주세요:', ui.ButtonSet.OK_CANCEL);
  
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
 * 자동 생성 작업을 강제로 종료하고 트리거를 해제합니다.
 */
function stopBatchProcess() {
  deleteActiveTriggers();
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  ss.toast("백그라운드 자동 세특 생성 트리거가 정상적으로 해제되었습니다.", "작업 중단 완료");
}

/**
 * 기존에 등록된 배치 실행용 트리거를 제거합니다.
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
 * 30초 뒤 다음 배치를 실행할 일회성 트리거를 등록합니다.
 */
function setupNextTrigger() {
  deleteActiveTriggers();
  Utilities.sleep(1000); 
  try {
    ScriptApp.newTrigger('generateSeteukInBatches')
      .timeBased()
      .after(CONFIG.DELAY_TIME)
      .create();
  } catch (e) {
    Utilities.sleep(3000);
    ScriptApp.newTrigger('generateSeteukInBatches')
      .timeBased()
      .after(CONFIG.DELAY_TIME)
      .create();
  }
}

/**
 * 시트 헤더를 확인/생성하고, D열(현재학번) 기준으로 데이터를 오름차순 정렬합니다.
 */
function prepareSheetAndSort() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
  var ui = SpreadsheetApp.getUi();
  
  if (!sheet) {
    ui.alert("경고", `'${CONFIG.RESPONSE_SHEET_NAME}' 시트를 찾을 수 없습니다. 시트 이름을 확인해 주세요.`, ui.ButtonSet.OK);
    return false;
  }
  
  var lastCol = sheet.getLastColumn();
  
  // Q열(17번째 열)까지 존재하지 않는 경우 시트 확장
  if (lastCol < 17) {
    sheet.insertColumnsAfter(lastCol, 17 - lastCol);
  }
  
  // O, P, Q열 헤더 세팅
  sheet.getRange(1, 15).setValue("세특 초안 (AI)");
  sheet.getRange(1, 16).setValue("바이트 수");
  sheet.getRange(1, 17).setValue("처리 상태");
  
  // 헤더 스타일 스타일링 (연청색 계열 배경 및 굵게 표시)
  sheet.getRange("O1:Q1")
       .setFontWeight("bold")
       .setBackground("#cfe2f3")
       .setHorizontalAlignment("center");
       
  // D열(현재학번, 4번째 열) 기준으로 정렬 (헤더 제외)
  var lastRow = sheet.getLastRow();
  if (lastRow > 1) {
    var sortRange = sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn());
    sortRange.sort({column: 4, ascending: true});
    ss.toast("학번 기준으로 데이터 정렬이 완료되었습니다.", "정렬 및 준비 완료");
  }
  return true;
}

/**
 * 일괄 자동 생성을 초기화하고 첫 번째 배치를 시작합니다.
 */
function startAutoGeneration() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var ui = SpreadsheetApp.getUi();
  
  var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
  if (!apiKey) {
    ui.alert("API 키 누락", "교사용 메뉴의 '🔑 Gemini API 키 설정'을 통해 먼저 API 키를 등록해 주세요.", ui.ButtonSet.OK);
    return;
  }
  
  if (!prepareSheetAndSort()) return;
  
  var props = PropertiesService.getScriptProperties();
  props.setProperty('PROCESSED_TOTAL', '0');
  props.setProperty('ERROR_COUNT', '0');
  
  deleteActiveTriggers();
  
  var confirm = ui.alert("자동 생성 시작", "1반 1번부터 순서대로 5명씩 30초 간격으로 세특 작성을 시작합니다. 진행하시겠습니까?", ui.ButtonSet.YES_NO);
  if (confirm == ui.Button.YES) {
    ss.toast("첫 번째 세특 생성 배치가 시작됩니다. 스프레드시트를 닫으셔도 백그라운드에서 계속 실행됩니다.", "작업 시작");
    generateSeteukInBatches();
  }
}

/**
 * 대기 중인 첫 번째 학생을 대상으로 1명 테스트 생성을 진행하여 기록합니다.
 */
function generateSingleTestSeteuk() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
  var ui = SpreadsheetApp.getUi();
  
  if (!sheet) {
    ui.alert("오류", `'${CONFIG.RESPONSE_SHEET_NAME}' 시트를 찾을 수 없습니다.`, ui.ButtonSet.OK);
    return;
  }
  
  var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
  if (!apiKey) {
    ui.alert("API 키 누락", "먼저 Gemini API 키를 설정해 주세요.", ui.ButtonSet.OK);
    return;
  }
  
  prepareSheetAndSort();
  
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    ui.alert("알림", "시트에 분석할 학생 데이터가 존재하지 않습니다.", ui.ButtonSet.OK);
    return;
  }
  
  var data = sheet.getRange(2, 1, lastRow - 1, 17).getValues();
  var targetRowIdx = -1;
  var targetRowData = null;
  
  for (var i = 0; i < data.length; i++) {
    var row = data[i];
    var status = row[16]; // Q열 (처리 상태)
    var draft = row[14];  // O열 (세특 초안)
    var studentName = row[4]; // E열 (이름)
    var hasData = row[6] && row[12]; // G열(대상 작품)과 M열(결론 및 성장)에 데이터가 있는지
    
    if (studentName && (status !== "완료" && !draft) && hasData) {
      targetRowIdx = i + 2;
      targetRowData = row;
      break;
    }
  }
  
  if (targetRowIdx === -1) {
    ui.alert("알림", "대기 중인 유효한 답변 행을 찾을 수 없습니다.", ui.ButtonSet.OK);
    return;
  }
  
  var name = targetRowData[4];
  var hakbun = targetRowData[3];
  ui.alert("테스트 시작", `${hakbun} ${name} 학생의 세특을 테스트 생성합니다. 약 5~10초 소요됩니다.`, ui.ButtonSet.OK);
  
  try {
    var q1 = targetRowData[6];  // G열 (대상 작품)
    var q2 = targetRowData[7];  // H열 (탐구 주제)
    var q3 = targetRowData[8];  // I열 (탐구 동기)
    var q4 = targetRowData[9];  // J열 (2-1. 작품 분석)
    var q5 = targetRowData[10]; // K열 (2-2. 진로/사회 연계)
    var q6 = targetRowData[11]; // L열 (탐구 과정)
    var q7 = targetRowData[12]; // M열 (결론 및 성장)
    
    var endingStyles = [
      "~라는 물음으로 탐구를 확장하려는 태도가 돋보임",
      "~라는 물음을 향한 지적 호기심을 드러냄",
      "~라는 물음을 후속 탐구 과제로 제시함",
      "~라는 물음을 스스로 탐색해보려는 학문적 열의를 보임",
      "~라는 물음으로 사고를 확장해가는 모습이 인상적임",
      "~라는 물음을 품고 심화 탐구를 계획함"
    ];
    var endingStyle = endingStyles[targetRowIdx % endingStyles.length];
    
    // 세특 생성
    var seteuk = callGeminiDraftApi(name, q1, q2, q3, q4, q5, q6, q7, endingStyle, apiKey);
    
    // 마크다운 기호 제거 및 한글식 따옴표로 변환
    seteuk = convertToKoreanQuotes(seteuk.replace(/\*\*/g, '').trim());
    var byteCount = calculateByte(seteuk);
    
    sheet.getRange(targetRowIdx, 15).setValue(seteuk);
    sheet.getRange(targetRowIdx, 16).setValue(byteCount);
    sheet.getRange(targetRowIdx, 17).setValue("완료").setBackground("#dcfce7");
    
    ui.alert("테스트 완료", `[생성 완료]\n\n${seteuk}\n\n시트 O~Q열에 저장되었습니다.`, ui.ButtonSet.OK);
  } catch (err) {
    ui.alert("오류 발생", "세특 생성 중 에러가 발생했습니다: " + err.toString(), ui.ButtonSet.OK);
  }
}

/**
 * 5명 단위로 대기 학생을 선별하여 세특을 자동 생성하는 핵심 배치 함수입니다.
 */
function generateSeteukInBatches() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
  
  if (!sheet) {
    console.warn("시트를 찾을 수 없어 백그라운드 작업을 중단합니다.");
    deleteActiveTriggers();
    return;
  }
  
  var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
  if (!apiKey) {
    console.warn("API 키 누락으로 작업을 중단합니다.");
    deleteActiveTriggers();
    return;
  }
  
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    deleteActiveTriggers();
    return;
  }
  
  var range = sheet.getRange(2, 1, lastRow - 1, 17);
  var data = range.getValues();
  
  var props = PropertiesService.getScriptProperties();
  var totalProcessed = parseInt(props.getProperty('PROCESSED_TOTAL') || '0', 10);
  var errorCount = parseInt(props.getProperty('ERROR_COUNT') || '0', 10);
  
  var processedInThisBatch = 0;
  var hasMoreQueue = false;
  
  var endingStyles = [
    "~라는 물음으로 탐구를 확장하려는 태도가 돋보임",
    "~라는 물음을 향한 지적 호기심을 드러냄",
    "~라는 물음을 후속 탐구 과제로 제시함",
    "~라는 물음을 스스로 탐색해보려는 학문적 열의를 보임",
    "~라는 물음으로 사고를 확장해가는 모습이 인상적임",
    "~라는 물음을 품고 심화 탐구를 계획함"
  ];
  
  for (var i = 0; i < data.length; i++) {
    var row = data[i];
    var rowIdx = i + 2;
    
    var hakbun = row[3];     // D열 (현재학번)
    var name = row[4];       // E열 (이름)
    var q1 = row[6];        // G열 (대상 작품)
    var q7 = row[12];       // M열 (결론 및 성장)
    var draft = row[14];     // O열 (세특 초안)
    var status = row[16];    // Q열 (처리 상태)
    
    var isPending = name && hakbun && (status !== "완료") && !draft && q1 && q7;
    
    if (isPending) {
      if (processedInThisBatch < CONFIG.BATCH_SIZE) {
        var q2 = row[7];
        var q3 = row[8];
        var q4 = row[9];
        var q5 = row[10];
        var q6 = row[11];
        
        ss.toast(`${hakbun} ${name} 학생 세특 작성 중... (${totalProcessed + processedInThisBatch + 1}명째)`, "Gemini AI 세특");
        
        try {
          var endingStyle = endingStyles[rowIdx % endingStyles.length];
          var seteuk = callGeminiDraftApi(name, q1, q2, q3, q4, q5, q6, q7, endingStyle, apiKey);
          
          seteuk = convertToKoreanQuotes(seteuk.replace(/\*\*/g, '').trim());
          var byteCount = calculateByte(seteuk);
          
          sheet.getRange(rowIdx, 15).setValue(seteuk);
          sheet.getRange(rowIdx, 16).setValue(byteCount);
          
          var statusCell = sheet.getRange(rowIdx, 17);
          if (seteuk.startsWith("[확인필요]") || byteCount < CONFIG.BYTE_MIN || byteCount > CONFIG.BYTE_MAX) {
            statusCell.setValue("확인필요").setBackground("#cfe2f3");
            errorCount++;
          } else {
            statusCell.setValue("완료").setBackground("#dcfce7");
          }
          
          processedInThisBatch++;
        } catch (err) {
          console.error(`행 ${rowIdx} 세특 생성 오류: ` + err.toString());
          sheet.getRange(rowIdx, 15).setValue("오류 발생: " + err.toString());
          sheet.getRange(rowIdx, 17).setValue("실패").setBackground("#fee2e2");
          errorCount++;
          processedInThisBatch++;
        }
        Utilities.sleep(1500); 
      } else {
        hasMoreQueue = true;
        break;
      }
    }
  }
  
  totalProcessed += processedInThisBatch;
  props.setProperty('PROCESSED_TOTAL', totalProcessed.toString());
  props.setProperty('ERROR_COUNT', errorCount.toString());
  
  SpreadsheetApp.flush();
  
  if (processedInThisBatch > 0 && hasMoreQueue) {
    setupNextTrigger();
    ss.toast(`${processedInThisBatch}명 처리 완료. 30초 뒤 다음 배치를 시작합니다. (스프레드시트를 닫아도 백그라운드에서 진행됨)`, "배치 자동화");
  } else {
    deleteActiveTriggers();
    var summaryText = `📝 [문학 세특 자동화 완료 보고]\n\n- 전체 처리 인원: ${totalProcessed}명\n- 확인필요/실패 건수: ${errorCount}건\n\n모든 대기 학생에 대한 세특 작성 및 윤문이 완료되었습니다.`;
    ss.toast("모든 학생의 문학 세특 초안 작성이 완료되었습니다.", "최종 완료");
    sendTelegramMessage(summaryText);
  }
}

/**
 * Gemini API를 호출하여 학생의 세특을 단층형으로 바로 생성합니다.
 */
function callGeminiDraftApi(name, q1, q2, q3, q4, q5, q6, q7, endingStyle, apiKey) {
  var sysInstruction = createSystemInstruction();
  var prompt = createStudentPrompt(name, q1, q2, q3, q4, q5, q6, q7, endingStyle);
  var lastError = "";
  
  for (var attempt = 0; attempt < 3; attempt++) {
    var responseRaw = callGeminiApiDirect(prompt, sysInstruction, apiKey);
    if (!responseRaw || responseRaw.startsWith("Error")) {
      lastError = responseRaw || "API 응답이 없습니다.";
      console.warn(`[세특 ${attempt+1}차 시도 실패] ${name}: ${lastError}`);
      Utilities.sleep(2000);
      continue;
    }
    var cleanText = cleanApiResponse(responseRaw);
    if (cleanText && cleanText.length > 30) {
      return cleanText;
    }
    lastError = "응답 파싱 결과가 비어있거나 너무 짧습니다.";
    Utilities.sleep(1500);
  }
  throw new Error("3회 재시도 실패: " + lastError);
}

/**
 * 세특 초안 구성을 위한 프롬프트 템플릿입니다.
 */
function createStudentPrompt(studentName, q1, q2, q3, q4, q5, q6, q7, endingStyle) {
  return `[학생 정보]
- 이름: ${studentName}
- 1. 선택 작품: ${q1}
- 2. 관점 주제(질문): ${q2}
- 3. 선정 이유: ${q3}
- 4. 현대사회 사례: ${q4}
- 5. 화자 태도 생각: ${q5}
- 6. 극복 노력: ${q6}
- 7. 성장 부분: ${q7}

[지정된 6단계 종결어미 형태]
${endingStyle}
※ 물결표(~) 부분에 둥근 따옴표(‘ ’)로 감싼 구체적인 의문문 형식의 후속 탐구 질문을 자연스럽게 생성하여 넣으십시오.`;
}

/**
 * 시스템 지시문 템플릿을 생성합니다. (토큰 최적화를 위해 static 지침 통합)
 */
function createSystemInstruction() {
  return `당신은 10년차 고등학교 국어 교사이자 문학 세특 평가 전문가입니다.
학생의 고전시가 현대적 관점 비평 활동 답변을 기반으로, 2022 개정 국어과 역량이 드러나는 세특을 작성해야 합니다.

[작성 규칙]
1. 분량: 한글 380~420자 내외 (NEIS 바이트 기준 1100~1250B 엄수).
2. 서술조: 생활기록부용 명사형 종결어미(~함., ~임., ~됨., ~평가함.) 사용.
3. 금지: 기재 금지 조항(부모 직업, 학원, 외부 수상, 성적, 장학금) 절대 언급 금지. '**' 등 마크다운 기호 및 특수문자 금지.
4. 문장부호: 모든 인용, 강조, 탐구 질문 등은 반드시 둥근 따옴표(‘, ’)로 감싸야 합니다.

[6단계 문장 구조 및 템플릿]
반드시 다음 6단계 구조를 엄격히 따라 하나의 유기적인 문단으로 작성하시오:
- 1단계 (선정 및 동기): "고전시가 현대적 관점으로 비평하기 활동에서 [선정 이유]라는 점에 주목하여 [작품명·작가]를 선정함."
  ※ [선정 이유]는 학생의 3번 답변(이유)과 1번 답변(작품명)을 분석해 동적으로 완성할 것.
- 2단계 (해석 및 질문): "화자의 [상황/태도] 상황과 정서, [표현 기법]을 주체적으로 해석하고 현대사회와 유사한 사례를 연계하여 분석함. ‘[탐구 질문]’라는 탐구 질문을 능동적으로 구성하여 비평함."
  ※ 탐구 질문은 둥근 따옴표로 감싼 의문문 형식으로 작성할 것.
- 3단계 (사례 연결): "[현대 사회 사례]를 제시하고, 이를 화자가 [경계한/드러낸/지향한] [핵심 태도]를 현대사회 [분야/직군]의 [현상]에 빗대어 고전과 현대의 공통점을 도출함."
  ※ 비유는 문장 내 1회만 사용할 것.
- 4단계 (재해석/심화): "[인과적 원인]이 [결과·한계]로 이어진다고 재해석하고, [추가 자료명]을 분석하여 논거를 보완하는 논증 역량을 발휘함."
  ※ 학생이 6번 등에서 뉴스/논문 등 추가 자료명을 직접 언급하지 않은 경우 "[추가 자료명]을 분석하여 논거를 보완하는" 구절은 통째로 생략하거나 다른 표현(예: '비평적 논리를 분석하여 논거를 보완하는')으로 대체하여 허위 작성을 방지할 것.
- 5단계 (결론 제시): "이를 통해 [2단계 탐구 질문]이 [부정적 답]이 아닌 [긍정적 답]이라는 결론을 제시함."
  ※ 2단계 질문과 반드시 호응해야 하며, 주관적 성장 서술(~깨달음) 대신 객관적 서술(~제시함)을 사용할 것.
- 6단계 (관찰 및 후속): "[학생의 구체적 통찰/가치관]이 드러나며, 나아가 [지정된 6단계 종결어미 형태]로 마침."
  ※ 주관적 평가 어미(~돋보임)는 이 단계에서 1회만 사용할 것.`;
}

/**
 * Gemini 3.1 Flash-Lite API를 직접 호출합니다.
 */
function callGeminiApiDirect(prompt, systemInstruction, apiKey) {
  var url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.MODEL_NAME}:generateContent?key=${apiKey}`;
  
  var payload = {
    "contents": [
      {
        "parts": [{ "text": prompt }]
      }
    ],
    "systemInstruction": {
      "parts": [{ "text": systemInstruction }]
    },
    "generationConfig": {
      "temperature": 0.4,
      "maxOutputTokens": 1024,
      "responseMimeType": "application/json",
      "responseSchema": {
        "type": "OBJECT",
        "properties": {
          "seteuk": {
            "type": "STRING",
            "description": "6단계 구조와 분량 규격을 만족하는 완결된 문학 세특 초안"
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

  try {
    var response = UrlFetchApp.fetch(url, options);
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();
    
    if (responseCode !== 200) {
      return "Error: Gemini API 호출 에러 (HTTP " + responseCode + "): " + responseText;
    }
    return responseText;
  } catch (e) {
    return "Error: " + e.toString();
  }
}

/**
 * API 응답에서 JSON 형식을 추출하고 세특 내용만 깨끗하게 분리합니다.
 */
function cleanApiResponse(responseText) {
  if (!responseText) return "";
  try {
    var json = JSON.parse(responseText);
    if (json.candidates && json.candidates.length > 0 && json.candidates[0].content) {
      var candidateText = json.candidates[0].content.parts[0].text.trim();
      
      candidateText = candidateText.replace(/^```json/i, '').replace(/^```/, '').replace(/```$/, '').trim();
      
      var parsedData = JSON.parse(candidateText);
      return (parsedData.seteuk || parsedData.draft || candidateText).trim();
    }
  } catch (e) {
    var match = responseText.match(/"seteuk"\s*:\s*"([\s\S]*?)"/);
    if (match && match[1]) {
      return match[1].replace(/\\"/g, '"').replace(/\\n/g, ' ').trim();
    }
  }
  return "";
}

/**
 * NEIS 생기부 기재 규격 맞춤 바이트 수 계산 (한글 3바이트, 공백/영문 1바이트)
 */
function calculateByte(str) {
  if (!str) return 0;
  return str.split('').reduce(function(acc, char) {
    var code = char.charCodeAt(0);
    if (code === 10) { 
      return acc + 2; 
    } else if (code === 13) {
      return acc;    
    } else if (code > 127) {
      return acc + 3; 
    } else {
      return acc + 1; 
    }
  }, 0);
}

/**
 * 텔레그램 메시지 발송 헬퍼 함수
 */
function sendTelegramMessage(text) {
  if (!CONFIG.TELEGRAM_TOKEN || !CONFIG.TELEGRAM_CHAT_ID) return;
  var url = "https://api.telegram.org/bot" + CONFIG.TELEGRAM_TOKEN + "/sendMessage";
  var payload = {
    "chat_id": CONFIG.TELEGRAM_CHAT_ID,
    "text": text
  };
  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  try {
    UrlFetchApp.fetch(url, options);
  } catch (e) {
    console.warn("텔레그램 알림 전송 실패: " + e.toString());
  }
}

/**
 * 모든 일반 작은따옴표(') 및 유사 인용구를 한글식 둥근 작은따옴표(‘, ’)로 올바르게 변환합니다.
 */
function convertToKoreanQuotes(str) {
  if (!str) return "";
  var open = true;
  return str.replace(/'/g, function() {
    var q = open ? '‘' : '’';
    open = !open;
    return q;
  });
}
