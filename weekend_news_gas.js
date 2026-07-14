// weekend_news_gas.gs
// 컴퓨터가 꺼져 있어도 구글 클라우드에서 주말마다 자동 실행되는 구글 앱스스크립트(Google Apps Script) 코드입니다.
// 리포트를 단순 텍스트가 아닌 세련된 '구글 문서(Google Docs)' 형식으로 생성하고, 세리프체(Georgia)와 양쪽 정렬, 들여쓰기 인용구 등 실제 단행본 책과 같은 고급 서식을 적용하여 저장합니다.
// Apps Script (https://script.google.com)의 주말 뉴스 프로젝트에 아래 코드를 붙여넣으세요.

// ----------------- 사용자 설정 ----------------- //
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
  var fullMessage = "[" + timestamp + "] [WeekendNews] " + message;
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

function sendTelegramAlert(fileName, isSunday, summary, fileUrl) {
  var prefix = isSunday ? "일요일 철학/인물산책" : "토요일 미래/친환경 기술";
  var summarySection = summary ? "\n\n💡 <b>핵심 요약 (5줄 이내):</b>\n" + summary : "";
  
  // HTML 태그를 활용한 하이퍼링크 메시지 포맷 구성
  var text = "📝 <b>[" + prefix + " 생성 완료]</b>\n\n" +
             "오늘의 리포트(<code>" + fileName + "</code>)가 구글 문서로 저장되었습니다." + 
             summarySection + "\n\n" +
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

// 구글 드라이브 폴더에서 과거에 작성했던 미래 기술 구글 문서들을 열어 제목 목록 추출
function getPastFutureTechTopics(folderId) {
  try {
    var folder = DriveApp.getFolderById(folderId);
    var files = folder.getFiles();
    var topics = [];
    var count = 0;
    
    while (files.hasNext() && count < 20) {
      var file = files.next();
      var name = file.getName();
      // 휴지통에 가지 않은 활성 파일만 스캔 대상으로 삼아 정확도 향상
      if (name.indexOf("Future_Tech_Report") !== -1 && !file.isTrashed()) {
        var title = "";
        try {
          // 구글 문서를 직접 열어 제목 파싱
          var doc = DocumentApp.openById(file.getId());
          var content = doc.getBody().getText();
          var lines = content.split("\n");
          for (var i = 0; i < Math.min(lines.length, 15); i++) {
            var line = lines[i].trim();
            if (line !== "") {
              title = line; // 마크다운 기호가 파싱 시 지워졌으므로 첫 번째 줄글이 곧 제목입니다.
              break;
            }
          }
        } catch(docErr) {
          title = name;
        }
        if (!title) {
          title = name;
        }
        topics.push("- " + title + " (생성일자: " + name.substring(0, 8) + ")");
        count++;
      }
    }
    return topics.length > 0 ? topics.join("\n") : "이전 기술 분석 기록이 없습니다.";
  } catch(e) {
    return "드라이브 조회 실패: " + e.toString();
  }
}

// 2026년 1월 기준 5개월 단위 순환 루프 연산
function getSundayEra() {
  var now = new Date();
  var year = now.getFullYear();
  var month = now.getMonth(); // 0 = 1월, 11 = 12월
  
  var monthsSinceStart = (year - 2026) * 12 + month;
  var cycleIndex = monthsSinceStart % 5;
  
  var eras = {
    0: { name: "고대 철학", desc: "그리스 철학의 탄생부터 헬레니즘 시대까지 (소크라테스, 플라톤, 아리스토텔레스, 스토아 학파, 에피쿠로스 등)" },
    1: { name: "고대에 가까운 중세 철학", desc: "로마 말기 교부 철학부터 초기 이슬람 철학의 황금기까지 (아우구스티누스, 보에티우스, 이븐 시나, 가잘리 등)" },
    2: { name: "중세 신학 및 철학", desc: "스콜라 철학의 융성 및 중세 후기 신학적 논쟁 (토마스 아퀴나스, 안셀무스, 윌리엄 오브 오컴 등)" },
    3: { name: "근대 철학", desc: "르네상스, 대륙 합리론, 영미 경험론 및 계몽주의 시대 (마키아벨리, 데카르트, 스피노자, 로크, 흄, 칸트 등)" },
    4: { name: "현대 철학 및 인지과학", desc: "19세기 실존주의, 실용주의, 현상학, 분석철학 및 행동경제학 (니체, 하이데거, 사르트르, 비트겐슈타인, 대니얼 카너먼 등)" }
  };
  return eras[cycleIndex];
}

// 마크다운 형태의 텍스트를 한 권의 책(E-Book)처럼 세련된 레이아웃의 구글 문서로 저장하는 변환기
function createFormattedDoc(folderId, fileName, markdownText) {
  var doc = DocumentApp.create(fileName);
  var file = DriveApp.getFileById(doc.getId());
  var folder = DriveApp.getFolderById(folderId);
  
  // 루트 폴더에서 대상 폴더로 깔끔하고 안전하게 이동 (현대적인 moveTo API 사용)
  file.moveTo(folder);
  
  var body = doc.getBody();
  body.clear();
  
  // 책과 같은 여백 설정 (상하좌우 1인치 = 72pt)
  body.setMarginTop(72);
  body.setMarginBottom(72);
  body.setMarginLeft(72);
  body.setMarginRight(72);
  
  var lines = markdownText.split("\n");
  var inQuote = false;
  var quoteText = [];
  
  // 세련된 서체 및 색상 테마 정의
  var FONT_FAMILY = "Georgia"; // 이북 감성의 세리프 서체
  var COLOR_TITLE = "#1A1A1A"; // 대제목용 깊은 블랙
  var COLOR_HEADING = "#1D3557"; // 챕터 제목용 세련된 네이비
  var COLOR_BODY = "#2F3E46"; // 가독성이 높은 본문용 부드러운 다크그레이
  var COLOR_QUOTE = "#4F5D75"; // 인용 블록용 뮤티드블루
  
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    
    // 구분선 (---) 처리
    if (line === "---") {
      if (inQuote) {
        flushQuote(body, quoteText, FONT_FAMILY, COLOR_QUOTE);
        quoteText = [];
        inQuote = false;
      }
      body.appendParagraph("").setSpacingBefore(12).setSpacingAfter(12);
      body.appendHorizontalRule();
      continue;
    }
    
    // 빈 줄 처리
    if (line === "") {
      if (inQuote) {
        flushQuote(body, quoteText, FONT_FAMILY, COLOR_QUOTE);
        quoteText = [];
        inQuote = false;
      }
      body.appendParagraph("").setSpacingAfter(6);
      continue;
    }
    
    // 인용구 (>) 감지 및 버퍼링
    if (line.indexOf(">") === 0) {
      inQuote = true;
      quoteText.push(line.substring(1).trim());
      continue;
    } else if (inQuote) {
      flushQuote(body, quoteText, FONT_FAMILY, COLOR_QUOTE);
      quoteText = [];
      inQuote = false;
    }
    
    // 마크다운 대제목 (# ) 처리
    if (line.indexOf("# ") === 0) {
      var titleText = line.substring(2).trim();
      var p = body.appendParagraph(titleText);
      p.setHeading(DocumentApp.ParagraphHeading.TITLE);
      p.setFontFamily(FONT_FAMILY);
      p.setFontSize(22);
      p.setBold(true);
      p.setForegroundColor(COLOR_TITLE);
      p.setAlignment(DocumentApp.HorizontalAlignment.CENTER); // 가운데 정렬
      p.setSpacingBefore(24);
      p.setSpacingAfter(20);
      continue;
    }
    
    // 마크다운 소제목/챕터 제목 (## 또는 ###) 처리
    if (line.indexOf("## ") === 0 || line.indexOf("### ") === 0) {
      var headingText = line.replace(/^#+\s+/, "").trim();
      var p = body.appendParagraph(headingText);
      p.setHeading(DocumentApp.ParagraphHeading.HEADING1);
      p.setFontFamily(FONT_FAMILY);
      p.setFontSize(14);
      p.setBold(true);
      p.setForegroundColor(COLOR_HEADING);
      p.setAlignment(DocumentApp.HorizontalAlignment.LEFT);
      p.setSpacingBefore(22);
      p.setSpacingAfter(12);
      continue;
    }
    
    // 일반 본문 줄글 처리
    var p = body.appendParagraph(line);
    p.setFontFamily(FONT_FAMILY);
    p.setFontSize(11);
    p.setForegroundColor(COLOR_BODY);
    p.setLineSpacing(1.55); // 단행본 수준의 편안한 행간
    p.setAlignment(DocumentApp.HorizontalAlignment.JUSTIFY); // 양쪽 정렬로 완벽한 조판 형태 구현
    p.setSpacingAfter(12);
    
    // 인라인 볼드체 (**) 처리
    applyInlineFormatting(p);
  }
  
  // 스크립트 종료 전 잔여 인용 블록 렌더링
  if (inQuote && quoteText.length > 0) {
    flushQuote(body, quoteText, FONT_FAMILY, COLOR_QUOTE);
  }
  
  doc.saveAndClose();
  return file;
}

// 인용 블록 렌더링 함수
function flushQuote(body, quoteLines, font, color) {
  var fullQuoteText = quoteLines.join("\n");
  var p = body.appendParagraph(fullQuoteText);
  p.setFontFamily(font);
  p.setFontSize(10.5);
  p.setForegroundColor(color);
  p.setItalic(true); // 이북 정석인 이탤릭체 적용
  p.setIndentStart(36); // 좌우 여백을 두어 본문과 차별화 (V8 규격)
  p.setIndentEnd(36);
  p.setSpacingBefore(12);
  p.setSpacingAfter(12);
  p.setLineSpacing(1.4);
  p.setAlignment(DocumentApp.HorizontalAlignment.JUSTIFY);
  
  applyInlineFormatting(p);
}

// 문단 내부의 **텍스트** 패턴을 찾아 굵게 스타일링하고 별표 기호는 삭제하는 파서
function applyInlineFormatting(paragraph) {
  var text = paragraph.getText();
  var boldPattern = /\*\*(.*?)\*\*/g;
  var match;
  var textObj = paragraph.editAsText();
  var boldRanges = [];
  
  while ((match = boldPattern.exec(text)) !== null) {
    var rawStart = match.index;
    var cleanStart = rawStart - (boldRanges.length * 4); // 앞서 제거된 **(4글자) 누적 보정
    var cleanLength = match[1].length;
    
    boldRanges.push({
      start: cleanStart,
      end: cleanStart + cleanLength - 1
    });
  }
  
  var finalCleanText = text.replace(/\*\*/g, "");
  if (finalCleanText !== text) {
    textObj.setText(finalCleanText);
    for (var i = 0; i < boldRanges.length; i++) {
      var r = boldRanges[i];
      if (r.start >= 0 && r.end < finalCleanText.length) {
        textObj.setBold(r.start, r.end, true);
      }
    }
  }
}

// ========================================================================= //
// ★ [토요일 실행 함수] 미래 & 친환경 유망 기술 리포트 생성
// 트리거 스케줄러 설정: [매주 토요일 오전 8시 ~ 9시 사이 실행]으로 지정하세요.
// ========================================================================= //
function runSaturdayFutureTech() {
  logMessage("🚀 Saturday Future Tech Report 생성 파이프라인 작동...");
  
  var now = new Date();
  var dateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), "yyyyMMdd");
  var dateFullStr = Utilities.formatDate(now, Session.getScriptTimeZone(), "yyyy년 MM월 dd일");
  
  var pastHistory = getPastFutureTechTopics(TARGET_FOLDER_ID);
  
  var prompt = 
    "당신은 글로벌 벤처캐피털(VC)의 시니어 기술 파트너이자 친환경 미래 기술 학술 분석가입니다. 현재 실제 날짜는 " + dateFullStr + "입니다.\n" +
    "아래는 기존에 이미 분석 보고서를 작성한 기술 목록입니다. 중복을 방지하기 위해 이 목록에 명시된 기술은 제외해 주세요.\n" +
    "--- 이미 다룬 기술 및 산업 역사 ---\n" + pastHistory + "\n--------------------\n\n" +
    "Google Search를 사용하여, 현재 글로벌 친환경 기술, 미래 혁신 기술, 또는 신성장 동력 분야 중 **최근 1-2주 사이에 가장 의미 있는 성과나 변화가 있었고 중요도가 높은 기술 분야**를 하나만 엄선해 주세요.\n" +
    "단, 과거에 다룬 주제라 할지라도 최근 1주일 이내에 세상을 바꿀 만한 획기적인 기술적 돌파구(Breakthrough)가 발표된 경우에 한해 예외적으로 중복 선정이 가능하며, 이 경우 무엇이 달라졌는지 명확히 설명해야 합니다.\n\n" +
    "**[요약 및 본문 구분 규칙 - 필수]**\n" +
    "반드시 응답의 맨 처음에 아래와 같이 `[요약]`과 `[본문]` 태그를 사용하여 요약과 본문을 명확히 구분해 주세요:\n" +
    "[요약]\n" +
    "- 5줄 이내로 이 리포트의 핵심 개념과 중요 인사이트를 개조식으로 요약해 주세요 (각 줄 끝에 줄바꿈 필수).\n" +
    "[본문]\n" +
    "(여기에 에세이 본문을 작성해 주세요. 아래 서식 규칙 준수)\n\n" +
    "**[E-Book 서식 및 태블릿 가독성 최적화 요구사항]**\n" +
    "- 본 텍스트는 건조한 '비즈니스 보고서'가 아닌, **한 권의 인문/과학 단행본(E-Book)이나 품격 있는 기술 에세이**처럼 서사적이고 유려한 문체로 작성해 주세요.\n" +
    "- **분량 극대화**: 본문은 **최소 4,000자 이상(공백 제외)**의 충분한 분량으로 상세히 기술하여 깊은 읽을거리를 제공해야 합니다. 얕은 단편 요약을 철저히 배제하고, 한 장의 밀도가 매우 높아야 합니다.\n" +
    "- 딱딱하게 숫자가 매겨진 제목(예: '1. 기술 작동 원리') 대신, 소설이나 과학책의 챕터처럼 **서사적이고 흥미를 유발하는 제목**을 사용해 주세요. (예: '제1장: 분자의 노래 - 작동과 흐름의 원리' 등)\n" +
    "- 항목을 단순히 나열하는 개조식 리스트(번호나 점 기호)는 되도록 지양하고, **부드럽게 연결되는 산문(줄글) 형식**을 사용하여 호흡이 끊기지 않고 책을 읽듯 읽어내려갈 수 있도록 해 주세요.\n" +
    "- 좁은 모바일 기기 화면에서도 눈이 편하도록 문단 구분을 명확히 하고 **주요 용어나 수치는 볼드체(**)로 표기해 주세요.\n" +
    "- 각 챕터 사이에는 마크다운 구분선(`---`)을 넣어 지면을 아름답게 구분해 주세요.\n\n" +
    "에세이는 대학 수준의 깊이를 갖추어 마크다운 형식으로 작성해 주시고, 아래 맥락을 담은 4개의 장으로 구성해 주세요. 각 장(Chapter)은 최소 1,000자 이상의 충분한 산문으로 자세히 상술되어야 합니다:\n" +
    "- **제1장 (기술의 핵심 원리와 정의)**\n" +
    "- **제2장 (글로벌 연구 및 상용화의 최전선)** (선도 기업, 연구소, 핵심 수치 데이터 포함)\n" +
    "- **제3장 (친환경적 가치와 인류에 미칠 파급력)**\n" +
    "- **제4장 (남겨진 기술적 난제와 미래의 지도)**";

  var content = callGeminiApi(prompt);
  if (!content) {
    logMessage("❌ 토요일 미래 기술 리포트 생성 실패");
    return;
  }
  
  var summary = "";
  var bodyText = content;
  
  var summaryIdx = content.indexOf("[요약]");
  var bodyIdx = content.indexOf("[본문]");
  if (summaryIdx !== -1 && bodyIdx !== -1) {
    summary = content.substring(summaryIdx + 4, bodyIdx).trim();
    bodyText = content.substring(bodyIdx + 4).trim();
  }
  
  var fileName = dateStr + "_Future_Tech_Report";
  
  try {
    // 텍스트 파일이 아닌 이북 서식이 가미된 구글 문서 형태로 저장
    var file = createFormattedDoc(TARGET_FOLDER_ID, fileName, bodyText);
    var fileUrl = file.getUrl(); 
    logMessage("토요일 미래 기술 파일 구글 문서 저장 성공: " + fileName);
    sendTelegramAlert(fileName, false, summary, fileUrl);
  } catch(e) {
    logMessage("파일 저장 또는 알림 발송 중 에러: " + e.toString());
  }
}

// ========================================================================= //
// ★ [일요일 실행 함수] 대학 전공 수준 철학 & 사상 리포트 생성
// 트리거 스케줄러 설정: [매주 일요일 오전 8시 ~ 9시 사이 실행]으로 지정하세요.
// ========================================================================= //
function runSundayPhilosophy() {
  logMessage("🚀 Sunday Philosophy Report 생성 파이프라인 작동...");
  
  var now = new Date();
  var dateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), "yyyyMMdd");
  var dateFullStr = Utilities.formatDate(now, Session.getScriptTimeZone(), "yyyy년 MM월 dd일");
  
  var era = getSundayEra();
  logMessage("금월 선정 시대: " + era.name + " (" + era.desc + ")");
  
  var prompt = 
    "당신은 인문학, 철학, 그리고 역사적 사상의 계보에 정통한 석학 교수입니다. 현재 실제 날짜는 " + dateFullStr + "입니다.\n" +
    "이번 달의 탐구 영역은 **'[" + era.name + "]'** (" + era.desc + ") 입니다.\n\n" +
    "이 영역 내에서 가장 논쟁적이고 사상사적 깊이가 깊은 **핵심 사상가 1명과 그의 핵심 개념/논쟁**을 엄선하여 깊이 있게 다뤄 주세요.\n" +
    "**[요구사항]**:\n" +
    "1. **학술적 수준**: 대략 대학 학부생(Undergraduate) 이상의 전공 수준으로 작성해 주세요. 단순 인물 소개나 넓고 얕을 요약은 피하고, 사상의 논리적 구조, 텍스트(원전)의 구절, 사상사적 계보 및 한계점을 깊이 있게 헤집어야 합니다.\n" +
    "2. **친근한 비유**: 글의 논조는 격조 높고 학구적이어야 하지만, 어려운 전문 용어가 처음 등장할 때는 고등학생이나 일반인이 직관적으로 이해할 수 있도록 명료한 일상적 비유나 사고 실험을 하나씩 곁들여 주세요.\n" +
    "3. **요약 및 본문 구분 규칙 - 필수**:\n" +
    "   반드시 응답의 맨 처음에 아래와 같이 `[요약]`과 `[본문]` 태그를 사용하여 요약과 본문을 명확히 구분해 주세요:\n" +
    "   [요약]\n" +
    "   - 5줄 이내로 이 리포트의 핵심 개념과 중요 인사이트를 개조식으로 요약해 주세요 (각 줄 끝에 줄바꿈 필수).\n" +
    "   [본문]\n" +
    "   (여기에 에세이 본문을 작성해 주세요. 아래 서식 규칙 준수)\n\n" +
    "4. **E-Book 서식 및 태블릿 가독성 최적화 요구사항**:\n" +
    "   - 본 텍스트는 건조한 '비즈니스 보고서'가 아닌, **한 권의 인문/철학 단행본(E-Book)이나 품격 있는 에세이**처럼 서사적이고 유려한 문체로 작성해 주세요.\n" +
    "   - **분량 극대화**: 본문은 **최소 4,000자 이상(공백 제외)**의 충분한 분량으로 상세히 기술하여 깊은 읽을거리를 제공해야 합니다. 얕은 단편 요약을 철저히 배제하고, 한 장의 밀도가 매우 높아야 합니다.\n" +
    "   - 딱딱하게 숫자가 매겨진 제목(예: '1. 사상적 맥락') 대신, 실제 철학 대중서의 챕터처럼 **서사적이고 영감을 주는 제목**을 사용해 주세요. (예: '제1장: 존재의 심연을 들여다보다' 등)\n" +
    "   - 리스트(번호나 점 기호)를 남발하지 말고, **부드럽고 긴밀하게 흐르는 줄글(산문) 형식**을 위주로 작성하여 책의 흐름을 즐길 수 있게 해 주세요. 중요한 철학 원전 인용은 마크다운 인용 블록(`>`)을 적극 활용해 주세요.\n" +
    "   - 좁은 화면에서도 눈이 편하도록 단락 구분을 명확히 하고, 핵심 원어(개념)는 **볼드체(**)로 표기하며, 챕터 사이에는 마크다운 구분선(`---`)을 넣어 주세요.\n" +
    "5. **구조화**: 아래 맥락을 담은 4개의 장으로 구성해 주세요. 각 장(Chapter)은 최소 1,000자 이상의 충분한 산문으로 자세히 상술되어야 합니다.\n" +
    "   - **제1장 (시대의 어둠과 철학적 문제의식)**\n" +
    "   - **제2장 (개념의 지도와 핵심 논증 아키텍처)** (원어 해설 포함)\n" +
    "   - **제3장 (비판자들의 시선과 학술적 한계)**\n" +
    "   - **제4장 (21세기 문명에 던지는 시사점과 생각거리)** (마지막에는 대학 세미나 수준의 성찰용 토론 질문 3가지를 본문 속에 자연스럽게 포함)";

  var content = callGeminiApi(prompt);
  if (!content) {
    logMessage("❌ 일요일 철학 리포트 생성 실패");
    return;
  }
  
  var summary = "";
  var bodyText = content;
  
  var summaryIdx = content.indexOf("[요약]");
  var bodyIdx = content.indexOf("[본문]");
  if (summaryIdx !== -1 && bodyIdx !== -1) {
    summary = content.substring(summaryIdx + 4, bodyIdx).trim();
    bodyText = content.substring(bodyIdx + 4).trim();
  }
  
  var fileName = dateStr + "_Philosophy_Reading";
  
  try {
    // 텍스트 파일이 아닌 이북 서식이 가미된 구글 문서 형태로 저장
    var file = createFormattedDoc(TARGET_FOLDER_ID, fileName, bodyText);
    var fileUrl = file.getUrl(); 
    logMessage("일요일 철학 파일 구글 문서 저장 성공: " + fileName);
    sendTelegramAlert(fileName, true, summary, fileUrl);
  } catch(e) {
    logMessage("파일 저장 또는 알림 발송 중 에러: " + e.toString());
  }
}
