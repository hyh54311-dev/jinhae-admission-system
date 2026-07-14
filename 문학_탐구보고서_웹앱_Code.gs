/**
 * 진해고등학교 2학년 문학 교과 심층 탐구 보고서 제출 시스템 - 백엔드 (GAS)
 * * 제작: Antigravity
 * 
 * 주요 기능:
 * 1. 학생 제출 및 피드백 화면 서비스 (doGet)
 * 2. 명렬 시트(Sheet1)에서 학급별 번호/이름 명단 로드 (getRoster)
 * 3. 학생 데이터 수집 및 '탐구보고서_응답' 시트 누적 기록 (submitReport)
 * 4. 제출 시 구글 드라이브 내 지정 폴더 자동 생성 및 템플릿 없이 '학생 맞춤형 심층 보고서 구글 문서' 자동 생성
 * 5. 학생이 제출 전에 작성 내용을 바탕으로 실시간 AI 첨삭 및 보완 조언을 받을 수 있는 Gemini 피드백 연동 (getAiFeedback)
 */

const CONFIG = {
  RESPONSE_SHEET_NAME: "탐구보고서_응답",
  ROSTER_SHEET_NAME: "Sheet1",                  // 학급별 학생 명렬 탭 이름
  FOLDER_NAME: "진해고 문학 탐구보고서 제출함", // 구글 드라이브에 자동 생성될 폴더 이름
  MODEL_NAME: "gemini-2.5-flash"              // 실시간 AI 피드백을 지원할 초고속 경량 모델
};

/**
 * 웹앱 배포 시 브라우저 접속을 처리하여 UI 화면을 출력합니다.
 */
function doGet() {
  return HtmlService.createTemplateFromFile('Index')
      .evaluate()
      .setTitle('진해고등학교 문학 심층 탐구 보고서 제출 시스템')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * 스프레드시트 메뉴에 '문학 탐구 보고서 설정'을 추가합니다.
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('📂 문학 탐구보고서 설정')
    .addItem('🔑 Gemini API 키 설정', 'promptApiKey')
    .addItem('📁 제출함 폴더 미리 생성', 'prepareSubmissionFolder')
    .addToUi();
}

/**
 * 사용자에게 Gemini API 키를 받아 안전하게 저장합니다.
 */
function promptApiKey() {
  var ui = SpreadsheetApp.getUi();
  var response = ui.prompt('Gemini API 키 입력', 'Google AI Studio에서 발급받은 API 키를 입력해 주세요:', ui.ButtonSet.OK_CANCEL);
  if (response.getSelectedButton() == ui.Button.OK) {
    var apiKey = response.getResponseText().trim();
    if (apiKey) {
      PropertiesService.getScriptProperties().setProperty('GEMINI_API_KEY', apiKey);
      ui.alert('설정 완료', 'Gemini API 키가 저장되었습니다.', ui.ButtonSet.OK);
    } else {
      ui.alert('경고', '올바른 API 키를 입력해 주세요.', ui.ButtonSet.OK);
    }
  }
}

/**
 * 구글 드라이브에 보고서 저장용 폴더를 조회하거나 새로 생성하여 폴더 ID를 반환합니다.
 */
function prepareSubmissionFolder() {
  // 진해고등학교/2026학년도/수업/2026학년도 세특/2학년 문학 폴더 ID
  var folderId = "10-JmLFHo0Rh2aFxHCCeFoalEalgtt0D2"; 
  try {
    var folder = DriveApp.getFolderById(folderId);
    return folderId;
  } catch (e) {
    var folders = DriveApp.getFoldersByName(CONFIG.FOLDER_NAME);
    if (folders.hasNext()) {
      return folders.next().getId();
    } else {
      return DriveApp.createFolder(CONFIG.FOLDER_NAME).getId();
    }
  }
}

/**
 * 'Sheet1' 시트에서 가로로 배치된 반별 명단(1열: 1반 번호, 2열: 1반 이름, 3열: 2반 번호, 4열: 2반 이름... )을 로드합니다.
 */
function getRoster() {
  try {
    var ss;
    try {
      // 지정해주신 2학년 명렬 스프레드시트(ID: 1KgpBoxrQUwiqA86qJr9eB6KAckSNfuC7QJea-m7qiSg)를 직접 열어 로드합니다.
      ss = SpreadsheetApp.openById("1KgpBoxrQUwiqA86qJr9eB6KAckSNfuC7QJea-m7qiSg");
    } catch(e) {
      // 권한 등의 이유로 외부 시트 호출이 어려울 경우, 웹앱 바인딩 시트에서 탐색합니다.
      ss = SpreadsheetApp.getActiveSpreadsheet();
    }
    var sheet = ss.getSheetByName(CONFIG.ROSTER_SHEET_NAME);
    if (!sheet) {
      return { success: false, error: `'${CONFIG.ROSTER_SHEET_NAME}' 명렬 시트를 찾을 수 없습니다.` };
    }
    
    var lastRow = sheet.getLastRow();
    if (lastRow < 2) {
      return { success: true, roster: {} };
    }
    
    // 최대 10개 반(20개 열)의 데이터를 가져옵니다.
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
    
    // 번호 순 정렬
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
 * 학생이 실시간 피드백을 요청할 때 Gemini 2.5 Flash API를 연동하여 첨삭 조언을 제공합니다.
 */
function getAiFeedback(formData) {
  var apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
  if (!apiKey) {
    return { success: false, error: "교사용 메뉴에서 Gemini API 키를 먼저 설정해야 피드백을 이용할 수 있습니다." };
  }

  var prompt = `
당신은 고등학교 국어 교사이자 입시 상담을 담당하는 문학 교과 심층 탐구 보고서 피드백 전문가입니다.
학생이 작성 중인 내용을 분석하여, '자기주도성', '비판적 사고력', '진로와의 연계 깊이'를 극대화할 수 있도록 친근하고 상세한 피드백을 주십시오.

[학생 작성 내용]
- 희망 진로: ${formData.career}
- 대상 작품: ${formData.work}
- 탐구 주제: ${formData.title}
- 1. 탐구 동기: ${formData.motivation}
- 2-1. 작품 속 탐구 장면/시어 분석: ${formData.content_literary}
- 2-2. 진로 학문 및 사회 연계 분석: ${formData.content_fusion}
- 3. 탐구 과정 및 심화 노력: ${formData.process}
- 4. 결론 및 성장: ${formData.conclusion}

[피드백 가이드라인]
1. 친근하고 따뜻한 국어 선생님 어조로 작성해 주세요. (예: "~구나!", "~해보면 어떨까?")
2. 학생의 진로(${formData.career})와 선택 문학 작품(${formData.work})의 융합도가 매끄러운지 평가해 주세요.
3. 특히 '탐구 과정 및 심화 노력' 부분에서 단순 네이버 검색에 머무르지 않고, 전문 학술 자료(RISS 논문 등)나 심도 있는 관련 도서 분석을 추가하도록 구체적인 학술적 키워드나 도서 추천을 포함해 주세요.
4. 부족한 점을 지적하되, 스스로 글을 채워갈 수 있도록 유도 질문(발문)을 1~2개 던져주세요.
5. 마크다운과 이모티콘을 활용해 가독성 있게 서술해 주세요.

출력:`;

  var url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.MODEL_NAME}:generateContent?key=${apiKey}`;
  var payload = {
    "contents": [{ "parts": [{ "text": prompt }] }],
    "generationConfig": { "temperature": 0.6 }
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
    if (json.candidates && json.candidates[0].content && json.candidates[0].content.parts[0].text) {
      return { success: true, feedback: json.candidates[0].content.parts[0].text.trim() };
    }
    return { success: false, error: "AI 피드백 결과를 생성하지 못했습니다." };
  } catch (e) {
    return { success: false, error: e.toString() };
  }
}

/**
 * 학생이 제출한 보고서 폼 데이터를 시트에 기록하고 구글 드라이브에 보고서 구글 문서를 프로그램적으로 자동 빌드합니다.
 */
function submitReport(formData) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000);
  } catch (e) {
    return { success: false, error: "서버 동시 트래픽이 많아 제출이 지연되었습니다. 다시 제출 버튼을 눌러주세요." };
  }

  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.RESPONSE_SHEET_NAME);
    
    var headers = [
      "제출일시", "학년", "반", "번호", "이름", "희망 진로", "대상 작품", 
      "탐구 주제", "탐구 동기", "2-1. 작품 분석", "2-2. 진로/사회 연계", "탐구 과정", "결론 및 성장", 
      "구글 문서 링크", "세특 초안 (AI)", "바이트 수", "처리 상태"
    ];

    if (!sheet) {
      sheet = ss.insertSheet(CONFIG.RESPONSE_SHEET_NAME);
      sheet.appendRow(headers);
      sheet.getRange("A1:Q1").setFontWeight("bold").setBackground("#e2e8f0").setHorizontalAlignment("center");
    }

    var timestamp = new Date();
    var grade = parseInt(formData.grade) || 2;
    var ban = parseInt(formData.ban);
    var num = parseInt(formData.num);
    var name = formData.name.trim();
    var career = formData.career.trim();
    var work = formData.work.trim();
    var title = formData.title.trim();
    var motivation = formData.motivation.trim();
    var content_literary = formData.content_literary.trim();
    var content_fusion = formData.content_fusion.trim();
    var process = formData.process.trim();
    var conclusion = formData.conclusion.trim();

    // 빈 입력값 유효성 검사
    if (!ban || !num || !name || !career || !work || !title || !motivation || !content_literary || !content_fusion || !process || !conclusion) {
      return { success: false, error: "모든 항목을 입력해 주세요." };
    }

    // [오류 수정] 세특 작성을 위한 실제 작성 텍스트 길이 합산 로직 추가 (공백 포함 글자수)
    var totalTextLength = motivation.length + content_literary.length + content_fusion.length + process.length + conclusion.length;

    var folderId = prepareSubmissionFolder();
    var docUrl = "";
    var downloadUrl = "";

    if (formData.fileData && formData.fileName) {
      // 파일 업로드 방식 처리
      var decodedFile = Utilities.base64Decode(formData.fileData);
      var blob = Utilities.newBlob(decodedFile, getMimeType(formData.fileName), formData.fileName);
      
      var folder = DriveApp.getFolderById(folderId);
      var ext = formData.fileName.split('.').pop();
      var newFileName = "[문학 보고서제출] " + ban + "반_" + num + "번_" + name + "_" + title + "." + ext;
      blob.setName(newFileName);
      
      var uploadedFile = folder.createFile(blob);
      uploadedFile.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      docUrl = uploadedFile.getUrl();
      downloadUrl = docUrl; 
    } else {
      // 직접 입력 방식 처리
      var docResult = createProgrammaticReportDoc(folderId, formData);
      docUrl = docResult.url;
      downloadUrl = docResult.downloadUrl;
    }

    // 동일 학생 검사
    var lastRow = sheet.getLastRow();
    var existingRowIdx = -1;
    if (lastRow > 1) {
      var data = sheet.getRange(2, 2, lastRow - 1, 4).getValues(); 
      for (var i = 0; i < data.length; i++) {
        if (parseInt(data[i][0]) === grade && parseInt(data[i][1]) === ban && parseInt(data[i][2]) === num && data[i][3].toString().trim() === name) {
          existingRowIdx = i + 2; 
          break;
        }
      }
    }

    if (existingRowIdx > -1) {
      // [오류 수정] 15~17열 업데이트 시 totalTextLength(바이트 수/글자 수) 기록 반영
      sheet.getRange(existingRowIdx, 1).setValue(timestamp);
      sheet.getRange(existingRowIdx, 6, 1, 9).setValues([[
        career, work, title, motivation, content_literary, content_fusion, process, conclusion, docUrl
      ]]);
      sheet.getRange(existingRowIdx, 15, 1, 3).setValues([["", totalTextLength, "대기"]]);
    } else {
      // [오류 수정] 신규 등록 시에도 totalTextLength 반영
      sheet.appendRow([
        timestamp, grade, ban, num, name, career, work, 
        title, motivation, content_literary, content_fusion, process, conclusion, 
        docUrl, "", totalTextLength, "대기"
      ]);
    }

    var updatedLastRow = sheet.getLastRow();
    if (updatedLastRow > 1) {
      var dataRange = sheet.getRange(2, 1, updatedLastRow - 1, 17);
      dataRange.sort([{column: 2, ascending: true}, {column: 3, ascending: true}, {column: 4, ascending: true}]);
    }

    return { success: true, docUrl: docUrl, downloadUrl: downloadUrl, name: name, isFile: !!(formData.fileData) };
  } catch (e) {
    return { success: false, error: e.toString() };
  } finally {
    lock.releaseLock();
  }
}

/**
 * 템플릿 문서 없이 완전 프로그램적으로 멋진 구글 문서를 드라이브에 빌드합니다.
 */
function createProgrammaticReportDoc(folderId, data) {
  var folder = DriveApp.getFolderById(folderId);
  var fileName = `[문학 심층보고서] ${data.ban}반_${data.num}번_${data.name}`;
  
  // 구글 문서 신규 생성
  var doc = DocumentApp.create(fileName);
  var docId = doc.getId();
  var body = doc.getBody();

  // 여백 설정
  body.setMarginTop(72);    // 1인치
  body.setMarginBottom(72);
  body.setMarginLeft(72);
  body.setMarginRight(72);

  // 1. 대제목 스타일링
  var title = body.appendParagraph("문학 교과 심층 탐구 보고서");
  title.setHeading(DocumentApp.ParagraphHeading.TITLE);
  title.setFontFamily("Malgun Gothic");
  title.setFontSize(26);
  title.setBold(true);
  title.setForegroundColor("#1e3a8a");
  title.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
  body.appendParagraph("").setSpacingAfter(15);

  // 2. 학생 정보 표 스타일링
  var tableData = [
    ["구분", "학년", "반", "번호", "이름", "희망 진로"],
    ["학생 정보", data.grade + "학년", data.ban + "반", data.num + "번", data.name, data.career]
  ];
  var table = body.appendTable(tableData);
  table.setBorderWidth(1);
  table.setBorderColor("#cbd5e1");
  
  for (var r = 0; r < 2; r++) {
    var row = table.getRow(r);
    for (var c = 0; c < 6; c++) {
      var cell = row.getCell(c);
      cell.setFontFamily("Malgun Gothic");
      cell.setFontSize(10);
      cell.setVerticalAlignment(DocumentApp.VerticalAlignment.CENTER);
      
      if (r === 0) {
        cell.setBackgroundColor("#f1f5f9");
        cell.getChild(0).asParagraph().setBold(true);
        cell.getChild(0).asParagraph().setAlignment(DocumentApp.HorizontalAlignment.CENTER);
      } else {
        cell.getChild(0).asParagraph().setAlignment(DocumentApp.HorizontalAlignment.CENTER);
      }
    }
  }
  body.appendParagraph("").setSpacingAfter(20);

  // 3. 서술부 레이아웃 추가
  appendSection(body, "■ 탐구 주제", data.title, true);
  appendSection(body, "■ 대상 작품 및 저자", data.work, false);
  appendSection(body, "1. 탐구 동기 (수업 연계성)", data.motivation, false);
  appendSection(body, "2-1. 작품 속 탐구 장면/시어의 문학적 분석", data.content_literary, false);
  appendSection(body, "2-2. 희망 진로 학문 및 현대 사회 사례 연계 분석", data.content_fusion, false);
  appendSection(body, "3. 탐구 과정 및 심화 노력 (도서/논문 등 독서 성과)", data.process, false);
  appendSection(body, "4. 결론 및 느낀 점 (인식의 변화와 학업적 성장)", data.conclusion, false);

  // 문서 저장 및 닫기
  doc.saveAndClose();

  // [오류 수정] 구글 드라이브 최신 API를 사용한 단일 폴더 이동 처리
  var file = DriveApp.getFileById(docId);
  file.moveTo(folder); 

  // 공유 권한 설정
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);

  var viewUrl = file.getUrl();
  var dlUrl = viewUrl.replace("/edit", "/export?format=docx");

  return { url: viewUrl, downloadUrl: dlUrl };
}

/**
 * 보고서 문서 내부의 서술용 섹션 구조를 일관적으로 추가해 주는 헬퍼 함수입니다.
 */
function appendSection(body, headerText, contentText, isMainTitle) {
  var heading = body.appendParagraph(headerText);
  heading.setFontFamily("Malgun Gothic");
  heading.setBold(true);
  heading.setLineSpacing(1.15);
  
  if (isMainTitle) {
    heading.setFontSize(14);
    heading.setForegroundColor("#1e3a8a");
    heading.setSpacingBefore(12);
  } else {
    heading.setFontSize(12);
    heading.setForegroundColor("#334155");
    heading.setSpacingBefore(16);
  }
  
  var content = body.appendParagraph(contentText);
  content.setFontFamily("Malgun Gothic");
  content.setFontSize(11);
  content.setForegroundColor("#0f172a");
  content.setLineSpacing(1.3);
  content.setSpacingAfter(10);
  content.setSpacingBefore(4);
}

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

/**
 * 파일 확장자로부터 MIME 타입을 반환하는 헬퍼 함수입니다.
 */
function getMimeType(fileName) {
  var ext = fileName.split('.').pop().toLowerCase();
  var mimeTypes = {
    'pdf': 'application/pdf',
    'hwp': 'application/x-hwp',
    'hwpx': 'application/x-hwpx',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'doc': 'application/msword'
  };
  return mimeTypes[ext] || 'application/octet-stream';
}
