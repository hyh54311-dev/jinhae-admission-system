// weekday_news_gas.gs
// 주중에 매일 오후 실행되던 구글 앱스스크립트(Google Apps Script) 코드입니다.
// 현재는 K-듀얼 모멘텀 전략 집중을 위해 일시정지(PAUSE) 상태로 세팅되어 있습니다.
// 다시 작동시키고 싶으실 때는 상단의 `PAUSE_WEEKDAY` 변수를 `false`로 변경하세요.
// Apps Script (https://script.google.com)의 주중 뉴스 프로젝트에 아래 코드를 붙여넣으세요.

// ----------------- 사용자 설정 ----------------- //
var PAUSE_WEEKDAY = true; // ★ 주중 데일리 뉴스 일시정지 여부 (true: 일시정지 및 스킵, false: 정상 작동)
var GEMINI_API_KEY = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY'); // ※ Apps Script 속성에 저장된 Gemini API 키를 읽어옵니다.
var MODEL_NAME = "gemini-3.1-flash-lite";

// 텔레그램 봇 토큰 및 채팅 ID
var TELEGRAM_TOKENS = [
  "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY"  // Macro News Bot
];
var TELEGRAM_CHAT_ID = "8518409134";

// 구글 드라이브 지정 폴더 설정 (파일을 저장할 폴더 ID)
var TARGET_FOLDER_ID = "1phqLh0I4iX5QEteNV-EYfoFwzo7YYe7U"; 
// ----------------------------------------------- //

function logMessage(message) {
  var timestamp = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss");
  var fullMessage = "[" + timestamp + "] [WeekdayNews] " + message;
  Logger.log(fullMessage);
}

function callGeminiApi(prompt) {
  var url = "https://generativelanguage.googleapis.com/v1beta/models/" + MODEL_NAME + ":generateContent?key=" + GEMINI_API_KEY;
  var payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "tools": [{"googleSearch": {}}], // 구글 검색 활성화
    "generationConfig": {"maxOutputTokens": 65536, "temperature": 0.2}
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

function sendTelegramAlert(fileName, fileUrl) {
  // HTML 태그를 활용한 하이퍼링크 메시지 포맷 구성
  var text = "📝 <b>[주중 경제 뉴스 생성 완료]</b>\n\n" +
             "오늘의 리포트(<code>" + fileName + "</code>)가 구글 드라이브에 저장되었습니다.\n\n" +
             "🔗 <a href=\"" + fileUrl + "\">여기서 리포트 바로 읽기</a>";
  
  for (var i = 0; i < TELEGRAM_TOKENS.length; i++) {
    var token = TELEGRAM_TOKENS[i];
    try {
      var url = "https://api.telegram.org/bot" + token + "/sendMessage";
      
      UrlFetchApp.fetch(url, {
        "method": "post",
        "payload": {
          "chat_id": TELEGRAM_CHAT_ID,
          "text": text,
          "parse_mode": "HTML" // HTML 형식 적용
        },
        "muteHttpExceptions": true
      });
      
      logMessage("텔레그램 알림 전송 성공 (Bot ID: " + token.split(":")[0] + ")");
      return;
    } catch(e) {
      logMessage("텔레그램 전송 실패: " + e.toString());
    }
  }
}

// 구글 드라이브 폴더에서 과거에 작성했던 경제 브리핑 파일들을 검색해 요약용 리스트 추출
function getPastBriefings(folderId) {
  try {
    var folder = DriveApp.getFolderById(folderId);
    var files = folder.getFiles();
    var pastContents = [];
    var count = 0;
    
    while (files.hasNext() && count < 3) {
      var file = files.next();
      var name = file.getName();
      if (name.indexOf("Macro_Briefing") !== -1) {
        var content = file.getAs("text/plain").getDataAsString();
        pastContents.push("[" + name + "] " + content.substring(0, 500).replace(/\n/g, " ") + "...");
        count++;
      }
    }
    return pastContents.length > 0 ? pastContents.join("\n") : "이전 뉴스 기록이 없습니다.";
  } catch(e) {
    return "이전 기록 조회 실패: " + e.toString();
  }
}

// ========================================================================= //
// ★ [주중 실행 함수] 데일리 코스피 포커스 경제 뉴스 생성
// 트리거 스케줄러 설정: [매일 오후 3시 15분]으로 지정해 두세요.
// ========================================================================= //
function runWeekdayDailyNews() {
  if (PAUSE_WEEKDAY) {
    logMessage("⏸️ 주중 데일리 경제 뉴스 자동 생성이 일시정지 상태이므로 실행을 건너뜁니다.");
    return;
  }
  
  logMessage("🚀 주중 데일리 경제 뉴스 생성 파이프라인 작동...");
  
  var now = new Date();
  var dateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), "yyyyMMdd");
  var dateFullStr = Utilities.formatDate(now, Session.getScriptTimeZone(), "yyyy년 MM월 dd일");
  
  var pastHistory = getPastBriefings(TARGET_FOLDER_ID);
  var targetRank = ((now.getDate() - 1) % 10) + 1; // 일자별로 코스피 시가총액 1위~10위 기업 순환 분석
  
  var prompt = 
    "당신은 AI 경제 전문가입니다. 현재 실제 날짜는 " + dateFullStr + "입니다.\n" +
    "최근 3일간의 브리핑 내용을 분석하여 중복을 방지합니다.\n" +
    "--- 이전 뉴스 이력 ---\n" + pastHistory + "\n--------------------\n\n" +
    "Google Search를 사용하여 오늘자 글로벌 주요국들의 핵심 경제 동향 중 가장 중요한 4가지(이슈 1~4)를 엄선하여 작성해 주세요.\n\n" +
    "이와 별도로 **[우리나라 코스피 상위 기업 포커스]** 섹션을 반드시 포함해야 합니다. 오늘은 **코스피 시가총액 " + targetRank + "위 기업**을 선정하여, " +
    "해당 기업의 **최근 2주 이내(뉴스 생성일 기준)**의 주요 동향과 이슈를 상세 분석해 주세요. (타임스탬프가 2주 이내인 정보만 사용)\n\n" +
    "각 이슈 및 기업 분석은 1)요약/데이터, 2)배경/역사적 맥락, 3)반대 시나리오, 4)한국 시장 영향력을 포함해야 합니다.\n\n" +
    "**[포맷팅 요구사항 - 모바일/태블릿 가독성 최적화]**\n" +
    "- 태블릿이나 휴대폰의 좁은 화면에서 가독성이 좋도록 문맥에 맞춰 **적절한 단락 구분(줄바꿈)**을 자주 적용해 주세요.\n" +
    "- 핵심 개념, 용어, 주목할 지표 등은 반드시 **볼드체(**)로 표시하여 시각적 리듬을 부여해 주세요.\n" +
    "- 각 섹션 사이에는 마크다운 구분선(`---`)을 삽입하여 단락 구분을 명확히 해 주세요.\n\n" +
    "격조 있고 품격 있는 분량으로 작성해 주세요. 최종 요약으로 아시아 마켓 뷰와 투자 포인트 3가지 대응 전략을 포함하여 작성하고 멈춰주세요.";

  var content = callGeminiApi(prompt);
  if (!content) {
    logMessage("❌ 주중 데일리 경제 뉴스 생성 실패");
    return;
  }
  
  var fileName = dateStr + "_Macro_Briefing.txt";
  
  try {
    var folder = DriveApp.getFolderById(TARGET_FOLDER_ID);
    var file = folder.createFile(fileName, content, MimeType.PLAIN_TEXT);
    var fileUrl = file.getUrl(); // 문서 바로가기 링크 생성
    logMessage("주중 데일리 경제 뉴스 파일 구글 드라이브 저장 성공: " + fileName);
    sendTelegramAlert(fileName, fileUrl);
  } catch(e) {
    logMessage("파일 저장 또는 알림 발송 중 에러: " + e.toString());
  }
}

// 기존 트리거 호환용 래퍼 함수 (구글 앱스 스크립트 트리거가 runDailyNewsAutomation을 호출할 때 대응)
function runDailyNewsAutomation() {
  runWeekdayDailyNews();
}

