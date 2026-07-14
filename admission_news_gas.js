// admission_news_gas.gs
// 컴퓨터가 꺼져 있어도 구글 클라우드에서 자동 실행되는 앱스스크립트(Google Apps Script) 코드입니다.
// Apps Script (https://script.google.com)에 새 프로젝트를 생성하고 아래 코드를 붙여넣으세요.

// ----------------- 사용자 설정 ----------------- //
var GEMINI_API_KEY = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY'); // ※ Apps Script 속성에 저장된 Gemini API 키를 읽어옵니다.
var MODEL_NAME = "gemini-3.1-flash-lite";

// 텔레그램 봇 토큰 및 채팅 ID
var TELEGRAM_TOKENS = [
  "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY"  // Macro News Bot (단일 사용)
];
var TELEGRAM_CHAT_ID = "8518409134";

// 구글 드라이브 지정 폴더 설정 (지정하신 공유 폴더 ID)
var TARGET_FOLDER_ID = "1phqLh0I4iX5QEteNV-EYfoFwzo7YYe7U";

var AUDIO_INSTRUCTIONS = "[오디오 리뷰 생성 지침]\n" +
"당신들은 교육 및 입시 전략 분야의 베테랑 전문가들입니다. 제가 업로드한 최신 대입 정보 리포트를 바탕으로, 학부모와 교사들에게 실질적인 도움이 되는 심층 오디오 리뷰를 생성해 주세요.\n\n" +
"분량 및 밀도: 시간에 구애받지 말고 텍스트의 모든 입시 정책 변화와 대학별 상세 정보를 충실히 반영하여 대화를 나눠주세요. 단순 요약이 아닌 전문가적 통찰이 필요합니다.\n" +
"대학별 상세 분석 필수: 리포트에 언급된 주요 대학들의 모집 인원 변화나 전형 방식의 미세한 차이를 반드시 상세히 다뤄주세요.\n" +
"전략적 시사점: 정책 변화가 실제 수험생들의 지원 패턴에 어떤 영향을 미칠지 구체적으로 분석해 주세요.\n" +
"한국어로 만드시오.\n\n---\n";
// ----------------------------------------------- //

function logMessage(message) {
  var timestamp = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss");
  var fullMessage = "[" + timestamp + "] [Admission] " + message;
  Logger.log(fullMessage);
}

function callGeminiApi(prompt) {
  var url = "https://generativelanguage.googleapis.com/v1beta/models/" + MODEL_NAME + ":generateContent?key=" + GEMINI_API_KEY;
  var payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "tools": [{"googleSearch": {}}], // 구글 검색 도구 사용
    "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.2}
  };
  
  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(url, options);
    var json = JSON.parse(response.getContentText());
    if (response.getResponseCode() !== 200) {
      logMessage("API 오류: " + response.getContentText());
      return null;
    }
    if (json.candidates && json.candidates.length > 0) {
      var parts = json.candidates[0].content.parts;
      var text = "";
      for (var i = 0; i < parts.length; i++) {
        if (parts[i].text) {
          text += parts[i].text;
        }
      }
      return text;
    }
  } catch (e) {
    logMessage("API 호출 예외 발생: " + e.toString());
  }
  return null;
}

function sendTelegramAlert(fileName, promptText) {
  var text = "📝 [대입 정보 텍스트 추출 완료]\n\n이번 주 대입 정보 파일(" + fileName + ") 추출 및 검증이 완료되었습니다.\n직접 NotebookLM에 업로드하여 오디오 리뷰를 생성해 주세요.";
  
  for (var i = 0; i < TELEGRAM_TOKENS.length; i++) {
    var token = TELEGRAM_TOKENS[i];
    try {
      var url = "https://api.telegram.org/bot" + token + "/sendMessage";
      
      // 1. 상태 알림 전송
      UrlFetchApp.fetch(url, {
        "method": "post",
        "payload": {
          "chat_id": TELEGRAM_CHAT_ID,
          "text": text
        },
        "muteHttpExceptions": true
      });
      
      // 2. 마스터 프롬프트 전송
      UrlFetchApp.fetch(url, {
        "method": "post",
        "payload": {
          "chat_id": TELEGRAM_CHAT_ID,
          "text": promptText
        },
        "muteHttpExceptions": true
      });
      
      logMessage("텔레그램 알림 전송 완료! (Bot index: " + i + ")");
      return; // 하나라도 성공하면 루프 종료
    } catch(e) {
      logMessage("텔레그램 전송 실패 (Bot index: " + i + "): " + e.toString());
    }
  }
  logMessage("모든 텔레그램 봇 전송에 실패했습니다.");
}

function verifyReport(content, nowDateStr) {
  logMessage("🔍 [Harness] 3단계 무결성 검증을 시작합니다...");
  
  var p1 = "당신은 입시 리포트 검증 전문가입니다. 현재 날짜는 " + nowDateStr + "이며, 주요 타겟은 '2027학년도' 대입입니다. 리포트에 연도 오류가 있는지 확인하고 [PASS] 혹은 수정 가이드를 작성하세요.\n\n" + content;
  var p2 = "리포트의 주요 대학 모집 인원 및 전형 수치(숫자)를 구글 검색으로 검증하세요. 2027학년도 대입 시행계획 기준입니다. [PASS] 혹은 오류 수정을 알려주세요.\n\n" + content;
  var p3 = "리포트가 입시 마인드셋과 주간 체크포인트를 포함하고 있는지 확인하세요. [PASS] 혹은 [MISSING]을 표시하세요.\n\n" + content;

  var results = [];
  var passAll = true;
  var prompts = [p1, p2, p3];
  
  for (var i = 0; i < prompts.length; i++) {
    Utilities.sleep(2000); // 짧은 시간 다중 호출에 의한 Rate Limit 방지
    var res = callGeminiApi(prompts[i]);
    res = res || "";
    results.push(res);
    
    if (res.indexOf("[PASS]") === -1) {
      logMessage("검증 " + (i + 1) + "단계 문제 발견: " + res.substring(0, 80));
      passAll = false;
    }
  }
  
  if (passAll) {
    return content;
  }
  
  logMessage("검증 문제 발견으로 인한 리포트 최종 보정 시도 중...");
  var fixPrompt = "다음 리포트와 검증 결과를 바탕으로 최종 보정된 리포트를 작성해 주세요.\n\n원본:\n" + content + "\n\n검증 피드백:\n" + results.join("\n");
  var fixedContent = callGeminiApi(fixPrompt);
  
  return fixedContent ? fixedContent : content;
}

// -------------------------------------------------------------------------------- //
// [신규] 상태 머신 및 체인 트리거 기반의 동적 실행 파이프라인
// 구글 앱스스크립트 6분 Timeout을 회피하기 위해 단계별로 실행하고 다음 단계를 예약합니다.
// -------------------------------------------------------------------------------- //

// 이전 스텝의 이어달리기(체인)용 임시 트리거를 깔끔하게 지우고 1분 뒤에 실행되도록 예약합니다.
function scheduleNextRun() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'continueAdmissionProcess') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
  // 1분 뒤에 continueAdmissionProcess 재실행 예약
  ScriptApp.newTrigger('continueAdmissionProcess')
           .timeBased()
           .after(1 * 60 * 1000)
           .create();
  logMessage("다음 단계 실행을 위해 1분 뒤 트리거를 예약했습니다.");
}

// 트리거가 이 함수를 반복적으로 호출하여 징검다리 식으로 파이프라인을 이어갑니다.
function continueAdmissionProcess() {
  var props = PropertiesService.getScriptProperties();
  var step = props.getProperty('ADMISSION_STEP');
  var nowDateStr = props.getProperty('NOW_DATE_STR');
  
  if (!step) {
    logMessage("실행할 단계가 없습니다. 처리가 이미 완료되었거나 초기화되지 않았습니다.");
    return;
  }
  
  logMessage("--- [실행 단계: STEP " + step + "] ---");

  if (step === '1') {
    var prompt1 = "당신은 대한민국 최고의 입시 전문가입니다. 현재 날짜는 " + nowDateStr + "입니다. 이번 주 교육부와 한국대학교육협의회(대교협)의 보도자료 및 핵심 입시 정책 변화를 심층 분석해 주세요. 2027/2028학년도 무전공, 첨단학과 정원 등 주요 변화를 다루세요. \n[요구사항] 단순 요약을 절대 금지하며, 이전 학년도와의 구체적인 수치(모집 인원, 전형 비율 변화 등)를 반드시 포함할 것. 보고서 수준의 밀도 있는 문장으로 최소 500자 이상 작성할 것.";
    var content1 = callGeminiApi(prompt1);
    if (content1) {
      props.setProperty('CONTENT_1', content1);
      props.setProperty('ADMISSION_STEP', '2');
      scheduleNextRun();
    } else {
      logMessage("1단계 API 호출 실패. 다음 번에 다시 시도해야 합니다.");
    }
    return; // 이번 턴 스크립트 실행 종료 (6분 초과 방지)
  }
  
  if (step === '2') {
    var prompt2 = "앞서 파악한 입시 정책 변화를 바탕으로, 서연고(SKY) 및 주요 수도권 대학 입학처의 최근 1주일 내 '신규 공지사항'만 타겟팅하여 세부 전형 변화를 분석해 주세요.\n[요구사항] 단순 요약을 절대 금지하며, 대학별 구체적인 수치(인원 증감, 비율 변화)를 반드시 포함할 것. 보고서 수준의 밀도 있는 문장으로 최소 500자 이상 작성할 것.";
    var content2 = callGeminiApi(prompt2);
    if (content2) {
      props.setProperty('CONTENT_2', content2);
      props.setProperty('ADMISSION_STEP', '3');
      scheduleNextRun();
    }
    return;
  }
  
  if (step === '3') {
    var prompt3 = "최근 1주일간 뉴스에 보도된 메가스터디, 종로학원 등 주요 입시 기관의 평가나 현장 교사들의 시각을 구글에서 검색하여 요약해 주세요.\n[요구사항] 새롭게 발표된 정책과 전형 변화가 합격선(Cut-off)에 미칠 영향을 구체적 시나리오로 제시할 것. 보고서 수준의 밀도 있는 문장으로 최소 500자 이상 작성할 것.";
    var content3 = callGeminiApi(prompt3);
    if (content3) {
      props.setProperty('CONTENT_3', content3);
      props.setProperty('ADMISSION_STEP', '4');
      scheduleNextRun();
    }
    return;
  }
  
  if (step === '4') {
    var content1 = props.getProperty('CONTENT_1') || "";
    var content2 = props.getProperty('CONTENT_2') || "";
    var content3 = props.getProperty('CONTENT_3') || "";
    
    var prompt4 = "다음은 1~3단계에서 수집된 정보입니다.\n\n[1단계]\n" + content1 + "\n\n[2단계]\n" + content2 + "\n\n[3단계]\n" + content3 + "\n\n이 내용을 모두 종합하여 '교사용 종합 전략 리포트'를 작성해 주세요. 마지막에는 학부모와 학생을 위한 [입시 마인드셋]과 [주간 체크포인트 3가지]를 반드시 포함해 주세요.\n[요구사항] 전체 내용을 구조화하여 보고서 형식으로 작성할 것. 내용이 누락되지 않도록 상세히 작성할 것.";
    var content4 = callGeminiApi(prompt4);
    
    var fullContent = content4 ? content4 : (content1 + "\n\n" + content2 + "\n\n" + content3);
    props.setProperty('FULL_CONTENT', fullContent);
    props.setProperty('ADMISSION_STEP', 'VERIFY');
    scheduleNextRun();
    return;
  }
  
  if (step === 'VERIFY') {
    var fullContent = props.getProperty('FULL_CONTENT') || "";
    
    // 무결성 검증
    var finalContent = verifyReport(fullContent, nowDateStr);
    var finalWithInstr = AUDIO_INSTRUCTIONS + finalContent;
    
    var now = new Date();
    var fileDateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), "yyyyMMdd");
    var fileName = fileDateStr + "_Admission_Info.txt";
    
    try {
      var folder = DriveApp.getFolderById(TARGET_FOLDER_ID);
      folder.createFile(fileName, finalWithInstr, MimeType.PLAIN_TEXT);
      logMessage("파일 저장 완료: " + fileName + " (구글 드라이브 지정 폴더 저장 성공)");
    } catch(e) {
      logMessage("파일 저장 중 오류 발생: " + e.toString());
    }
    
    // 텔레그램 알림 전송
    var masterPrompt = "당신들은 대한민국 최고의 대입 전략 전문가입니다. 업로드된 리포트를 바탕으로 교사들을 위한 고밀도 오디오 브리핑을 생성해 주세요. 분량에 구애받지 말고 대학별 미세한 차이와 전략적 시사점을 심도 있게 다뤄야 합니다. 한국어로 진행하세요.";
    sendTelegramAlert(fileName, masterPrompt);
    
    // 모든 과정이 끝났으므로 속성 초기화 및 임시 트리거 삭제
    props.deleteProperty('ADMISSION_STEP');
    props.deleteProperty('CONTENT_1');
    props.deleteProperty('CONTENT_2');
    props.deleteProperty('CONTENT_3');
    props.deleteProperty('FULL_CONTENT');
    
    var triggers = ScriptApp.getProjectTriggers();
    for (var i = 0; i < triggers.length; i++) {
      if (triggers[i].getHandlerFunction() === 'continueAdmissionProcess') {
        ScriptApp.deleteTrigger(triggers[i]);
      }
    }
    
    logMessage("🎉 모든 대입 정보 자동 생성 파이프라인이 완료되었습니다!");
    return;
  }
}

// ★ 최초 실행 지점: 매주 수요일 시간 기반 트리거에는 이 함수를 등록하세요!
function runWeeklyTrigger() {
  if (GEMINI_API_KEY === "YOUR_GEMINI_API_KEY_HERE") {
    logMessage("오류: GEMINI_API_KEY가 설정되지 않았습니다.");
    return;
  }

  var now = new Date();
  var nowDateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), "yyyy-MM-dd");
  logMessage("============== 새 대입 정보 생성 파이프라인 시작: " + nowDateStr + " ==============");
  
  var props = PropertiesService.getScriptProperties();
  props.setProperty('NOW_DATE_STR', nowDateStr);
  props.setProperty('ADMISSION_STEP', '1');
  
  // 첫 번째 스텝 실행으로 점화
  continueAdmissionProcess();
}
