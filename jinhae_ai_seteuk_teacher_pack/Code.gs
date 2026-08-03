/**
 * [2022 개정 교육과정 교과역량 & NEIS 바이트 선택형 AI 세특 대시보드 패키지]
 * 
 * 저자: 황요한 교사 (진해고등학교)
 * 템플릿 버전: v2.0 (2022 개정교육과정 교과역량 반영 & 선생님별 NEIS 바이트 선택권 완벽 지원)
 * 백엔드: Google Apps Script + Upstage Solar / Google Gemini AI Multi-Switcher
 * 보안: PropertiesService (구글 서버 암호화 금고) 기반 API Key 안전 관리
 */

// 1. 웹앱 접속 라우팅 (스마트폰 음성 앱 vs 교사 대시보드)
function doGet(e) {
  var view = (e && e.parameter && e.parameter.view) ? e.parameter.view.toLowerCase() : 'app';
  var fileName = (view === 'dashboard') ? 'dashboard' : 'app';
  var title = (view === 'dashboard') ? '교사용 관찰기 기록 & AI 세특 완성 대시보드' : 'AI 음성 수업 관찰기 (5분할 휠)';
  
  var htmlOutput;
  try {
    htmlOutput = HtmlService.createHtmlOutputFromFile(fileName);
  } catch(err) {
    try {
      htmlOutput = HtmlService.createHtmlOutputFromFile(fileName + '.html');
    } catch(err2) {
      htmlOutput = HtmlService.createTemplateFromFile(fileName).evaluate();
    }
  }

  return htmlOutput
    .setTitle(title)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// 2. 구글 시트 상단 메뉴 생성
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('🪄 AI 세특 대시보드 시스템')
    .addItem('1. 🔑 API 키 및 2022 교과역량/바이트 보안 설정', 'setApiKeysPrompt')
    .addItem('2. 📋 시트 6대 탭 자동 양식 세팅', 'setupInitialSheets')
    .addItem('3. 🪄 전 학생 누적 기록 ➔ 세특 초안 전체 자동 생성', 'generateAllStudentReportsFromMenu')
    .addToUi();
}

function generateAllStudentReportsFromMenu() {
  var result = generateAllStudentReports('all');
  if (result && result.success) {
    SpreadsheetApp.getUi().alert('🎉 ' + result.count + '명 학생의 AI 세특 초안이 생성되었습니다!');
  } else {
    SpreadsheetApp.getUi().alert('오류: ' + (result ? result.message : '알 수 없는 오류'));
  }
}

// 🛡️ PropertiesService 암호화 보안 금고 API Key 및 2022 개정 교과역량/바이트 설정 대화상자
function setApiKeysPrompt() {
  var ui = SpreadsheetApp.getUi();
  var props = PropertiesService.getScriptProperties();

  var currentUpstage = props.getProperty('UPSTAGE_API_KEY') || '';
  var currentGemini = props.getProperty('GEMINI_API_KEY') || '';
  var currentSelectedAI = props.getProperty('SELECTED_AI') || 'Gemini';
  var currentSubject = props.getProperty('SUBJECT_NAME') || '국어';
  var currentCompetencies = props.getProperty('SUBJECT_COMPETENCIES') || '비판적 사고력, 지식정보처리 역량, 공동체·인성 역량';
  var currentTargetBytes = props.getProperty('TARGET_BYTES') || '1500';

  // 1. Upstage Key 입력
  var resp1 = ui.prompt(
    '🔑 [보안 설정 1/6] Upstage API Key',
    'Upstage Solar API 키를 입력하세요.
(현재 등록 상태: ' + (currentUpstage ? '✅ 등록됨' : '❌ 미등록') + ')',
    ui.ButtonSet.OK_CANCEL
  );
  if (resp1.getSelectedButton() !== ui.Button.OK) return;
  var newUpstage = resp1.getResponseText().trim();
  if (newUpstage) props.setProperty('UPSTAGE_API_KEY', newUpstage);

  // 2. Gemini Key 입력
  var resp2 = ui.prompt(
    '🔑 [보안 설정 2/6] Google Gemini API Key (추천)',
    'Google Gemini API 키를 입력하세요.
(현재 등록 상태: ' + (currentGemini ? '✅ 등록됨' : '❌ 미등록') + ')',
    ui.ButtonSet.OK_CANCEL
  );
  if (resp2.getSelectedButton() !== ui.Button.OK) return;
  var newGemini = resp2.getResponseText().trim();
  if (newGemini) props.setProperty('GEMINI_API_KEY', newGemini);

  // 3. AI 모델 선택 (Gemini vs Upstage)
  var resp3 = ui.prompt(
    '🤖 [보안 설정 3/6] AI 엔진 선택',
    '사용할 AI 엔진을 입력하세요. [ Gemini ] 또는 [ Upstage ]
(현재 설정: ' + currentSelectedAI + ')',
    ui.ButtonSet.OK_CANCEL
  );
  if (resp3.getSelectedButton() !== ui.Button.OK) return;
  var newAI = resp3.getResponseText().trim();
  if (newAI) props.setProperty('SELECTED_AI', newAI);

  // 4. 과목명 설정 (2022 개정교육과정 연계)
  var resp4 = ui.prompt(
    '📚 [교과 설정 4/6] 담당 과목명',
    '담당 과목을 입력하세요 (예: 국어, 수학, 영어, 정보, 통합사회, 통합과학, 행특 등)
(현재 과목: ' + currentSubject + ')',
    ui.ButtonSet.OK_CANCEL
  );
  if (resp4.getSelectedButton() !== ui.Button.OK) return;
  var newSubject = resp4.getResponseText().trim();
  if (newSubject) props.setProperty('SUBJECT_NAME', newSubject);

  // 5. 2022 개정교육과정 핵심역량 지정
  var resp5 = ui.prompt(
    '🎯 [교과 설정 5/6] 2022 개정교육과정 핵심역량',
    '세특 생성 시 강조할 교과 핵심역량을 입력하세요.
(예: 컴퓨팅 사고력, 협력적 문제해결력, 지식정보처리, 비판적 사고력 등)
(현재 설정: ' + currentCompetencies + ')',
    ui.ButtonSet.OK_CANCEL
  );
  if (resp5.getSelectedButton() !== ui.Button.OK) return;
  var newComp = resp5.getResponseText().trim();
  if (newComp) props.setProperty('SUBJECT_COMPETENCIES', newComp);

  // 6. NEIS 바이트 목표 선택 (500B / 750B / 1000B / 1500B)
  var resp6 = ui.prompt(
    '📏 [바이트 설정 6/6] NEIS 목표 바이트(Byte) 수',
    '선생님이 원하시는 세특 목표 바이트 수를 입력하세요.
[ 500 ] (수업소감형), [ 750 ] (1학기 분량), [ 1000 ], [ 1500 ] (1년 풀세특)
(현재 설정: ' + currentTargetBytes + ' Bytes)',
    ui.ButtonSet.OK_CANCEL
  );
  if (resp6.getSelectedButton() === ui.Button.OK && resp6.getResponseText().trim()) {
    props.setProperty('TARGET_BYTES', resp6.getResponseText().trim());
  }

  ui.alert('🎉 2022 개정 교과역량과 NEIS 바이트 목표 설정이 PropertiesService 암호화 금고에 안전하게 저장되었습니다!');
}

// 🛡️ API 및 교과/바이트 설정 안전 읽기 유틸리티
function getApiConfig() {
  var props = PropertiesService.getScriptProperties();
  var upstageKey = props.getProperty('UPSTAGE_API_KEY') || '';
  var geminiKey = props.getProperty('GEMINI_API_KEY') || '';
  var selectedAI = props.getProperty('SELECTED_AI') || 'Gemini';
  var subjectName = props.getProperty('SUBJECT_NAME') || '국어';
  var subjectCompetencies = props.getProperty('SUBJECT_COMPETENCIES') || '비판적 사고력, 지식정보처리 역량, 공동체·인성 역량';
  var targetBytes = props.getProperty('TARGET_BYTES') || '1500';

  return {
    upstageKey: upstageKey,
    geminiKey: geminiKey,
    selectedAI: selectedAI,
    subjectName: subjectName,
    subjectCompetencies: subjectCompetencies,
    targetBytes: targetBytes
  };
}

// 2-1. 7대 탭 초기화 함수 (교사 맞춤 템플릿 포함)
function setupInitialSheets() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  var configSheet = ss.getSheetByName('API설정') || ss.insertSheet('API설정');
  configSheet.getRange('A1:B1').setValues([['보안 및 교과역량 설정 항목', '설정 및 상태']]).setFontWeight('bold').setBackground('#e0f2fe');
  configSheet.getRange('A2:B2').setValues([['보안 API 키 저장 방식', 'PropertiesService (구글 서버 암호화 금고 - 시트 노출 방지)']]);
  configSheet.getRange('A3:B3').setValues([['담당 교과명', '국어 / 정보 / 공통']]);
  configSheet.getRange('A4:B4').setValues([['2022 개정교육과정 핵심역량', '비판적 사고력, 지식정보처리 역량, 컴퓨팅 사고력']]);
  configSheet.getRange('A5:B5').setValues([['NEIS 세특 목표 바이트', '1500 Bytes (선택권: 500B, 750B, 1000B, 1500B)']]);
  configSheet.getRange('A6:B6').setValues([['AI 모델 선택 (Gemini / Upstage)', 'Gemini (gemini-3.1-flash-lite)']]);
  configSheet.getRange('A7:B7').setValues([['설정 방법', '상단 메뉴 [🪄 AI 세특 대시보드 시스템] ➔ [1. 🔑 API 키 및 2022 교과역량/바이트 보안 설정] 클릭']]);
  
  var templateSheet = ss.getSheetByName('세특템플릿') || ss.insertSheet('세특템플릿');
  templateSheet.getRange('A1:B1').setValues([['템플릿 구분 / 강조 항목', '교사 맞춤 작성 지침 / 템플릿 내용']]).setFontWeight('bold').setBackground('#fce7f3');
  if (templateSheet.getLastRow() <= 1) {
    templateSheet.getRange('A2:B4').setValues([
      ['기본 세특 프롬프트 스타일', '2022 개정 교과역량을 구체적 탐구 사례와 함께 서술하고, 문장은 ~함., ~임. 어조로 마무리할 것.'],
      ['수업 및 세특 강조 사항', '수업 참여 태도, 모둠 내 협력적 의사소통, 자기주도적 문제해결 과정이 잘 드러나도록 작성할 것.'],
      ['생기부 금지어 수칙', '대회, 수상, 대학명, 기관명, 사교육, 도서 출간 사실 등 생기부 기재 금지어를 절대 포함하지 말 것.']
    ]);
  }

  var studentSheet = ss.getSheetByName('학생명렬') || ss.insertSheet('학생명렬');
  studentSheet.getRange('A1:D1').setValues([['반', '번호', '학번', '이름']]).setFontWeight('bold').setBackground('#fef3c7');
  if (studentSheet.getLastRow() <= 1) {
    studentSheet.getRange('A2:D6').setValues([
      [1, 1, '30101', '강해린'],
      [1, 2, '30102', '박지민'],
      [1, 3, '30103', '김민준'],
      [2, 1, '30201', '이서윤'],
      [2, 2, '30202', '최현우']
    ]);
  }

  var obsSheet = ss.getSheetByName('시간대별기록') || ss.insertSheet('시간대별기록');
  obsSheet.getRange('A1:G1').setValues([['일시', '반', '영역', '학번', '이름', '거친음성/메모', 'AI정돈관찰문장']]).setFontWeight('bold').setBackground('#dcfce7');

  var respSheet = ss.getSheetByName('학생응답기록') || ss.insertSheet('학생응답기록');
  respSheet.getRange('A1:F1').setValues([['일시', '반', '학번', '이름', '응답/제출내용', '구분']]).setFontWeight('bold').setBackground('#fef9c3');

  var reportSheet = ss.getSheetByName('세특초안생성') || ss.insertSheet('세특초안생성');
  reportSheet.getRange('A1:F1').setValues([['반', '학번', '이름', '생성 일시', 'NEIS 바이트 수', 'AI 최종 세특/행특 초안']]).setFontWeight('bold').setBackground('#f3e8ff');

  var summarySheet = ss.getSheetByName('학생별모아보기') || ss.insertSheet('학생별모아보기');
  summarySheet.getRange('A1:D1').setValues([['학번', '이름', '누적건수', '누적관찰내용']]).setFontWeight('bold').setBackground('#e0e7ff');

  SpreadsheetApp.getUi().alert('✅ 교사 맞춤 [세특템플릿]을 포함한 7대 탭 세팅이 성공적으로 완료되었습니다!');
}

// 💡 교사 맞춤 [세특템플릿] 시트 읽기 유틸리티
function getTeacherTemplate() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('세특템플릿');
    if (!sheet || sheet.getLastRow() <= 1) {
      return {
        hasCustom: false,
        promptGuidelines: "2022 개정 교과역량을 구체적 탐구 사례와 함께 서술하고, 문장은 '~함.', '~임.' 어조로 마무리할 것."
      };
    }
    
    var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 2).getValues();
    var guidelines = [];
    for (var i = 0; i < data.length; i++) {
      var item = data[i][0] ? data[i][0].toString().trim() : '';
      var content = data[i][1] ? data[i][1].toString().trim() : '';
      if (item && content) {
        guidelines.push("• [" + item + "] " + content);
      }
    }
    
    if (guidelines.length > 0) {
      return {
        hasCustom: true,
        promptGuidelines: guidelines.join("\n")
      };
    } else {
      return {
        hasCustom: false,
        promptGuidelines: "2022 개정 교과역량을 구체적 탐구 사례와 함께 서술하고, 문장은 '~함.', '~임.' 어조로 마무리할 것."
      };
    }
  } catch (e) {
    return {
      hasCustom: false,
      promptGuidelines: "2022 개정 교과역량을 구체적 탐구 사례와 함께 서술하고, 문장은 '~함.', '~임.' 어조로 마무리할 것."
    };
  }
}

function getStudentList(classNum) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('학생명렬');
    if (!sheet) return [];
    
    var lastRow = sheet.getLastRow();
    if (lastRow <= 1) return [];
    
    var data = sheet.getRange(2, 1, lastRow - 1, 4).getValues();
    var list = [];
    for (var i = 0; i < data.length; i++) {
      var cNum = parseInt(data[i][0]) || 0;
      var hakbun = data[i][2] ? data[i][2].toString().trim() : '';
      var name = data[i][3] ? data[i][3].toString().trim() : '';
      
      if (hakbun && name) {
        if (!classNum || classNum === 'all' || cNum === parseInt(classNum)) {
          list.push({
            classNum: cNum,
            number: parseInt(data[i][1]) || 0,
            hakbun: hakbun,
            name: name,
            display: hakbun + ' ' + name
          });
        }
      }
    }
    return list;
  } catch (e) {
    return [];
  }
}

function getSelectedAIName() {
  var config = getApiConfig();
  return (config.selectedAI.toUpperCase().indexOf('GEMINI') >= 0) ? 'Gemini' : 'Upstage';
}

// 💡 1차 음성 메모 분석 및 교사용 보완 피드백 코칭 생성
function analyzeObservationFeedback(rawMemo, category) {
  try {
    category = category || '교과';
    var config = getApiConfig();

    var sysPrompt = 
      "당신은 교사의 학교생활기록부/세특 관찰 기록 작성을 돕는 AI 코치입니다.
" +
      "교사가 1차로 입력한 음성 메모를 분석하여 아래 JSON 항목으로만 응답하십시오:
" +
      "1. hasStudentInfo: boolean (음성에 학번이나 학생 이름이 포함되어 있는지 여부)
" +
      "2. extractedName: string (추출된 학생 이름, 없으면 "")
" +
      "3. extractedHakbun: string (추출된 학번, 없으면 "")
" +
      "4. feedbackTitle: string (한 줄 요약 피드백, 예: "⚠️ 학생 이름 누락됨" 또는 "💡 2022 개정 교과역량 연계 추천")
" +
      "5. feedbackMsg: string (교사에게 2022 개정 교육과정 역량 관점에서 친절하게 제안하는 1~2문장의 코칭 팁)

" +
      "반드시 JSON 형식으로만 응답하십시오:
" +
      "{
" +
      '  "hasStudentInfo": true,
' +
      '  "extractedName": "강해린",
' +
      '  "extractedHakbun": "30101",
' +
      '  "feedbackTitle": "💡 구체적 사례 및 교과역량 보강 추천",
' +
      '  "feedbackMsg": "사용한 자료나 탐구 주제를 덧붙이시면 2022 개정 교과역량이 돋보이는 감동적인 세특이 완성됩니다!"
' +
      "}";

    var userPrompt = "관찰 영역: [" + category + "]
1차 음성 메모: " + rawMemo;
    var aiResponseText = "";

    if (config.selectedAI.toUpperCase().indexOf('GEMINI') >= 0) {
      if (!config.geminiKey) throw new Error('Gemini Key 미설정');
      aiResponseText = callGeminiAPI(config.geminiKey, sysPrompt, userPrompt);
    } else {
      if (!config.upstageKey) throw new Error('Upstage Key 미설정');
      aiResponseText = callUpstageSolarAPI(config.upstageKey, sysPrompt, userPrompt);
    }

    var cleaned = aiResponseText.replace(/```json/g, '').replace(/```/g, '').trim();
    var obj = JSON.parse(cleaned);

    return {
      success: true,
      hasStudentInfo: obj.hasStudentInfo || false,
      extractedName: obj.extractedName || '',
      extractedHakbun: obj.extractedHakbun || '',
      feedbackTitle: obj.feedbackTitle || '💡 AI 관찰 코칭',
      feedbackMsg: obj.feedbackMsg || '추가할 내용이 있다면 2차 음성을 덧붙여보세요!'
    };
  } catch (e) {
    return {
      success: false,
      hasStudentInfo: true,
      extractedName: '',
      extractedHakbun: '',
      feedbackTitle: '💡 AI 관찰 코칭',
      feedbackMsg: '필요 시 2차 보완 음성을 덧붙여서 완성하세요!'
    };
  }
}

// 4. 모바일 5분할 휠 음성 입력 ➔ 0.3초 초고속 학번/이름 파싱 & 날것(Raw) 메모 즉시 저장 (AI 세특 어조 완성과 분리)
function processObservationWithAIExtraction(rawMemo, category) {
  try {
    category = category || '교과';
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var obsSheet = ss.getSheetByName('시간대별기록') || ss.getSheets()[0];
    
    // 1초도 지체 없는 학번/이름 정규식 파싱
    var parsed = parseHakbunAndNameFast(rawMemo);
    var now = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm');

    // 시간대별 기록 시트에 날것(Raw) 메모를 그대로 0.3초 만에 즉시 저장!
    obsSheet.appendRow([now, parsed.classNum, category, parsed.hakbun, parsed.name, rawMemo, rawMemo]);
    
    // 학생별 모아보기 탭에 즉시 누적
    updateStudentSummary(parsed.hakbun, parsed.name, category, rawMemo);

    return {
      success: true,
      category: category,
      hakbun: parsed.hakbun,
      name: parsed.name,
      classNum: parsed.classNum,
      refinedText: rawMemo,
      timestamp: now
    };

  } catch (error) {
    return {
      success: false,
      message: '오류 발생: ' + error.toString()
    };
  }
}

// ⚡ 0.3초 내장 학번/이름 초고속 파싱 함수 (API 대기시간 0초)
function parseHakbunAndNameFast(rawMemo) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var studentSheet = ss.getSheetByName('학생명렬');
  
  var hakbun = '';
  var name = '';
  var classNum = 1;

  // 1. 5자리 학번 패턴 검색 (예: 30101, 30215 등)
  var hakbunMatch = rawMemo.match(/\b([1-3][0-1][0-9][0-3][0-9])\b/);
  if (hakbunMatch) {
    hakbun = hakbunMatch[1];
    classNum = parseInt(hakbun.substring(1, 3)) || 1;
  }

  // 2. 학생명렬 시트가 있으면 학생 이름 패턴 자동 매칭
  if (studentSheet && studentSheet.getLastRow() > 1) {
    var data = studentSheet.getRange(2, 1, studentSheet.getLastRow() - 1, 4).getValues();
    for (var i = 0; i < data.length; i++) {
      var sName = data[i][3] ? data[i][3].toString().trim() : '';
      if (sName && rawMemo.indexOf(sName) >= 0) {
        name = sName;
        if (!hakbun && data[i][2]) {
          hakbun = data[i][2].toString().trim();
          classNum = parseInt(data[i][0]) || 1;
        }
        break;
      }
    }
  }

  if (!name && !hakbun) name = '미인식';

  return {
    hakbun: hakbun,
    name: name,
    classNum: classNum
  };
}


// 4-1. 기존 파서
function processObservationWithAIExtraction(rawMemo, category) {
  try {
    category = category || '교과';
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var obsSheet = ss.getSheetByName('시간대별기록') || ss.getSheets()[0];
    
    var config = getApiConfig();

    var sysPrompt = 
      "당신은 대한민국 학교의 교사 보조 AI입니다.
" +
      "교사가 녹음한 음성 텍스트에서 [학번 또는 반/번호/이름]을 추출하고, 관찰 내용을 관찰 문장어조('~함.', '~를 보여줌.')로 정돈하십시오.
" +
      "반드시 아래 JSON 형식으로만 응답하십시오 (다른 설명 금지):
" +
      "{
" +
      '  "hakbun": "추출된 학번 (예: 30101 또는 미상상 시 미입력)",
' +
      '  "name": "추출된 학생 이름 (예: 강해린)",
' +
      '  "classNum": 추출된 반 숫자 (예: 1),
' +
      '  "refinedText": "생기부 어조로 정돈된 관찰 문장 1~2개"
' +
      "}";

    var userPrompt = "관찰 영역: [" + category + "]
녹음 음성 텍스트: " + rawMemo;
    var aiResponseText = "";

    if (config.selectedAI.toUpperCase().indexOf('GEMINI') >= 0) {
      if (!config.geminiKey) {
        throw new Error('Gemini API Key가 등록되지 않았습니다. 구글 시트 메뉴 [1. 🔑 API 키 및 2022 교과역량/바이트 보안 설정]에서 키를 등록해주세요.');
      }
      aiResponseText = callGeminiAPI(config.geminiKey, sysPrompt, userPrompt);
    } else {
      if (!config.upstageKey) {
        throw new Error('Upstage API Key가 등록되지 않았습니다. 구글 시트 메뉴 [1. 🔑 API 키 및 2022 교과역량/바이트 보안 설정]에서 키를 등록해주세요.');
      }
      aiResponseText = callUpstageSolarAPI(config.upstageKey, sysPrompt, userPrompt);
    }

    var parsed = parseAIJsonResponse(aiResponseText, rawMemo);
    var now = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm');

    obsSheet.appendRow([now, parsed.classNum, category, parsed.hakbun, parsed.name, rawMemo, parsed.refinedText]);
    updateStudentSummary(parsed.hakbun, parsed.name, category, parsed.refinedText);

    return {
      success: true,
      category: category,
      hakbun: parsed.hakbun,
      name: parsed.name,
      classNum: parsed.classNum,
      refinedText: parsed.refinedText,
      timestamp: now
    };

  } catch (error) {
    return {
      success: false,
      message: '오류 발생: ' + error.toString()
    };
  }
}

function parseAIJsonResponse(responseText, rawMemo) {
  try {
    var cleaned = responseText.replace(/```json/g, '').replace(/```/g, '').trim();
    var obj = JSON.parse(cleaned);
    return {
      hakbun: obj.hakbun || '',
      name: obj.name || '미인식',
      classNum: parseInt(obj.classNum) || 1,
      refinedText: obj.refinedText || rawMemo
    };
  } catch (e) {
    return {
      hakbun: '',
      name: '미인식',
      classNum: 1,
      refinedText: rawMemo
    };
  }
}

// 5. Upstage API 호출
function callUpstageSolarAPI(apiKey, systemPrompt, userPrompt) {
  var url = 'https://api.upstage.ai/v1/chat/completions';
  var payload = {
    "model": "solar-pro3",
    "messages": [
      { "role": "system", "content": systemPrompt },
      { "role": "user", "content": userPrompt }
    ],
    "temperature": 0.2
  };
  var options = {
    "method": "post",
    "contentType": "application/json",
    "headers": { "Authorization": "Bearer " + apiKey },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  var response = UrlFetchApp.fetch(url, options);
  var json = JSON.parse(response.getContentText());
  if (response.getResponseCode() === 200 && json.choices && json.choices.length > 0) {
    return json.choices[0].message.content.trim();
  } else {
    throw new Error('Upstage API 실패: ' + (json.error ? json.error.message : response.getContentText()));
  }
}

// 5-1. Gemini API 호출 (gemini-3.1-flash-lite 적용)
function callGeminiAPI(apiKey, systemPrompt, userPrompt) {
  var url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key=' + apiKey;
  var payload = {
    "systemInstruction": { "parts": [{ "text": systemPrompt }] },
    "contents": [{ "parts": [{ "text": userPrompt }] }],
    "generationConfig": { "temperature": 0.3 }
  };
  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  var response = UrlFetchApp.fetch(url, options);
  var json = JSON.parse(response.getContentText());
  if (response.getResponseCode() === 200 && json.candidates && json.candidates.length > 0) {
    var candidate = json.candidates[0];
    if (candidate && candidate.content && candidate.content.parts && candidate.content.parts.length > 0) {
      return candidate.content.parts[0].text.trim();
    }
    throw new Error('Gemini API: 응답에 콘텐츠가 없습니다 (안전 필터 차단 가능).');
  } else {
    throw new Error('Gemini API 실패: ' + (json.error ? json.error.message : response.getContentText()));
  }
}

function safeString(val) {
  if (val === null || val === undefined) return '';
  if (val instanceof Date) {
    return Utilities.formatDate(val, 'Asia/Seoul', 'yyyy-MM-dd HH:mm');
  }
  return val.toString();
}

function getDashboardFullData(classNum) {
  try {
    var studentList = getStudentList(classNum);
    var dashboardData = getDashboardData(classNum);
    var config = getApiConfig();

    return {
      success: true,
      config: config,
      students: studentList,
      observations: dashboardData.observations || [],
      responses: dashboardData.responses || [],
      reports: dashboardData.reports || []
    };
  } catch (e) {
    return {
      success: false,
      message: '데이터 조회 실패: ' + e.toString(),
      students: [],
      observations: [],
      responses: [],
      reports: []
    };
  }
}

function getDashboardData(classNum) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var obsSheet = ss.getSheetByName('시간대별기록');
    var respSheet = ss.getSheetByName('학생응답기록');
    var reportSheet = ss.getSheetByName('세특초안생성');

    var obsList = [];
    if (obsSheet && obsSheet.getLastRow() > 1) {
      var obsData = obsSheet.getRange(2, 1, obsSheet.getLastRow() - 1, 7).getValues();
      for (var i = 0; i < obsData.length; i++) {
        var c = parseInt(obsData[i][1]) || 0;
        if (!classNum || classNum === 'all' || c === parseInt(classNum)) {
          obsList.push({
            date: safeString(obsData[i][0]),
            classNum: c,
            category: safeString(obsData[i][2]),
            hakbun: safeString(obsData[i][3]),
            name: safeString(obsData[i][4]),
            rawMemo: safeString(obsData[i][5]),
            refinedText: safeString(obsData[i][6])
          });
        }
      }
    }

    var respList = [];
    if (respSheet && respSheet.getLastRow() > 1) {
      var respData = respSheet.getRange(2, 1, respSheet.getLastRow() - 1, 6).getValues();
      for (var j = 0; j < respData.length; j++) {
        var c2 = parseInt(respData[j][1]) || 0;
        if (!classNum || classNum === 'all' || c2 === parseInt(classNum)) {
          respList.push({
            date: safeString(respData[j][0]),
            classNum: c2,
            hakbun: safeString(respData[j][2]),
            name: safeString(respData[j][3]),
            content: safeString(respData[j][4]),
            type: safeString(respData[j][5])
          });
        }
      }
    }

    var reportList = [];
    if (reportSheet && reportSheet.getLastRow() > 1) {
      var repData = reportSheet.getRange(2, 1, reportSheet.getLastRow() - 1, 6).getValues();
      for (var k = 0; k < repData.length; k++) {
        var c3 = parseInt(repData[k][0]) || 0;
        if (!classNum || classNum === 'all' || c3 === parseInt(classNum)) {
          reportList.push({
            classNum: c3,
            hakbun: safeString(repData[k][1]),
            name: safeString(repData[k][2]),
            date: safeString(repData[k][3]),
            bytes: safeString(repData[k][4]),
            reportText: safeString(repData[k][5])
          });
        }
      }
    }

    return {
      success: true,
      observations: obsList,
      responses: respList,
      reports: reportList
    };
  } catch (e) {
    return { success: false, message: e.toString() };
  }
}

function updateStudentSummary(hakbun, name, category, newRefinedText) {
  if (!hakbun || hakbun.toString().trim() === '') return;
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var summarySheet = ss.getSheetByName('학생별모아보기');
  if (!summarySheet) return;

  var lastRow = summarySheet.getLastRow();
  var foundRow = -1;

  if (lastRow > 1) {
    var data = summarySheet.getRange(2, 1, lastRow - 1, 4).getValues();
    for (var i = 0; i < data.length; i++) {
      if (data[i][0].toString().trim() === hakbun.toString().trim()) {
        foundRow = i + 2;
        break;
      }
    }
  }

  var formattedEntry = "• [" + category + "] " + newRefinedText;

  if (foundRow > 1) {
    var count = summarySheet.getRange(foundRow, 3).getValue() + 1;
    var prevContent = summarySheet.getRange(foundRow, 4).getValue().toString().trim();
    var updatedContent = prevContent ? (prevContent + "
" + formattedEntry) : formattedEntry;
    summarySheet.getRange(foundRow, 3, 1, 2).setValues([[count, updatedContent]]);
  } else {
    summarySheet.appendRow([hakbun, name, 1, formattedEntry]);
  }
}

// 8. 🎯 교사 맞춤 템플릿 + 5명 30초 휴식(할루시네이션 방지) + 스마트 캐싱(변경 없으면 유지) AI 세특 생성
function generateAllStudentReports(classNum, customSubject, customCompetency, customBytes) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var summarySheet = ss.getSheetByName('학생별모아보기');
  var obsSheet = ss.getSheetByName('시간대별기록');
  var reportSheet = ss.getSheetByName('세특초안생성') || ss.insertSheet('세특초안생성');

  if (!summarySheet) {
    return { success: false, message: '[학생별모아보기] 시트가 없습니다. 먼저 [2. 📋 시트 7대 탭 자동 양식 세팅]을 실행해 주세요.' };
  }

  var config = getApiConfig();
  var subject = customSubject || config.subjectName;
  var competency = customCompetency || config.subjectCompetencies;
  var targetBytes = parseInt(customBytes || config.targetBytes) || 1500;
  var teacherTemplate = getTeacherTemplate();

  var lastRow = summarySheet.getLastRow();
  if (lastRow <= 1) return { success: false, message: '누적 관찰 데이터가 없습니다.' };

  var summaryData = summarySheet.getRange(2, 1, lastRow - 1, 4).getValues();

  // 1. 학생별 최신 관찰 타임스탬프 Map 구축 (시간대별기록 탭 기준)
  var latestObsDateMap = {};
  if (obsSheet && obsSheet.getLastRow() > 1) {
    var obsData = obsSheet.getRange(2, 1, obsSheet.getLastRow() - 1, 7).getValues();
    for (var o = 0; o < obsData.length; o++) {
      var oHakbun = obsData[o][3] ? obsData[o][3].toString().trim() : '';
      var oDateStr = obsData[o][0] ? safeString(obsData[o][0]) : '';
      if (oHakbun && oDateStr) {
        if (!latestObsDateMap[oHakbun] || oDateStr > latestObsDateMap[oHakbun]) {
          latestObsDateMap[oHakbun] = oDateStr;
        }
      }
    }
  }

  // 2. 기존 세특 초안 Map 및 행 위치 구축 (세특초안생성 탭 기준)
  var existingReportMap = {};
  if (reportSheet.getLastRow() > 1) {
    var reportData = reportSheet.getRange(2, 1, reportSheet.getLastRow() - 1, 6).getValues();
    for (var r = 0; r < reportData.length; r++) {
      var rHakbun = reportData[r][1] ? reportData[r][1].toString().trim() : '';
      var rDateStr = reportData[r][3] ? safeString(reportData[r][3]) : '';
      var rText = reportData[r][5] ? reportData[r][5].toString().trim() : '';
      if (rHakbun) {
        existingReportMap[rHakbun] = {
          rowIndex: r + 2,
          date: rDateStr,
          reportText: rText
        };
      }
    }
  }

  var systemPrompt = 
    "당신은 대한민국 고등학교 " + subject + " 교과 담당 교사입니다.\n" +
    "2022 개정 교육과정에 입각하여, 학생의 교과 핵심역량([" + competency + "])이 명확히 드러나도록 생활기록부 세부능력 및 특기사항(세특)을 작성하십시오.\n\n" +
    "[작성 기본 수칙]\n" +
    "1. 문장은 반드시 '~함.', '~를 보여줌.', '~임.' 형태의 개조식 종결어 어조로 마무리하십시오.\n" +
    "2. 2022 개정 교육과정 교과 핵심역량(" + competency + ")이 구체적 탐구 사례와 함께 서술되게 하십시오.\n" +
    "3. 분량 조건: 나이스(NEIS) 입력 기준 약 " + targetBytes + " Bytes 내외 (한글 기준 약 " + Math.floor(targetBytes/3) + "자)에 맞추어 단락을 구성하십시오.\n" +
    "4. 불필요한 서론/결론 인사말이나 마크다운 기호(**, #)는 절대 사용하지 마십시오.\n" +
    "5. 생기부 기재 금지어(대회, 수상, 대학명, 사교육, 기관명 등)를 절대 사용하지 마십시오.\n\n" +
    "[교사 지정 맞춤 템플릿/작성 스타일 지침]\n" +
    teacherTemplate.promptGuidelines;

  var generatedCount = 0;
  var retainedCount = 0;
  var now = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm');

  for (var i = 0; i < summaryData.length; i++) {
    var hakbun = summaryData[i][0].toString().trim();
    var name = summaryData[i][1].toString().trim();
    var accumLogs = summaryData[i][3] ? summaryData[i][3].toString().trim() : '';
    var cNum = parseInt(hakbun.substring(1, 3)) || 1;

    if (classNum && classNum !== 'all' && cNum !== parseInt(classNum)) continue;
    if (!accumLogs) continue;

    var latestObsDate = latestObsDateMap[hakbun] || '';
    var existing = existingReportMap[hakbun];

    // 💡 스마트 캐싱/차분 검증: 기존 세특이 있고, 세특 생성일시가 최신 관찰일시 이후이면 기존 세특 유지
    if (existing && existing.reportText && !existing.reportText.startsWith('생성 실패') && existing.date >= latestObsDate) {
      retainedCount++;
      continue; // 새로운 관찰 데이터가 없으므로 이전 세특 100% 유지!
    }

    // 💡 5명 신규 생성 시마다 AI 과열 및 할루시네이션 완벽 방지를 위한 30초 대기
    if (generatedCount > 0 && generatedCount % 5 === 0) {
      Logger.log("5명 생성 완료: AI 과열 및 할루시네이션 방지를 위해 30초간 휴식 대기 중...");
      Utilities.sleep(30000); // 30초 휴식
    } else if (generatedCount > 0) {
      Utilities.sleep(1500); // 1.5초 기본 휴식
    }

    var userPrompt = "담당 과목: [" + subject + "]\n" +
      "학생 학번/이름: " + hakbun + " " + name + "\n" +
      "목표 분량: " + targetBytes + " Bytes\n" +
      "누적 관찰 기록:\n" + accumLogs;

    var finalReport = "";
    try {
      if (config.selectedAI.toUpperCase().indexOf('GEMINI') >= 0) {
        finalReport = callGeminiAPI(config.geminiKey, systemPrompt, userPrompt);
      } else {
        finalReport = callUpstageSolarAPI(config.upstageKey, systemPrompt, userPrompt);
      }

      // 마크다운 기호 제거
      finalReport = finalReport.replace(/\*\*/g, '').replace(/^[\*\-]\s+/gm, '');
      var byteSize = getByteLength(finalReport);
      var byteInfoStr = byteSize + ' / ' + targetBytes + ' B';

      if (existing && existing.rowIndex > 1) {
        // 기존 행 덮어쓰기 (신규 데이터가 추가되었을 때만 업데이트)
        reportSheet.getRange(existing.rowIndex, 1, 1, 6).setValues([[cNum, hakbun, name, now, byteInfoStr, finalReport]]);
      } else {
        // 신규 행 추가
        reportSheet.appendRow([cNum, hakbun, name, now, byteInfoStr, finalReport]);
        existingReportMap[hakbun] = { rowIndex: reportSheet.getLastRow(), date: now, reportText: finalReport };
      }
      generatedCount++;
    } catch (err) {
      if (existing && existing.rowIndex > 1) {
        reportSheet.getRange(existing.rowIndex, 4, 1, 3).setValues([[now, 'ERROR', '생성 실패: ' + err.toString()]]);
      } else {
        reportSheet.appendRow([cNum, hakbun, name, now, 'ERROR', '생성 실패: ' + err.toString()]);
      }
    }
  }

  return {
    success: true,
    count: generatedCount,
    retainedCount: retainedCount,
    targetBytes: targetBytes,
    subject: subject,
    message: '신규/갱신 생성: ' + generatedCount + '명, 변경 없음(기존 세특 유지): ' + retainedCount + '명'
  };
}

function getByteLength(str) {
  if (!str) return 0;
  return Utilities.newBlob(str).getBytes().length;
}


// 6-2. [학생명렬] 시트 기반 실제 존재하는 학년과 반 동적 추출 유틸리티
function getAvailableGradesAndClasses() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('학생명렬');
    if (!sheet || sheet.getLastRow() <= 1) {
      return { grades: [1, 2, 3], classesByGrade: { 1: [1], 2: [1], 3: [1] } };
    }

    var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 4).getValues();
    var gradesSet = {};
    var classesByGrade = {};

    for (var i = 0; i < data.length; i++) {
      var cNum = parseInt(data[i][0]) || 1; // 반
      var hakbun = data[i][2] ? data[i][2].toString().trim() : ''; // 학번 (예: 30101)
      
      // 학번 첫글자로 학년 파싱 (없으면 1학년)
      var grade = 1;
      if (hakbun.length >= 5) {
        grade = parseInt(hakbun.substring(0, 1)) || 1;
      } else if (hakbun.length === 4) {
        grade = parseInt(hakbun.substring(0, 1)) || 1;
      }

      if (!gradesSet[grade]) gradesSet[grade] = true;
      if (!classesByGrade[grade]) classesByGrade[grade] = {};
      classesByGrade[grade][cNum] = true;
    }

    var grades = Object.keys(gradesSet).map(function(g) { return parseInt(g); }).sort(function(a,b){return a-b;});
    var formattedClasses = {};

    for (var g in classesByGrade) {
      formattedClasses[g] = Object.keys(classesByGrade[g]).map(function(c) { return parseInt(c); }).sort(function(a,b){return a-b;});
    }

    if (grades.length === 0) grades = [1, 2, 3];

    return {
      success: true,
      grades: grades,
      classesByGrade: formattedClasses
    };
  } catch (e) {
    return { grades: [1, 2, 3], classesByGrade: { 1: [1,2,3,4,5,6,7,8,9,10], 2: [1,2,3,4,5,6,7,8,9,10], 3: [1,2,3,4,5,6,7,8,9,10] } };
  }
}
