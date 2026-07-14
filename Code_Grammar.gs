/**
 * 2학년 국어 문법 'AI 협업 귀납적 문법 탐구 학습' 시스템 - 백엔드 (안정화 버전)
 * * 제작: Antigravity
 */

const CONFIG = {
  MODEL_NAME: "gemini-2.5-pro",        // 세특 작성용 최고 성능 모델
  FEEDBACK_MODEL: "gemini-2.5-flash",  // 실시간 피드백용 초고속 모델
  BATCH_SIZE: 5,
  RESPONSE_SHEET_NAME: "문법_수행평가_응답",
  GROUP_RESPONSE_SHEET_NAME: "문법_조별_응답", 
  ROSTER_SHEET_NAME: "Sheet1",          
  DICTIONARY_SHEET_NAME: "문법_단어_사전", 
  EXAM_DATABASE_SHEET_NAME: "수능_모평_문항_사전",
  
  // 시스템 모드 설정 ("SETEUK" 또는 "ASSESSMENT")
  SYSTEM_MODE: "SETEUK",
  
  // 2022 개정 화법과 언어 성취기준
  ACHIEVEMENT_STANDARD: "[12화언01-02] 표준 발음을 이해하고 정확하게 발음하는 국어생활을 한다."
};

/**
 * 웹앱 접속 시 index_grammar.html 서빙
 */
function doGet(e) {
  var view = e && e.parameter && e.parameter.view;
  if (view === 'teacher') {
    return HtmlService.createTemplateFromFile('dashboard')
        .evaluate()
        .setTitle('교사용 실시간 관제 대시보드 - 문법 탐구')
        .addMetaTag('viewport', 'width=device-width, initial-scale=1.0')
        .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
  }
  return HtmlService.createTemplateFromFile('index_grammar')
      .evaluate()
      .setTitle('2학년 국어 문법 탐구 - AI 협업 가설 검증 학습')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * 스프레드시트 메뉴 추가
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('📝 문법 세특 자동화')
    .addItem('🔑 Gemini API 키 설정', 'promptApiKey')
    .addSeparator()
    .addItem('📖 문법 단어 사전 초기화', 'initDictionarySheet')
    .addSeparator()
    .addItem('🧪 테스트 생성 (1명만)', 'generateSingleTestGrammarSeteuk')
    .addItem('🤖 세특 초안 생성 (5명씩)', 'generateGrammarSeteukInBatches')
    .addItem('🛑 자동 생성 작업 중단 (트리거 해제)', 'menuStopGrammarBatch')
    .addToUi();
}

function menuStopGrammarBatch() {
  deleteActiveGrammarTriggers();
  SpreadsheetApp.getActiveSpreadsheet().toast("문법 세특 자동 생성 백그라운드 트리거가 해제되었습니다.", "작업 중단 완료");
}

function getActiveGrammarTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'generateGrammarSeteukInBatches') {
      return triggers[i];
    }
  }
  return null;
}

function deleteActiveGrammarTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'generateGrammarSeteukInBatches') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
}

function createGrammarBatchTrigger() {
  if (!getActiveGrammarTrigger()) {
    ScriptApp.newTrigger('generateGrammarSeteukInBatches')
      .timeBased()
      .everyMinutes(1)
      .create();
  }
}

function promptApiKey() {
  var ui = SpreadsheetApp.getUi();
  var response = ui.prompt('Gemini API 키 입력', 'Google AI Studio에서 발급받은 API 키를 입력해 주세요:', ui.ButtonSet.OK_CANCEL);
  if (response.getSelectedButton() == ui.Button.OK) {
    var apiKey = response.getResponseText().trim();
    if (apiKey) {
      PropertiesService.getScriptProperties().setProperty('GEMINI_API_KEY', apiKey);
      ui.alert('설정 완료', 'Gemini API 키가 안전하게 저장되었습니다.', ui.ButtonSet.OK);
    }
  }
}

/**
 * 명렬 시트 로드
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
    
    var data = sheet.getRange(2, 1, lastRow - 1, 20).getValues();
    var roster = {};
    for (var b = 1; b <= 10; b++) roster[b] = [];
    
    for (var i = 0; i < data.length; i++) {
      var row = data[i];
      for (var b = 1; b <= 10; b++) {
        var numColIdx = (b - 1) * 2;
        var nameColIdx = (b - 1) * 2 + 1;
        var num = parseInt(row[numColIdx]);
        var name = row[nameColIdx] ? row[nameColIdx].toString().trim() : "";
        if (!isNaN(num) && name && !/^\d+\s*명$/.test(name) && !name.includes("인원")) {
          roster[b].push({ num: num, name: name });
        }
      }
    }
    for (var b = 1; b <= 10; b++) roster[b].sort((x, y) => x.num - y.num);
    return { success: true, roster: roster };
  } catch (e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * AI 실시간 가설 검증 피드백 API 호출 (Socratic)
 */
function getGrammarFeedback(topic, hypothesis, history) {
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
    if (!hypothesis || hypothesis.trim().length < 10) {
      return { success: false, error: "발견한 규칙(가설)을 최소 10자 이상 작성해 주세요." };
    }
    var feedback = callGeminiFeedbackApi(topic, hypothesis, history, apiKey);
    return { success: true, feedback: feedback };
  } catch (e) {
    return { success: false, error: e.toString() };
  } finally {
    lock.releaseLock();
  }
}

function callGeminiFeedbackApi(topic, hypothesis, history, apiKey) {
  var url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.FEEDBACK_MODEL}:generateContent?key=${apiKey}`;
  
  var dictMatch = lookupDictionary(hypothesis);
  var factContext = "";
  if (dictMatch) {
    factContext = `
[RAG 사전 조회 결과 - 절대적 팩트 자료]
- 대상 단어: ${dictMatch.word}
- 표준 발음: [${dictMatch.pronunciation}]
- 적용된 음운 변동 유형: ${dictMatch.changeType}
- 학교 문법 탐구 가이드라인: ${dictMatch.points}

이 단어의 발음 및 음운 변동 정보를 절대적으로 신뢰하여 피드백을 구성하십시오. 절대 학생에게 표준 발음이나 변동 규칙명을 먼저 다 알려주지 마십시오.`;
  }
  
  var examMatch = lookupExamDatabase(hypothesis);
  var examContext = "";
  if (examMatch) {
    examContext = `
[RAG 수능/모의평가 기출 연계 자료]
- 시험명: ${examMatch.examName} (${examMatch.qNum}번 문항)
- 음운론 유형: ${examMatch.phonologyType}
- 문제 내용: ${examMatch.qContent}
- <보기> 내용: ${examMatch.boxContent}
- 선지 정보: ${examMatch.options}
- 정답: ${examMatch.answer}번
- 해설 요약: ${examMatch.explanation}

이 최신 기출문제 데이터를 적극적으로 활용하여 학생에게 힌트나 질문을 던져주십시오.
예를 들어, "이 규칙은 최신 ${examMatch.examName} ${examMatch.qNum}번 문항에 나온 '${examMatch.phonologyType}' 연관 현상과 일치하네요! 혹시 그 문제에서 어떻게 설명하고 있는지 떠올려 볼 수 있을까요?" 또는 해당 문항의 보기나 예시를 변형하여 반례나 탐구 질문으로 제시해 주십시오.`;
  }
  
  var systemInstructionText = `당신은 고등학교 국어 교사이자, 학생의 귀납적 문법 탐구를 이끄는 소크라테스식 대화 멘토입니다.
학생들이 주어진 언어 데이터를 바탕으로 세운 문법 규칙 가설에 대해 친절하게 평가하고 피드백을 제공하십시오.

[필수 준수 규칙]
1. **의미 없는 입력 차단 (Nonsense Detection)**:
   - 학생의 입력이 무의미한 자음/모음의 나열(예: 'ㅋㅋㅋ', 'ㄱㄱㄱ', 'ㅎㅎㅎ'), 의미 없는 숫자나 기호/알파벳의 단순 반복(예: '1'을 여러 개 반복하여 적는 행위, 'asdfasdf'), 비속어, 혹은 오늘 탐구하는 문법 주제와 전혀 무관한 장난성 글인 경우, **절대로 학생의 관찰력을 칭찬하거나 맞다고 수긍(동조)하지 마십시오.**
   - 이 경우, 정중하지만 단호하게 "어라? 의미 없는 텍스트나 장난성 글이 입력되었네요! 오늘 우리가 함께 탐구할 [문법 탐구 주제]와 관련된 가설이나 질문을 던져주면 AI 튜터가 친절하게 도와줄 수 있어요. 다시 한 번 발음을 소리 내어 읽어보고 관찰하여 적어볼까요?" 형태로 대답하여 탐구를 올바른 방향으로 즉시 유도하십시오.
2. **소크라테스식 학습 방향 제시 (Scaffolding & Socratic Guidance)**:
   - 절대로 정답(공식 규칙명이나 표준 발음 자체)을 교사(AI)가 먼저 직접 가르쳐주지 마십시오.
   - 이전 대화 이력을 참고하여 학생이 점진적으로 생각의 폭을 넓히고 가설을 정교화할 수 있도록 발전의 방향을 제시하십시오.
   - 만약 학생의 관찰이 막막해 보인다면, 다음과 같이 단계별 관찰 단서(Scaffolding)를 구체적으로 제안하여 참여를 유도하십시오.
     - 예: "먼저 해당 단어들의 받침 자음이 실제 단독으로 발음될 때 대표적으로 어떤 소리로 발음되는지 직접 소리 내어 읽고 적어볼까요?"
     - 예: "받침 자음 뒤에 모음으로 시작하는 문법 형태소가 올 때와 자음으로 시작하는 말이 결합할 때의 발음 차이점을 관찰해 보세요."
3. **용어 및 구조**:
   - 학생이 규칙의 원리를 스스로 깨닫기 전까지는 교과서 속 공식 규칙명을 발설하지 마십시오.
   - 보기 좋게 이모티콘(💡, 🔍, 📝 등)을 섞어 3~4줄의 간결한 한글 텍스트 단락으로 작성해 주십시오.`;

  var historyText = (history && history.length > 0) ? history.join("\n\n") : "이전 대화 없음";
  var userPrompt = `[탐구 문법 주제]
${topic}

[이전 대화 이력]
${historyText}

[학생의 새로운 가설/질문]
"${hypothesis}"
`;

  if (factContext) {
    userPrompt += `\n${factContext}`;
  } else {
    userPrompt += `\n[알림] 단어 사전에서 직접적으로 매칭된 단어가 없습니다. 학교 문법 범위 내에서 학생이 스스로 깨달을 수 있도록 유도해 주세요.`;
  }
  
  if (examContext) {
    userPrompt += `\n${examContext}`;
  }

  var payload = {
    "contents": [{ "parts": [{ "text": userPrompt }] }],
    "systemInstruction": {
      "parts": [{ "text": systemInstructionText }]
    },
    "generationConfig": { "temperature": 0.5, "maxOutputTokens": 8192 }
  };

  var response = UrlFetchApp.fetch(url, {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  });
  
  var responseCode = response.getResponseCode();
  var responseText = response.getContentText();
  if (responseCode !== 200) {
    throw new Error(`Gemini API 호출 에러 (HTTP ${responseCode}): ${responseText}`);
  }
  var json = JSON.parse(responseText);
  if (json.candidates && json.candidates.length > 0 && json.candidates[0].content && json.candidates[0].content.parts.length > 0) {
    return json.candidates[0].content.parts[0].text.trim();
  }
  throw new Error("피드백 생성에 실패했습니다.");
}

/**
 * 문법 수행평가 응답 제출 및 시트 기록
 */
function submitGrammarAnswer(formData) {
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
      "문법 탐구 주제", "최초 수립 가설", 
      "AI 피드백 대화 이력", "최종 수정 가설", 
      "세특 초안 (AI)", "글자수(바이트)", "처리 상태"
    ];

    if (!sheet) {
      sheet = ss.insertSheet(CONFIG.RESPONSE_SHEET_NAME);
      sheet.appendRow(headers);
      sheet.getRange("A1:K1").setFontWeight("bold").setBackground("#f0fdf4");
    } else {
      var lastCol = sheet.getLastColumn();
      if (lastCol > 0 && lastCol <= 8) {
        sheet.getRange(1, 1, 1, 11).setValues([headers]).setFontWeight("bold").setBackground("#f0fdf4");
      }
    }
    
    var timestamp = new Date();
    var ban = parseInt(formData.ban);
    var num = parseInt(formData.num);
    var name = formData.name.trim();
    var topic = formData.topic ? formData.topic.trim() : "";
    var initialHypothesis = formData.initialHypothesis ? formData.initialHypothesis.trim() : "";
    var aiHistory = formData.aiHistory ? formData.aiHistory.trim() : "";
    var finalHypothesis = formData.finalHypothesis ? formData.finalHypothesis.trim() : "";
    
    if (isNaN(ban) || isNaN(num) || !name || !finalHypothesis) {
      return { success: false, error: "제출한 데이터의 필수값이 유효하지 않습니다." };
    }
    
    sheet.appendRow([
      timestamp, ban, num, name, topic,
      initialHypothesis, aiHistory, finalHypothesis,
      "", "", "대기"
    ]);
    
    return { success: true, message: `${name} 학생의 문법 탐구 보고서가 성공적으로 제출되었습니다.` };
  } catch (e) {
    return { success: false, error: e.toString() };
  } finally {
    lock.releaseLock();
  }
}

/**
 * 조별 보고서 기록
 */
function submitGroupAnswer(formData) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000);
  } catch (e) {
    return { success: false, error: "서버가 혼잡하여 조별 보고서 제출이 실패했습니다. 잠시 후 다시 시도해 주세요." };
  }
  
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.GROUP_RESPONSE_SHEET_NAME);
    
    var headers = [
      "제출일시", "반", "조", "조원 명단", 
      "통합 탐구 주제", "조별 통합 분석 보고서", 
      "조별 세특 참고사항 (AI)", "글자수(바이트)", "처리 상태"
    ];

    if (!sheet) {
      sheet = ss.insertSheet(CONFIG.GROUP_RESPONSE_SHEET_NAME);
      sheet.appendRow(headers);
      sheet.getRange("A1:I1").setFontWeight("bold").setBackground("#eff6ff");
    }
    
    var timestamp = new Date();
    var ban = parseInt(formData.ban);
    var groupNum = parseInt(formData.groupNum);
    var members = formData.members.trim();
    var topic = formData.topic ? formData.topic.trim() : "";
    var synthesis = formData.synthesis ? formData.synthesis.trim() : "";
    
    if (isNaN(ban) || isNaN(groupNum) || !members || !synthesis) {
      return { success: false, error: "제출한 조별 데이터의 필수값이 유효하지 않습니다." };
    }
    
    sheet.appendRow([
      timestamp, ban, groupNum, members, topic,
      synthesis, "", "", "완료"
    ]);
    
    return { success: true, message: `${ban}반 ${groupNum}조 조별 통합 보고서가 성공적으로 제출되었습니다.` };
  } catch (e) {
    return { success: false, error: e.toString() };
  } finally {
    lock.releaseLock();
  }
}

/**
 * 문법 세특 초안 생성 (배치 처리)
 */
function generateGrammarSeteukInBatches() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
  
  if (!sheet) return;
  var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
  if (!apiKey) {
    deleteActiveGrammarTriggers();
    return;
  }
  
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return;
  
  var range = sheet.getRange(2, 1, lastRow - 1, 11);
  var data = range.getValues();
  var processedCount = 0;
  var hasMoreQueue = false;
  
  for (var i = 0; i < data.length; i++) {
    var rowData = data[i];
    var status = rowData[10]; 
    var draft = rowData[8];  
    var finalHypo = rowData[7]; 
    var ban = parseInt(rowData[1]); 
    
    var isPending = (status === "대기" || !status) && status !== "완료" && status !== "실패" && !draft;
    
    if (isPending && finalHypo && finalHypo.toString().trim().length > 0) {
      if (processedCount < CONFIG.BATCH_SIZE) {
        var rowIdx = i + 2;
        var studentName = rowData[3];
        var topic = rowData[4];
        var initHypo = rowData[5];
        var aiHistory = rowData[6];
        
        ss.toast(`${studentName} 학생 문법 탐구 분석 중...`, "Gemini API 연동");
        
        var groupSynthesis = "";
        var groupNum = "";
        try {
          var groupSheet = ss.getSheetByName(CONFIG.GROUP_RESPONSE_SHEET_NAME);
          if (groupSheet) {
            var groupLastRow = groupSheet.getLastRow();
            if (groupLastRow >= 2) {
              var groupData = groupSheet.getRange(2, 1, groupLastRow - 1, 6).getValues();
              for (var g = groupData.length - 1; g >= 0; g--) {
                var gBan = parseInt(groupData[g][1]);
                var gMembers = groupData[g][3].toString();
                if (gBan === ban && gMembers.indexOf(studentName) !== -1) {
                  groupSynthesis = groupData[g][5].toString();
                  groupNum = groupData[g][2];
                  break;
                }
              }
            }
          }
        } catch (ge) {
          console.error("조별 보고서 로드 에러: " + ge.toString());
        }
        
        try {
          var rawDraft = callGrammarGeminiApi(studentName, topic, initHypo, aiHistory, finalHypo, apiKey, groupNum, groupSynthesis);
          var cleanDraft = cleanApiResponse(rawDraft);
          var byteCount = calculateByte(cleanDraft);
          
          sheet.getRange(rowIdx, 9).setValue(cleanDraft);
          sheet.getRange(rowIdx, 10).setValue(`${cleanDraft.length}자 (${byteCount}B)`);
          sheet.getRange(rowIdx, 11).setValue("완료").setBackground(null);
          
          processedCount++;
        } catch (err) {
          console.error(`행 ${rowIdx} 오류: ` + err.toString());
          sheet.getRange(rowIdx, 9).setValue("오류 발생: " + err.toString());
          sheet.getRange(rowIdx, 11).setValue("실패").setBackground("#fee2e2");
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
  if (processedCount > 0) {
    if (hasMoreQueue) {
      createGrammarBatchTrigger();
      ss.toast(`${processedCount}명 완료. 대기자가 있어 1분 뒤 연속 실행됩니다.`, "자동화 동작 중");
    } else {
      deleteActiveGrammarTriggers();
      ss.toast("모든 문법 세특 생성 작업이 종료되었습니다.", "자동화 완료");
    }
  }
}

/**
 * 테스트용 1명 생성
 */
function generateSingleTestGrammarSeteuk() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
  var ui = SpreadsheetApp.getUi();
  
  if (!sheet) {
    ui.alert("경고", "제출된 답변 시트가 없습니다.", ui.ButtonSet.OK);
    return;
  }
  var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
  if (!apiKey) {
    ui.alert("API 키 누락", "API 키 설정을 먼저 해주세요.", ui.ButtonSet.OK);
    return;
  }
  
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return;
  
  var range = sheet.getRange(2, 1, lastRow - 1, 11);
  var data = range.getValues();
  var targetRowIdx = -1;
  var targetRowData = null;
  
  for (var i = 0; i < data.length; i++) {
    if (data[i][10] === "대기" || !data[i][8]) {
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
  var topic = targetRowData[4];
  var initHypo = targetRowData[5];
  var aiHistory = targetRowData[6];
  var finalHypo = targetRowData[7];
  var ban = parseInt(targetRowData[1]);
  
  ss.toast(`${studentName} 학생 문법 세특 테스트 중...`, "Gemini API");
  
  var groupSynthesis = "";
  var groupNum = "";
  try {
    var groupSheet = ss.getSheetByName(CONFIG.GROUP_RESPONSE_SHEET_NAME);
    if (groupSheet) {
      var groupLastRow = groupSheet.getLastRow();
      if (groupLastRow >= 2) {
        var groupData = groupSheet.getRange(2, 1, groupLastRow - 1, 6).getValues();
        for (var g = groupData.length - 1; g >= 0; g--) {
          var gBan = parseInt(groupData[g][1]);
          var gMembers = groupData[g][3].toString();
          if (gBan === ban && gMembers.indexOf(studentName) !== -1) {
            groupSynthesis = groupData[g][5].toString();
            groupNum = groupData[g][2];
            break;
          }
        }
      }
    }
  } catch (ge) {
    console.error("조별 보고서 로드 에러: " + ge.toString());
  }
  
  try {
    var rawDraft = callGrammarGeminiApi(studentName, topic, initHypo, aiHistory, finalHypo, apiKey, groupNum, groupSynthesis);
    var cleanDraft = cleanApiResponse(rawDraft);
    var byteCount = calculateByte(cleanDraft);
    
    sheet.getRange(targetRowIdx, 9).setValue(cleanDraft);
    sheet.getRange(targetRowIdx, 10).setValue(`${cleanDraft.length}자 (${byteCount}B)`);
    sheet.getRange(targetRowIdx, 11).setValue("완료").setBackground(null);
    
    SpreadsheetApp.flush();
    ui.alert("테스트 성공", `이름: ${studentName}\n\n[생성된 문법 세특]\n${cleanDraft}`, ui.ButtonSet.OK);
  } catch (err) {
    ui.alert("테스트 실패", err.toString(), ui.ButtonSet.OK);
  }
}

/**
 * 2022 개정 교육과정 국어과 문법 세특 및 수행평가 프롬프트 호출
 */
function callGrammarGeminiApi(studentName, topic, initHypo, aiHistory, finalHypo, apiKey, groupNum, groupSynthesis) {
  var url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.MODEL_NAME}:generateContent?key=${apiKey}`;
  var systemMode = CONFIG.SYSTEM_MODE || "SETEUK";
  
  var hasHistory = initHypo && aiHistory && initHypo.trim().length > 0 && aiHistory.trim().length > 0;
  var processSection = hasHistory ? `\n[학생 개인 탐구 과정 (1차시)]\n- 최초 작성 가설:\n${initHypo}\n- AI 피드백 이력:\n${aiHistory}\n` : "";
  var groupSection = (groupNum && groupSynthesis) ? `\n[조별 협력 과정]\n- 소속 조: ${groupNum}조\n- 통합 보고서:\n${groupSynthesis}\n` : "";

  var prompt = "";
  if (systemMode === "SETEUK") {
    prompt = `
[학생 문법 탐구 수행 정보]
- 학생 이름: ${studentName}
- 개인 탐구 주제: ${topic}
- 개인 최종 수정 가설: ${finalHypo}
${processSection}${groupSection}

[문법 교육과정 성취기준]
- 성취기준: ${CONFIG.ACHIEVEMENT_STANDARD}

[세특 초안 작성 지침]
1. 자연스럽고 주체적인 도입문으로 구성하십시오.
2. AI 피드백을 통해 오개념을 수정하고 정교화한 주체적 성장 과정을 기술하십시오.
3. 조별 협동 보고서 작성을 통한 공동체/대인관계 역량을 조화롭게 기술하십시오.
4. 문장은 명료하게 하고, 끝은 반드시 '~함.', '~임.', '~도출함.' 등의 명사형 종결어미로 끝내십시오.
5. 글자 수: 공백 포함 한글 330자 ~ 370자 내외로 분량을 성실히 채우십시오.
6. 출력 형식: 아래 스키마에 정의된 JSON 형식으로만 완벽히 응답하십시오.
`;
  } else {
    prompt = `
[학생 문법 탐구 수행 정보]
- 학생 이름: ${studentName}
- 개인 탐구 주제: ${topic}
- 개인 최종 수정 가설: ${finalHypo}
${processSection}${groupSection}

[수행평가 채점 기준]
1. 가설의 타당성 (35점) / 2. 탐구 및 정교화 과정 (35점) / 3. 조별 협업 및 자료 통합 (30점)

[평가서 작성 지침]
1. 성적 등급(A/B/C)과 점수(100점 만점)를 맨 앞에 기재하십시오.
2. 강점과 향후 보완점을 상세히 기술해 주십시오.
3. 출력 형식: 반드시 JSON 형식으로 스키마에 맞춰 "seteuk" 필드 하나에 모든 텍스트를 줄바꿈(\\n) 처리하여 응답하십시오.
`;
  }

  // SYSTEM_MODE에 상관없이 스키마 요구사항 고정하여 오류 방지
  var payload = {
    "contents": [{ "parts": [{ "text": prompt }] }],
    "generationConfig": {
      "temperature": 0.4,
      "maxOutputTokens": 8192,
      "responseMimeType": "application/json",
      "responseSchema": {
        "type": "OBJECT",
        "properties": {
          "seteuk": { "type": "STRING", "description": "작성 완료된 세특 초안 또는 평가 피드백 결과물" }
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

  var response = UrlFetchApp.fetch(url, {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  });
  
  var responseCode = response.getResponseCode();
  var responseText = response.getContentText();
  if (responseCode !== 200) {
    throw new Error(`Gemini API 호출 에러 (HTTP ${responseCode}): ${responseText}`);
  }
  var json = JSON.parse(responseText);
  if (json.candidates && json.candidates[0].content && json.candidates[0].content.parts.length > 0) {
    return json.candidates[0].content.parts[0].text;
  }
  throw new Error("세특 생성에 실패했습니다.");
}

function cleanApiResponse(text) {
  if (!text) return "[생성 실패]";
  var cleanText = text.trim().replace(/^```json/i, '').replace(/^```/, '').replace(/```$/, '').trim();
  try {
    var parsed = JSON.parse(cleanText);
    return (parsed.seteuk || parsed.draft || cleanText).trim();
  } catch (e) {
    var match = cleanText.match(/"seteuk"\s*:\s*"([\s\S]*?)"/);
    if (match && match[1]) {
      return match[1].replace(/\\"/g, '"').replace(/\\n/g, '\n').trim();
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
 * 조원별 개별 제출 내역 로드
 */
function getGroupMembersSubmissions(ban, memberNames) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
    if (!sheet) return { success: false, error: "수행평가 제출 내역이 없습니다." };
    
    var lastRow = sheet.getLastRow();
    if (lastRow < 2) return { success: true, data: [] };
    
    var data = sheet.getRange(2, 1, lastRow - 1, 8).getValues();
    var results = [];
    
    for (var i = 0; i < data.length; i++) {
      var row = data[i];
      var sBan = parseInt(row[1]);
      var sName = row[3] ? row[3].toString().trim() : "";
      if (sBan === parseInt(ban) && memberNames.indexOf(sName) !== -1) {
        results.push({
          name: sName,
          topic: row[4] ? row[4].toString().trim() : "",
          finalHypothesis: row[7] ? row[7].toString().trim() : ""
        });
      }
    }
    return { success: true, data: results };
  } catch (e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * 조별 보고서 초안에 대한 AI 피드백 제공
 */
function getGroupReportFeedback(topic, synthesis) {
  try {
    var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
    if (!apiKey) return { success: false, error: "교사용 스프레드시트 메뉴에서 Gemini API 키를 먼저 설정해야 합니다." };
    
    var cleanText = synthesis.replace(/\s/g, "");
    if (cleanText.length < 20) {
      return { success: false, error: "조별 보고서 내용을 최소 20자 이상 입력한 후 검토를 요청해 주세요." };
    }
    
    var feedback = callGeminiGroupFeedbackApi(topic, synthesis, apiKey);
    return { success: true, feedback: feedback };
  } catch (e) {
    return { success: false, error: e.toString() };
  }
}

function callGeminiGroupFeedbackApi(topic, synthesis, apiKey) {
  var url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.FEEDBACK_MODEL}:generateContent?key=${apiKey}`;
  
  var systemInstructionText = `당신은 고등학교 국어 교사이자, 조별 협업 문법 탐구 학습을 지도하는 소크라테스식 멘토입니다.
당신은 오직 [비상교육 2022 개정 화법과 언어 교과서 음운 변동 공식 해설 데이터]의 원리에만 완전히 기반하여 피드백을 제공해야 합니다.

[피드백 가이드라인]
1. 학생들이 협력하여 분석한 흔적에 대해 따뜻하게 칭찬하며 시작하십시오.
2. 보고서 수정안을 직접 작성해 주지 말고 스스로 보완할 수 있도록 반례나 질문을 제시하십시오.
3. 이모티콘을 섞어 3~4줄의 간결한 단락으로 작성하십시오.`;

  var userPrompt = `[조별 통합 탐구 주제]\n${topic}\n\n[학생들의 작성 중인 조별 보고서 내용]\n"${synthesis}"\n`;

  var payload = {
    "contents": [{ "parts": [{ "text": userPrompt }] }],
    "systemInstruction": { "parts": [{ "text": systemInstructionText }] },
    "generationConfig": { "temperature": 0.5, "maxOutputTokens": 8192 }
  };

  var response = UrlFetchApp.fetch(url, {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  });
  
  var responseCode = response.getResponseCode();
  if (responseCode !== 200) throw new Error(`Gemini API 호출 에러 (HTTP ${responseCode})`);
  var json = JSON.parse(response.getContentText());
  return json.candidates[0].content.parts[0].text.trim();
}

/**
 * '문법_단어_사전' 시트 초기화
 */
function initDictionarySheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. 문법_단어_사전 시트 초기화
  var sheet = ss.getSheetByName(CONFIG.DICTIONARY_SHEET_NAME) || ss.insertSheet(CONFIG.DICTIONARY_SHEET_NAME);
  sheet.clear();
  var headers = ["단어(Key)", "표준발음", "적용된 음운변동", "평가원 유사 문항 연계 가이드"];
  sheet.appendRow(headers);
  sheet.getRange(1, 1, 1, 4).setFontWeight("bold").setBackground("#fef08a");
  
  // 2. 수능_모평_문항_사전 시트 초기화 (AI 튜터 연계용)
  var examSheet = ss.getSheetByName(CONFIG.EXAM_DATABASE_SHEET_NAME) || ss.insertSheet(CONFIG.EXAM_DATABASE_SHEET_NAME);
  examSheet.clear();
  var examHeaders = ["ID", "시험명", "문항번호", "음운론유형", "문제내용(발문)", "보기(Box)", "선지(1~5번)", "정답", "해설", "연계 키워드"];
  examSheet.appendRow(examHeaders);
  examSheet.getRange(1, 1, 1, 10).setFontWeight("bold").setBackground("#c084fc");
  
  var rawDb = {
    "음운_데이터": {
      "교체 (음절의 끝소리 규칙 & 된소리되기)": [
        { "구분": "음절의 끝소리 규칙", "표기": "옷, 꽃, 밖, 부엌, 히읗", "실제 발음": "[옫], [꼳], [박], [부억], [히읃]", "탐구 포인트": "국어 음절 끝에서 발음되는 자음은 7개뿐임" },
        { "구분": "된소리되기 (표준발음법 23항)", "표기": "국밥, 닭장", "실제 발음": "[국빱], [닥짱]", "탐구 포인트": "안울림 예사소리 뒤 된소리 변하는 현상" },
        { "구분": "된소리되기 (표준발음법 24항)", "표기": "신고, 넘고", "실제 발음": "[신ː꼬], [넘ː꼬]", "탐구 포인트": "용언 어간 받침 뒤 결합하는 어미 된소리" },
        { "구분": "된소리되기 (표준발음법 26/27항)", "표기": "갈등, 할 것을", "실제 발음": "[갈뜽], [할꺼슬]", "탐구 포인트": "한자어 받침 ㄹ 뒤, 관형사형 어미 뒤 된소리" }
      ],
      "교체 (비음화 & 유음화)": [
        { "구분": "비음화 (자음 앞 비음화)", "표기": "국물, 옷맵시", "실제 발음": "[궁물], [온맵씨]", "탐구 포인트": "비음의 영향을 받아 비음으로 동화" },
        { "구분": "비음화 (ㄹ의 비음화)", "표기": "담력, 막론", "실제 발음": "[담ː녁], [망논]", "탐구 포인트": "유음 ㄹ이 비음 ㄴ으로 변하는 현상" },
        { "구분": "유음화 현상", "표기": "신라, 물난리", "실제 발음": "[실라], [물랄리]", "탐구 포인트": "ㄴ이 ㄹ의 앞뒤에서 ㄹ로 동화" },
        { "구분": "유음화 예외 (ㄹ의 ㄴ발음)", "표기": "생산량, 의견란, 상견례", "실제 발음": "[생산냥], [의ː견난], [상견녜]", "탐구 포인트": "한자어 예외 현상 관찰" }
      ],
      "교체 (구개음화 현상)": [
        { "구분": "구개음화 (기본)", "표기": "굳이, 같이, 미닫이", "실제 발음": "[구지], [가치], [미다지]", "탐구 포인트": "ㄷ, ㅌ이 모음 ㅣ를 만나 ㅈ, ㅊ으로 변함" },
        { "구분": "구개음화 (축약 연계)", "표기": "굳히다, 묻히다", "실제 발음": "[구치다], [무치다]", "탐구 포인트": "ㄷ이 ㅎ과 만나 ㅌ이 된 후 구개음화 연쇄 적용" }
      ],
      "탈락 (자음군 단순화 & 어간 탈락)": [
        { "구분": "자음군 단순화 (겹받침 발음)", "표기": "닭, 값, 읊다, 넓다", "실제 발음": "[닥], [갑], [읍따], [널따]", "탐구 포인트": "두 개의 자음 중 하나 탈락" },
        { "구분": "용언 어간의 'ㅎ' 탈락", "표기": "낳은, 싫어도", "실제 발음": "[나은], [시러도]", "탐구 포인트": "모음 어미 앞 ㅎ 탈락" },
        { "구분": "용언 어간의 'ㄹ' / 'ㅡ' 탈락", "표기": "가니, 꺼", "실제 발음": "[가니], [꺼]", "탐구 포인트": "보편적 탈락 현상 규칙 활용" }
      ],
      "첨가 (ㄴ 첨가 & 반모음 첨가)": [
        { "구분": "'ㄴ' 첨가 현상", "표기": "솜이불, 서울역, 한여름", "실제 발음": "[솜ː니불], [서울력], [한녀름]", "탐구 포인트": "자음 끝+이/야/여/요/유 앞 ㄴ 소리 덧남" },
        { "구분": "반모음 첨가 (표준발음 허용)", "표기": "피어, 아니오", "실제 발음": "[피어/피여], [아니오/아니요]", "탐구 포인트": "반모음 j가 덧나는 현상 표준발음 허용" }
      ],
      "첨가 (사잇소리 현상 & 사이시옷)": [
        { "구분": "사잇소리 (된소리 덧남)", "표기": "냇가, 샛길", "실제 발음": "[내ː까/낻ː까], [새ː낄/샏ː낄]", "탐구 포인트": "합성명사 앞말 모음 뒤 된소리 및 사이시옷 표기" },
        { "구분": "사잇소리 (ㄴ 소리 덧남)", "표기": "콧날, 아랫니", "실제 발음": "[콘날], [아랜니]", "탐구 포인트": "ㄴ, ㅁ 시작 시 앞말 끝 ㄴ 소리 덧남" },
        { "구분": "사잇소리 (ㄴㄴ 소리 덧남)", "표기": "깻잎, 베갯잇", "실제 발음": "[깬닙], [베갠닏]", "탐구 포인트": "모음 이 시작 시 ㄴㄴ 소리 덧남" }
      ],
      "축약 (거센소리되기)": [
        { "구분": "자음 축약 (거센소리되기)", "표기": "좋다, 먹히다, 맏형, 넓히다", "실제 발음": "[조ː타], [머키다], [마텽], [널피다]", "탐구 포인트": "ㄱ,ㄷ,ㅂ,ㅈ이 ㅎ을 만나 거센소리로 축약" }
      ]
    }
  };

  var rows = [];
  for (var category in rawDb.음운_데이터) {
    var items = rawDb.음운_데이터[category];
    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      var words = item.표기.split(",");
      var prons = item["실제 발음"].split(",");
      for (var j = 0; j < words.length; j++) {
        var rawWord = words[j] ? words[j].trim() : "";
        if (!rawWord) continue;
        var cleanWord = rawWord.split("(")[0].trim();
        var cleanPron = prons[j] ? prons[j].replace(/[\[\]]/g, "").trim() : "";
        rows.push([cleanWord, cleanPron, item.구분, item["탐구 포인트"]]);
      }
    }
  }
  if (rows.length > 0) sheet.getRange(2, 1, rows.length, 4).setValues(rows);
  ss.toast("총 " + rows.length + "개의 문법 단어 사전 및 수능/모평 문항 사전이 초기화되었습니다.", "사전 초기화 완료");
}

/**
 * 수능/모의평가 문항 사전 매칭 수행 (RAG 컨텍스트 획득용)
 */
function lookupExamDatabase(hypothesisOrInput) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.EXAM_DATABASE_SHEET_NAME);
    if (!sheet) return null;
    
    var lastRow = sheet.getLastRow();
    if (lastRow < 2) return null;
    
    var data = sheet.getRange(2, 1, lastRow - 1, 10).getValues();
    var inputClean = hypothesisOrInput.replace(/\s/g, "");
    
    for (var i = 0; i < data.length; i++) {
      var row = data[i];
      if (!row || row.length < 10) continue;
      
      var examName = row[1].toString().trim();
      var qNum = row[2].toString().trim();
      var phonologyType = row[3].toString().trim();
      var qContent = row[4].toString().trim();
      var boxContent = row[5].toString().trim();
      var options = row[6].toString().trim();
      var answer = row[7].toString().trim();
      var explanation = row[8].toString().trim();
      var keywords = row[9].toString().split(",");
      
      var isMatched = false;
      
      // 1) 음운론 유형명 매칭
      if (phonologyType && inputClean.indexOf(phonologyType.replace(/\s/g, "")) !== -1) {
        isMatched = true;
      }
      
      // 2) 연계 키워드 매칭
      if (!isMatched && keywords) {
        for (var k = 0; k < keywords.length; k++) {
          var kw = keywords[k].trim();
          if (kw && inputClean.indexOf(kw.replace(/\s/g, "")) !== -1) {
            isMatched = true;
            break;
          }
        }
      }
      
      if (isMatched) {
        return {
          examName: examName,
          qNum: qNum,
          phonologyType: phonologyType,
          qContent: qContent,
          boxContent: boxContent,
          options: options,
          answer: answer,
          explanation: explanation
        };
      }
    }
    return null;
  } catch (e) {
    console.error("lookupExamDatabase 에러: " + e.toString());
    return null;
  }
}

/**
 * 단어 사전 매칭 수행
 */
function lookupDictionary(hypothesisOrInput) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.DICTIONARY_SHEET_NAME);
    if (!sheet) return null;
    
    var lastRow = sheet.getLastRow();
    if (lastRow < 2) return null;
    
    var data = sheet.getRange(2, 1, lastRow - 1, 4).getValues();
    var inputClean = hypothesisOrInput.replace(/\s/g, "");
    
    var sortedRows = data.slice().sort(function(a, b) {
      return b[0].toString().length - a[0].toString().length;
    });
    
    for (var i = 0; i < sortedRows.length; i++) {
      if (!sortedRows[i] || sortedRows[i].length < 4) continue; // 안전장치 추가
      var wordKey = sortedRows[i][0].toString().trim();
      var wordKeyNoSpace = wordKey.replace(/\s/g, "");
      if (wordKeyNoSpace && inputClean.indexOf(wordKeyNoSpace) !== -1) {
        return {
          word: wordKey,
          pronunciation: sortedRows[i][1].toString().trim(),
          changeType: sortedRows[i][2].toString().trim(),
          points: sortedRows[i][3].toString().trim()
        };
      }
    }
    return null;
  } catch (e) {
    console.error("lookupDictionary 에러: " + e.toString());
    return null;
  }
}

function getLogoBase64() {
  try {
    var files = DriveApp.getFilesByName("school_logo.png");
    if (files.hasNext()) {
      var file = files.next();
      var blob = file.getBlob();
      return "data:" + blob.getContentType() + ";base64," + Utilities.base64Encode(blob.getBytes());
    }
  } catch (e) {
    console.error("로고 이미지 로딩 중 오류 발생: " + e.toString());
  }
  return "school_logo.png";
}

/**
 * 교사용 실시간 포스트잇 대시보드 데이터 조회 API (날짜 직렬화 오류 보완)
 */
function getTeacherDashboardData() {
  var debugInfo = {};
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var personalList = [];
    var groupList = [];
    
    debugInfo.spreadsheetId = ss ? ss.getId() : "null";
    debugInfo.spreadsheetName = ss ? ss.getName() : "null";
    
    var personalSheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
    debugInfo.personalSheetName = CONFIG.RESPONSE_SHEET_NAME;
    debugInfo.personalSheetExists = personalSheet ? true : false;
    
    if (personalSheet) {
      var lastRowPersonal = personalSheet.getLastRow();
      debugInfo.lastRowPersonal = lastRowPersonal;
      if (lastRowPersonal >= 2) {
        var personalValues = personalSheet.getRange(2, 1, lastRowPersonal - 1, 11).getValues();
        debugInfo.personalValuesLength = personalValues.length;
        if (personalValues.length > 0) {
          debugInfo.firstRowData = JSON.stringify(personalValues[0]);
        }
        for (var i = 0; i < personalValues.length; i++) {
          var row = personalValues[i];
          var name = row[3] ? row[3].toString().trim() : "";
          if (!name) continue; // 이름이 없는 빈 행 건너뛰기
          
          // 반, 번호 정보 방어적 파싱 ("1반", "01" 등 대응)
          var rawBan = row[1] ? row[1].toString().trim() : "";
          var banNum = parseInt(rawBan.replace(/[^0-9]/g, "")) || 0;
          var rawNum = row[2] ? row[2].toString().trim() : "";
          var numVal = parseInt(rawNum.replace(/[^0-9]/g, "")) || 0;
          
          // 날짜 객체를 문자열로 직렬화하여 전달 (GAS 런타임 에러 차단)
          var formattedDate = row[0] ? Utilities.formatDate(new Date(row[0]), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm") : "";
          
          personalList.push({
            timestamp: formattedDate,
            ban: banNum,
            num: numVal,
            name: name,
            topic: row[4] ? row[4].toString().trim() : "",
            initialHypothesis: row[5] ? row[5].toString().trim() : "",
            aiHistory: row[6] ? row[6].toString().trim() : "",
            historyLength: row[6] ? row[6].toString().length : 0,
            finalHypothesis: row[7] ? row[7].toString().trim() : "",
            status: row[10] ? row[10].toString().trim() : "대기"
          });
        }
      }
    }
    
    var groupSheet = ss.getSheetByName(CONFIG.GROUP_RESPONSE_SHEET_NAME);
    debugInfo.groupSheetExists = groupSheet ? true : false;
    if (groupSheet) {
      var lastRowGroup = groupSheet.getLastRow();
      debugInfo.lastRowGroup = lastRowGroup;
      if (lastRowGroup >= 2) {
        var groupValues = groupSheet.getRange(2, 1, lastRowGroup - 1, 9).getValues();
        debugInfo.groupValuesLength = groupValues.length;
        for (var j = 0; j < groupValues.length; j++) {
          var gRow = groupValues[j];
          var members = gRow[3] ? gRow[3].toString().trim() : "";
          if (!members) continue; // 조원이 없는 빈 행 건너뛰기
          
          // 반, 조 정보 방어적 파싱
          var rawGBan = gRow[1] ? gRow[1].toString().trim() : "";
          var gBanNum = parseInt(rawGBan.replace(/[^0-9]/g, "")) || 0;
          var rawGNum = gRow[2] ? gRow[2].toString().trim() : "";
          var gGroupNum = parseInt(rawGNum.replace(/[^0-9]/g, "")) || 0;
          
          var formattedGroupDate = gRow[0] ? Utilities.formatDate(new Date(gRow[0]), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm") : "";
          
          groupList.push({
            timestamp: formattedGroupDate,
            ban: gBanNum,
            groupNum: gGroupNum,
            members: members,
            topic: gRow[4] ? gRow[4].toString().trim() : "",
            report: gRow[5] ? gRow[5].toString().trim() : "",
            seteuk: gRow[6] ? gRow[6].toString().trim() : "",
            byteCount: gRow[7] ? gRow[7].toString() : "0",
            status: gRow[8] ? gRow[8].toString().trim() : "대기"
          });
        }
      }
    }
    
    return { success: true, personal: personalList, group: groupList, debugInfo: debugInfo };
  } catch (e) {
    return { success: false, error: e.toString(), debugInfo: debugInfo };
  }
}
