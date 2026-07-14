/**
 * 2026학년도 자율적 교육과정 '쉬었음 청년 탐구' 프로젝트 - 백엔드 엔진 (안정화 리팩토링 버전)
 * 제작: Antigravity
 */

const CONFIG = {
  MODEL_NAME: "gemini-2.5-pro",         // 세특 작성용 최고 성능 모델
  FEEDBACK_MODEL: "gemini-2.5-flash",   // 실시간 피드백용 초고속 모델
  BATCH_SIZE: 5,                        // 배치 생성 시 한 번에 처리할 인원 수
  RESPONSE_SHEET_NAME: "쉬었음_개인_응답",
  GROUP_RESPONSE_SHEET_NAME: "쉬었음_조별_응답", 
  ROSTER_SHEET_NAME: "명렬",            // 학급 명렬 데이터 시트
  
  // 학교 자율적 교육과정 성취 지향점
  ACHIEVEMENT_STANDARD: "청년층 '쉬었음' 현상의 거시적 구조(노동시장 미스매치, 수도권 쏠림)와 미시적 심리(번아웃, 상흔 효과)를 다차원적으로 분석하고 대안을 제안하며, 미디어 콘텐츠를 통해 사회적 공론화를 시도함."
};

/**
 * 웹앱 접속 제어 및 HTML 서빙
 */
function doGet(e) {
  var view = e && e.parameter && e.parameter.view;
  if (view === 'teacher') {
    return HtmlService.createTemplateFromFile('dashboard_youth')
        .evaluate()
        .setTitle('교사용 대시보드 - 쉬었음 청년 탐구')
        .addMetaTag('viewport', 'width=device-width, initial-scale=1.0')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
  }
  return HtmlService.createTemplateFromFile('index_youth')
      .evaluate()
      .setTitle('자율 교육과정 탐구 - AI 협업 쉬었음 청년 탐구')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * 스프레드시트 메뉴 UI 추가
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('🎬 쉬었음 청년 세특 자동화')
    .addItem('🔑 Gemini API 키 설정', 'promptApiKey')
    .addSeparator()
    .addItem('🧪 테스트 생성 (대기자 1명)', 'generateSingleTestYouthSeteuk')
    .addItem('🤖 세특 초안 생성 (5명씩 실행)', 'generateYouthSeteukInBatches')
    .addItem('🛑 자동 생성 작업 중단', 'stopYouthBatch')
    .addToUi();
}

function promptApiKey() {
  var ui = SpreadsheetApp.getUi();
  var response = ui.prompt('Gemini API 키 설정', 'Google AI Studio에서 발급받은 API 키를 입력해 주세요:', ui.ButtonSet.OK_CANCEL);
  if (response.getSelectedButton() == ui.Button.OK) {
    var apiKey = response.getResponseText().trim();
    if (apiKey) {
      PropertiesService.getScriptProperties().setProperty('GEMINI_API_KEY', apiKey);
      ui.alert('설정 완료', 'Gemini API 키가 성공적으로 저장되었습니다.', ui.ButtonSet.OK);
    }
  }
}

function stopYouthBatch() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'generateYouthSeteukInBatches') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
  SpreadsheetApp.getActiveSpreadsheet().toast("세특 자동 생성 트리거가 해제되었습니다.", "중단 완료");
}

function createYouthBatchTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  var hasTrigger = false;
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'generateYouthSeteukInBatches') {
      hasTrigger = true;
      break;
    }
  }
  if (!hasTrigger) {
    ScriptApp.newTrigger('generateYouthSeteukInBatches')
      .timeBased()
      .everyMinutes(1)
      .create();
  }
}

/**
 * 학급 명렬 로드 (반, 번호, 이름 드롭다운용)
 */
function getRoster() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.ROSTER_SHEET_NAME);
    if (!sheet) {
      return { success: false, error: `'${CONFIG.ROSTER_SHEET_NAME}' 시트를 찾을 수 없습니다.` };
    }
    var lastRow = sheet.getLastRow();
    if (lastRow < 2) return { success: true, roster: {} };
    
    var data = sheet.getRange(2, 1, lastRow - 1, 4).getValues();
    var roster = {};
    for (var b = 1; b <= 10; b++) roster[b] = [];
    
    for (var i = 0; i < data.length; i++) {
      var ban = parseInt(data[i][0]);
      var num = parseInt(data[i][1]);
      var name = data[i][2] ? data[i][2].toString().trim() : "";
      var team = data[i][3] ? data[i][3].toString().trim() : "";
      if (!isNaN(ban) && ban >= 1 && ban <= 10 && name) {
        roster[ban].push({ num: num, name: name, team: team });
      }
    }
    for (var b = 1; b <= 10; b++) {
      roster[b].sort((x, y) => x.num - y.num);
    }
    return { success: true, roster: roster };
  } catch (e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * AI 실시간 소크라테스식 피드백 엔진
 */
function getSocraticFeedback(topic, content, history) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
  } catch (e) {
    return { success: false, error: "접속자가 많습니다. 잠시 후 다시 시도해 주세요." };
  }
  
  try {
    var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
    if (!apiKey) return { success: false, error: "교사용 스프레드시트 메뉴에서 Gemini API 키를 먼저 설정해야 합니다." };
    if (!content || content.trim().length < 5) return { success: false, error: "의견이나 분석을 최소 5자 이상 작성해 주세요." };
    
    var feedback = callGeminiFeedbackApi(topic, content, history, apiKey);
    return { success: true, feedback: feedback };
  } catch (e) {
    return { success: false, error: e.toString() };
  } finally {
    lock.releaseLock();
  }
}

function callGeminiFeedbackApi(topic, content, history, apiKey) {
  var url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.FEEDBACK_MODEL}:generateContent?key=${apiKey}`;
  
  var systemInstructionText = `당신은 고등학교 사회과 교사이자, '쉬었음 청년 현상' 자율 교육과정 프로젝트를 지도하는 소크라테스식 대화 멘토입니다.
학생들이 세운 가설이나 분석 의견에 대해 스스로 문제를 해결하고 한계점을 인식할 수 있도록 유도하십시오.

[RAG 딥리서치 팩트 데이터베이스]
- 청년 고용률: 2026년 상반기 기준 43.8% (25개월 연속 하락세)
- 대졸 이상 비중: 쉬었음 청년의 46.7%가 대졸 이상의 고학력자 (17만 4천 명)
- 지역 소멸 (창원시): 2015년 청년 인구 86.6만 명에서 최근 64.6만 명으로 급감. 연간 순유출 2,147명에서 12,092명으로 약 5.6배 급증. 청년 가구 평균 부채 1,806만 원 돌파.
- 미시적 노동 실태: 쉬었음 청년의 87.7%는 직장 유경험자이나, 42.2%가 소기업/소상공인, 29.5%가 6개월 미만 단기계약 등 열악한 환경으로 인해 평균 근속 17.8개월에 불과함.
- 소진 원인: 번아웃(27.7%), 심리/정신적 장애(25%). 소진 세부 요인은 진로 불안(38.6%), 직무 과중(16.4%), 회의감(16.1%) 순임.
- 유민상 5분류 모델: 취준-적극형(일시 휴식), 취준-소극형(탈락 누적으로 포기), 이직-적극형(경력 전환), 이직-소극형(직장 트라우마/소진), 취약형(정신질환/돌봄 고립)

[Socratic 개입 지침]
1. 의미 없는 단순 문자나 나태함에 대한 맹목적인 비난이 입력될 경우 ("요즘 애들은 게으르다" 등), 칭찬이나 긍정을 절대 하지 말고 즉각적으로 RAG 통계 팩트(예: 쉬었음 청년 87.7%가 평균 17.8개월을 버틴 노동 유경험자라는 사실)를 반례로 제시하여 구조적 맥락을 상기시키십시오.
2. 학생에게 정답 정책을 바로 다 알려주지 마십시오. "그렇다면 대졸 청년층 비중이 절반에 가까운 통계(46.7%)는 청년들의 직무 역량이 모자라서일까요, 아니면 일자리 미스매치 때문일까요?" 같은 꼬리 질문(Scaffolding)을 던져 스스로 인과를 발견하게 유도하십시오.
3. 보기 좋게 이모티콘(🔍, 💡, 📝 등)을 섞어 3~4줄의 간결한 존댓말로 작성하십시오.`;

  var historyText = (history && history.length > 0) ? history.join("\n\n") : "이전 대화 없음";
  var userPrompt = `[학생 탐구 활동 단계]\n${topic}\n\n[이전 대화 이력]\n${historyText}\n\n[학생의 입력 분석/가설]\n"${content}"`;

  var payload = {
    "contents": [{ "parts": [{ "text": userPrompt }] }],
    "systemInstruction": { "parts": [{ "text": systemInstructionText }] },
    "generationConfig": { "temperature": 0.5, "maxOutputTokens": 4096 }
  };

  var response = UrlFetchApp.fetch(url, {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  });
  
  var responseCode = response.getResponseCode();
  if (responseCode !== 200) {
    throw new Error(`Gemini API 에러 (HTTP ${responseCode}): ${response.getContentText()}`);
  }
  var json = JSON.parse(response.getContentText());
  return json.candidates[0].content.parts[0].text.trim();
}

/**
 * 개인별 1단계 연구 보고서 및 성찰 일지 최종 제출
 */
function submitIndividualReport(formData) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
  } catch (e) {
    return { success: false, error: "제출이 지연되고 있습니다. 잠시 후 다시 시도해 주세요." };
  }
  
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
    
    var headers = [
      "제출일시", "반", "번호", "이름", 
      "최초 가설", "통계 분석", "인과 규명", 
      "연구 제목", "실태 요약", "페르소나 대안", "제도 및 기대효과",
      "AI 대화 이력", "성찰 일지", 
      "세특 초안 (AI)", "글자수(바이트)", "처리 상태"
    ];

    if (!sheet) {
      sheet = ss.insertSheet(CONFIG.RESPONSE_SHEET_NAME);
      sheet.appendRow(headers);
      sheet.getRange("A1:P1").setFontWeight("bold").setBackground("#f0fdf4");
    }
    
    var ban = parseInt(formData.ban);
    var num = parseInt(formData.num);
    var name = formData.name.trim();
    if (isNaN(ban) || isNaN(num) || !name) {
      return { success: false, error: "학생 성함 및 학반 정보가 올바르지 않습니다." };
    }
    
    sheet.appendRow([
      new Date(), ban, num, name,
      formData.initialHypothesis || "",
      formData.statAnalysis || "",
      formData.causeAnalysis || "",
      formData.policyTitle || "",
      formData.policySummary || "",
      formData.policyPersona || "",
      formData.policyEffect || "",
      formData.aiHistory || "",
      formData.reflection || "",
      "", "", "대기"
    ]);
    
    return { success: true, message: `${name} 학생의 개인 보고서가 제출되었습니다.` };
  } catch (e) {
    return { success: false, error: e.toString() };
  } finally {
    lock.releaseLock();
  }
}

/**
 * 12차시 개인 KWL 성찰록 전용 업데이트 API
 */
function submitReflectionOnly(ban, name, reflectionData) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
  } catch (e) {
    return { success: false, error: "서버 락 지연. 잠시 후 다시 제출해 주세요." };
  }
  
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
    if (!sheet) return { success: false, error: "개인 보고서 시트를 찾을 수 없습니다." };
    
    var lastRow = sheet.getLastRow();
    if (lastRow < 2) return { success: false, error: "매칭할 학생 기록이 없습니다." };
    
    var data = sheet.getRange(2, 1, lastRow - 1, 16).getValues();
    var targetRowIdx = -1;
    
    // 가장 최근 제출된 반과 이름이 매칭되는 행 추적
    for (var i = data.length - 1; i >= 0; i--) {
      var sBan = parseInt(data[i][1]);
      var sName = data[i][3].toString().trim();
      if (sBan === parseInt(ban) && sName === name.trim()) {
        targetRowIdx = i + 2;
        break;
      }
    }
    
    if (targetRowIdx === -1) {
      // 1~5차시를 안 쓰고 12차시를 먼저 쓴 경우 새 행 추가
      sheet.appendRow([
        new Date(), ban, "", name,
        "", "", "", "", "", "", "", "", reflectionData,
        "", "", "대기"
      ]);
    } else {
      // 성찰록 업데이트 및 상태 '대기'로 리셋 (세특 재생성 유도)
      sheet.getRange(targetRowIdx, 13).setValue(reflectionData); // M열 (성찰 일지)
      sheet.getRange(targetRowIdx, 16).setValue("대기");       // P열 (상태)
    }
    
    return { success: true, message: `${name} 학생의 12차시 성찰록이 무사히 저장되었습니다.` };
  } catch(e) {
    return { success: false, error: e.toString() };
  } finally {
    lock.releaseLock();
  }
}

/**
 * 모둠별 2단계 시나리오 및 미디어 기획안 제출
 */
function submitGroupScenario(formData) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
  } catch (e) {
    return { success: false, error: "제출 지연 발생. 잠시 후 재시도 바랍니다." };
  }
  
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.GROUP_RESPONSE_SHEET_NAME);
    
    var headers = [
      "제출일시", "반", "조 번호", "모둠장", "모둠원 및 역할", 
      "미디어 유형", "대안 방식 유무", "기획 의도", "핵심 메시지", "페르소나 연출 주안점", 
      "도입부 콘티", "전개부 콘티", "절정부 콘티", "결말부 콘티", 
      "최종 산출물 드라이브 링크", "처리 상태"
    ];

    if (!sheet) {
      sheet = ss.insertSheet(CONFIG.GROUP_RESPONSE_SHEET_NAME);
      sheet.appendRow(headers);
      sheet.getRange("A1:P1").setFontWeight("bold").setBackground("#eff6ff");
    }
    
    var ban = parseInt(formData.ban);
    var groupNum = parseInt(formData.groupNum);
    if (isNaN(ban) || isNaN(groupNum)) {
      return { success: false, error: "학반 및 조 정보가 올바르지 않습니다." };
    }
    
    sheet.appendRow([
      new Date(), ban, groupNum,
      formData.leader || "",
      formData.membersAndRoles || "",
      formData.mediaType || "",
      formData.alternativeType || "일반 촬영 영상",
      formData.purpose || "",
      formData.keyMessage || "",
      formData.personaFocus || "",
      formData.scenarioIntro || "",
      formData.scenarioDev || "",
      formData.scenarioClimax || "",
      formData.scenarioRes || "",
      formData.mediaLink || "",
      "완료"
    ]);
    
    return { success: true, message: `${ban}반 ${groupNum}조의 미디어 기획 및 시나리오 제출이 완료되었습니다.` };
  } catch (e) {
    return { success: false, error: e.toString() };
  } finally {
    lock.releaseLock();
  }
}

/**
 * 교사용 실시간 관제 대시보드 데이터 수집 API
 */
function getTeacherDashboardData() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    
    var pSheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
    var gSheet = ss.getSheetByName(CONFIG.GROUP_RESPONSE_SHEET_NAME);
    
    var personalList = [];
    var groupList = [];
    
    if (pSheet && pSheet.getLastRow() >= 2) {
      var pData = pSheet.getRange(2, 1, pSheet.getLastRow() - 1, 16).getValues();
      for (var i = 0; i < pData.length; i++) {
        var row = pData[i];
        personalList.push({
          timestamp: row[0] ? new Date(row[0]).toISOString() : "",
          ban: row[1],
          num: row[2],
          name: row[3],
          initialHypothesis: row[4],
          statAnalysis: row[5],
          causeAnalysis: row[6],
          policyTitle: row[7],
          policySummary: row[8],
          policyPersona: row[9],
          policyEffect: row[10],
          aiHistory: row[11],
          reflection: row[12],
          seteuk: row[13],
          status: row[15]
        });
      }
    }
    
    if (gSheet && gSheet.getLastRow() >= 2) {
      var gData = gSheet.getRange(2, 1, gSheet.getLastRow() - 1, 9).getValues();
      for (var j = 0; j < gData.length; j++) {
        var grow = gData[j];
        groupList.push({
          timestamp: grow[0] ? new Date(grow[0]).toISOString() : "",
          ban: grow[1],
          groupNum: grow[2],
          members: grow[3],
          mediaType: grow[4],
          scenarioText: grow[5],
          alternativeType: grow[6],
          mediaLink: grow[7]
        });
      }
    }
    
    return {
      success: true,
      personal: personalList,
      group: groupList,
      debugInfo: {
        spreadsheetName: ss.getName(),
        lastRowPersonal: pSheet ? pSheet.getLastRow() : 0,
        personalValuesLength: personalList.length
      }
    };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * 2026학년도 자율적 교육과정 개별 세특 자동 생성 (배치 처리)
 */
function generateYouthSeteukInBatches() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
  if (!sheet) return;
  
  var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
  if (!apiKey) {
    stopYouthBatch();
    return;
  }
  
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return;
  
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
  } catch (e) {
    return; 
  }
  
  try {
    var range = sheet.getRange(2, 1, lastRow - 1, 16);
    var data = range.getValues();
    var processedCount = 0;
    var hasMoreQueue = false;
    
    var targetRows = [];
    for (var i = 0; i < data.length; i++) {
      var rowData = data[i];
      var status = rowData[15];
      var draft = rowData[13];
      
      var isPending = (status === "대기" || !status) && !draft;
      
      if (isPending) {
        if (targetRows.length < CONFIG.BATCH_SIZE) {
          var rowIdx = i + 2;
          targetRows.push({ index: rowIdx, rowData: rowData });
          sheet.getRange(rowIdx, 16).setValue("처리중");
        } else {
          hasMoreQueue = true;
          break;
        }
      }
    }
    
    SpreadsheetApp.flush();
    lock.releaseLock(); 
    
    for (var k = 0; k < targetRows.length; k++) {
      var target = targetRows[k];
      var rowIdx = target.index;
      var rowData = target.rowData;
      var studentName = rowData[3];
      var ban = parseInt(rowData[1]);
      
      ss.toast(`${studentName} 학생 분석 중...`, "AI 세특 기재 고도화");
      
      var groupMedia = "";
      var groupScenario = "";
      var groupNum = "";
      try {
        var groupSheet = ss.getSheetByName(CONFIG.GROUP_RESPONSE_SHEET_NAME);
        if (groupSheet) {
          var gLastRow = groupSheet.getLastRow();
          if (gLastRow >= 2) {
            var gData = groupSheet.getRange(2, 1, gLastRow - 1, 8).getValues();
            for (var g = gData.length - 1; g >= 0; g--) {
              var gBan = parseInt(gData[g][1]);
              var gMembers = gData[g][3].toString();
              if (gBan === ban && gMembers.indexOf(studentName) !== -1) {
                groupNum = gData[g][2];
                groupMedia = gData[g][4];
                groupScenario = gData[g][5];
                break;
              }
            }
          }
        }
      } catch (err) {
        console.error("조별 데이터 매칭 에러: " + err.toString());
      }
      
      try {
        var rawDraft = callYouthGeminiApi(rowData, groupNum, groupMedia, groupScenario, apiKey);
        var cleanDraft = cleanApiResponse(rawDraft);
        var byteCount = calculateByte(cleanDraft);
        
        sheet.getRange(rowIdx, 14).setValue(cleanDraft);
        sheet.getRange(rowIdx, 15).setValue(`${cleanDraft.length}자 (${byteCount}B)`);
        sheet.getRange(rowIdx, 16).setValue("완료").setBackground(null);
        
        processedCount++;
      } catch (err) {
        sheet.getRange(rowIdx, 14).setValue("API 오류: " + err.toString());
        sheet.getRange(rowIdx, 16).setValue("실패").setBackground("#fee2e2");
        processedCount++;
      }
      Utilities.sleep(2000);
    }
    
    SpreadsheetApp.flush();
    if (processedCount > 0) {
      if (hasMoreQueue) {
        createYouthBatchTrigger();
        ss.toast(`${processedCount}명 처리 완료. 대기자가 있어 1분 후 연속 처리됩니다.`, "자동화 실행 중");
      } else {
        stopYouthBatch();
        ss.toast("모든 학생의 자율 교육과정 세특 초안 작성이 완료되었습니다.", "자동화 완료");
      }
    }
  } catch (err) {
    console.error("배치 실행 치명적 오류: " + err.toString());
  } finally {
    try { lock.releaseLock(); } catch(e) {}
  }
}

/**
 * 1명 테스트 생성
 */
function generateSingleTestYouthSeteuk() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
  var ui = SpreadsheetApp.getUi();
  if (!sheet) return;
  
  var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
  if (!apiKey) {
    ui.alert("경고", "Gemini API 키 설정을 완료해 주세요.", ui.ButtonSet.OK);
    return;
  }
  
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return;
  
  var targetRowIdx = -1;
  var targetRowData = null;
  var data = sheet.getRange(2, 1, lastRow - 1, 16).getValues();
  
  for (var i = 0; i < data.length; i++) {
    var status = data[i][15];
    if (status === "대기" || !data[i][13]) {
      targetRowIdx = i + 2;
      targetRowData = data[i];
      break;
    }
  }
  
  if (targetRowIdx === -1) {
    targetRowIdx = lastRow;
    targetRowData = data[data.length - 1];
  }
  
  var studentName = targetRowData[3];
  var ban = parseInt(targetRowData[1]);
  
  var groupMedia = "";
  var groupScenario = "";
  var groupNum = "";
  try {
    var groupSheet = ss.getSheetByName(CONFIG.GROUP_RESPONSE_SHEET_NAME);
    if (groupSheet) {
      var gLastRow = groupSheet.getLastRow();
      if (gLastRow >= 2) {
        var gData = groupSheet.getRange(2, 1, gLastRow - 1, 8).getValues();
        for (var g = gData.length - 1; g >= 0; g--) {
          var gBan = parseInt(gData[g][1]);
          var gMembers = gData[g][3].toString();
          if (gBan === ban && gMembers.indexOf(studentName) !== -1) {
            groupNum = gData[g][2];
            groupMedia = gData[g][4];
            groupScenario = gData[g][5];
            break;
          }
        }
      }
    }
  } catch (e) {}
  
  try {
    var rawDraft = callYouthGeminiApi(targetRowData, groupNum, groupMedia, groupScenario, apiKey);
    var cleanDraft = cleanApiResponse(rawDraft);
    var byteCount = calculateByte(cleanDraft);
    
    sheet.getRange(targetRowIdx, 14).setValue(cleanDraft);
    sheet.getRange(targetRowIdx, 15).setValue(`${cleanDraft.length}자 (${byteCount}B)`);
    sheet.getRange(targetRowIdx, 16).setValue("완료").setBackground(null);
    SpreadsheetApp.flush();
    
    ui.alert("테스트 성공", `이름: ${studentName}\n\n[생성된 세특 초안]\n${cleanDraft}`, ui.ButtonSet.OK);
  } catch (err) {
    ui.alert("테스트 실패", err.toString(), ui.ButtonSet.OK);
  }
}

/**
 * 2022 개정 자율 교육과정 세특 초안 생성 API 호출
 */
function callYouthGeminiApi(rowData, groupNum, groupMedia, groupScenario, apiKey) {
  var url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.MODEL_NAME}:generateContent?key=${apiKey}`;
  
  var studentName = rowData[3];
  
  var sanitize = function(text) {
    if (!text) return "";
    return text.toString().replace(/"/g, '\\"').replace(/\n/g, ' ').replace(/\r/g, '').trim();
  };

  var initialHypo = sanitize(rowData[4]);
  var statAnalysis = sanitize(rowData[5]);
  var causeAnalysis = sanitize(rowData[6]);
  var policyTitle = sanitize(rowData[7]);
  var policySummary = sanitize(rowData[8]);
  var policyPersona = sanitize(rowData[9]);
  var policyEffect = sanitize(rowData[10]);
  var aiHistory = sanitize(rowData[11]);
  var reflection = sanitize(rowData[12]);
  
  var groupInfo = (groupNum && groupMedia) ? `
[모둠 협업 정보]
- 소속 모둠: ${groupNum}조 (기획 미디어 유형: ${groupMedia})
- 모둠 시나리오 기획 내용: ${sanitize(groupScenario).substring(0, 400)}` : "";

  var prompt = `
[학생 자율 교육과정 탐구 수행 정보]
- 학생 이름: ${studentName}
- 1차시 탐구 전 생각/가설: ${initialHypo}
- 2차시 통계청 데이터 교차분석 내용: ${statAnalysis}
- 3~4차시 구조적(수시채용 장벽/미스매치) & 심리적(번아웃/상흔 효과) 원인 규명: ${causeAnalysis}
- 5차시 대안 설계 연구 제목: ${policyTitle}
- 5차시 실태 정의 및 분석 요약: ${policySummary}
- 5차시 페르소나별 해결 대안 및 지역 연계: ${policyPersona}
- 5차시 제도 매핑 및 기대 효과: ${policyEffect}
- 1~5차시 AI 소크라테스 대화이력: ${aiHistory}
- 12차시 최종 KWL 성찰 일지(인식 변화): ${reflection}
${groupInfo}

[세특 초안 작성 지침]
1. 학교생활기록부 '개인별 세부능력 및 특기사항'에 즉시 기재 가능하도록 서술하십시오.
2. 특정 교과명(국어, 사회 등)을 절대 서술에 포함하지 마십시오.
3. 딥리서치 팩트 데이터(예: 대졸 쉬었음 46.7%, 창원 청년 순유출 12,092명, 경력직 선호 수시채용 장벽, 유민상 5분류 페르소나, 상흔 효과 등)를 학생이 탐구 과정에서 구체적으로 어떻게 접목하고 생각의 폭을 넓혔는지(편견 해소 ➡️ 원인 규명) 사실에 근거하여 작성하십시오.
4. 문장의 종결은 반드시 객관적인 관찰 서사체인 '~함.', '~임.', '~발굴함.' 등의 명사형 종결로 끝나야 합니다. (어미 중복 주의)
5. 분량: 한글 공백 포함 330자 ~ 380자 내외로 핵심 활동 내용을 꽉 채워 기입하십시오.
6. 응답 형식: 반드시 아래 JSON 스키마를 준수하여 "seteuk" 필드 하나에 작성본을 반환하십시오.
`;

  var payload = {
    "contents": [{ "parts": [{ "text": prompt }] }],
    "generationConfig": {
      "temperature": 0.45,
      "maxOutputTokens": 4096,
      "responseMimeType": "application/json",
      "responseSchema": {
        "type": "OBJECT",
        "properties": {
          "seteuk": { "type": "STRING", "description": "완성된 개인별 세특 기재 초안" }
        },
        "required": ["seteuk"]
      }
    }
  };

  var response = UrlFetchApp.fetch(url, {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  });
  
  var responseCode = response.getResponseCode();
  if (responseCode !== 200) {
    throw new Error(`API 호출 실패 (HTTP ${responseCode}): ${response.getContentText()}`);
  }
  var json = JSON.parse(response.getContentText());
  return json.candidates[0].content.parts[0].text;
}

function cleanApiResponse(text) {
  if (!text) return "[생성 실패]";
  var cleanText = text.trim().replace(/^```json/i, '').replace(/^```/, '').replace(/```$/, '').trim();
  try {
    var parsed = JSON.parse(cleanText);
    return (parsed.seteuk || cleanText).trim();
  } catch (e) {
    var match = cleanText.match(/"seteuk"\s*:\s*"([\s\S]*?)"/);
    if (match && match[1]) {
      return match[1].replace(/\\"/g, '"').replace(/\\n/g, '\n').replace(/\\r/g, '').trim();
    }
    return cleanText;
  }
}

function calculateByte(str) {
  if (!str) return 0;
  var byteLength = 0;
  for (var i = 0; i < str.length; i++) {
    var code = str.charCodeAt(i);
    if (code === 10) byteLength += 2;
    else if (code === 13) {}
    else if (code > 127) byteLength += 3;
    else byteLength += 1;
  }
  return byteLength;
}

/**
 * 특정 학생이 제출한 1단계 개인 탐구 보고서 내용을 가져옴
 */
function getIndividualReportByStudent(ban, name) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
    if (!sheet) return { success: false, error: "개인 보고서 시트를 찾을 수 없습니다." };
    
    var lastRow = sheet.getLastRow();
    if (lastRow < 2) return { success: false, error: "제출된 기록이 없습니다." };
    
    var data = sheet.getRange(2, 1, lastRow - 1, 16).getValues();
    for (var i = data.length - 1; i >= 0; i--) {
      var sBan = parseInt(data[i][1]);
      var sName = data[i][3].toString().trim();
      if (sBan === parseInt(ban) && sName === name.trim()) {
        return {
          success: true,
          report: {
            initialHypothesis: data[i][4],
            statAnalysis: data[i][5],
            causeAnalysis: data[i][6],
            policyTitle: data[i][7],
            policySummary: data[i][8],
            policyPersona: data[i][9],
            policyEffect: data[i][10]
          }
        };
      }
    }
    return { success: false, error: "해당 학생의 제출 기록을 찾을 수 없습니다." };
  } catch(e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * 학생이 업로드한 파일을 구글 드라이브에 저장하고 공유 링크를 반환함
 */
function uploadFileToDrive(fileName, base64Data, contentType) {
  try {
    var folderName = "2026_자율교육과정_최종산출물제출";
    var folders = DriveApp.getFoldersByName(folderName);
    var folder;
    
    if (folders.hasNext()) {
      folder = folders.next();
    } else {
      folder = DriveApp.createFolder(folderName);
    }
    
    var decoded = Utilities.base64Decode(base64Data);
    var blob = Utilities.newBlob(decoded, contentType, fileName);
    var file = folder.createFile(blob);
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    
    return {
      success: true,
      fileUrl: file.getUrl()
    };
  } catch (e) {
    return { success: false, error: e.toString() };
  }
}
