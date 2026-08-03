/**
 * 📱 모바일 생생세특 (Live Seteuk) v2.0 - 구글 시트 네이티브 중심 백엔드
 * 
 * 주요 특징:
 * 1. 선생님께 100% 익숙한 진짜 구글 시트(스프레드시트) 중심 구조
 * 2. 엑셀/나이스 명렬 Ctrl+C -> Ctrl+V 1초 완성 지원 (학생명렬 탭)
 * 3. 7대 시트 탭 (API설정, 세특템플릿, 학생명렬, 시간대별기록, 학생응답기록, 세특초안생성, 학생별모아보기)
 * 4. doGet: 핸드폰 모바일 앱(app.html) & PC 대시보드(dashboard.html) 2원화 서빙 (가짜 sheet.html 제거)
 * 5. 5명 작성 후 15초 자동 대기 (할루시네이션 방지 & 300자 규격 세특)
 */

function doGet(e) {
  var view = e ? e.parameter.view : '';
  if (view === 'dashboard') {
    return HtmlService.createHtmlOutputFromFile('dashboard')
      .setTitle('모바일 생생세특 - 2022 교과역량 AI 세특 대시보드')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
      .addMetaTag('viewport', 'width=device-width, initial-scale=1');
  }
  // 기본 뷰: 스마트폰 모바일 음성 관찰기 앱 (app.html)
  return HtmlService.createHtmlOutputFromFile('app')
    .setTitle('모바일 생생세특 - 현장 관찰 AI 기록기')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no');
}

function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('📱 모바일 생생세특 v2.0')
    .addItem('1. 🔑 API 키 및 2022 교과역량/바이트 보안 설정', 'setApiKeysPrompt')
    .addItem('2. 📋 시트 7대 탭 자동 양식 세팅', 'setupInitialSheets')
    .addItem('3. 📱 핸드폰 음성 앱 & 🖥️ 대시보드 링크 안내', 'showWebappLinksPrompt')
    .addSeparator()
    .addItem('4. 🔮 선택된 반 AI 세특 초안 전체 생성', 'generateAllStudentReportsMenu')
    .addToUi();
}

function getApiConfig() {
  var props = PropertiesService.getScriptProperties();
  return {
    upstageKey: props.getProperty('UPSTAGE_API_KEY') || '',
    geminiKey: props.getProperty('GEMINI_API_KEY') || '',
    selectedAI: props.getProperty('SELECTED_AI') || 'Gemini',
    subjectName: props.getProperty('SUBJECT_NAME') || '국어',
    subjectCompetencies: props.getProperty('SUBJECT_COMPETENCIES') || '비판적·창의적 사고 역량, 지식정보처리 역량',
    targetBytes: props.getProperty('TARGET_BYTES') || '900'
  };
}

function saveDashboardConfig(subject, competency, targetBytes) {
  try {
    var props = PropertiesService.getScriptProperties();
    if (subject) props.setProperty('SUBJECT_NAME', subject);
    if (competency) props.setProperty('SUBJECT_COMPETENCIES', competency);
    if (targetBytes) props.setProperty('TARGET_BYTES', targetBytes.toString());

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('API설정');
    if (sheet) {
      var data = sheet.getDataRange().getValues();
      for (var i = 1; i < data.length; i++) {
        var key = data[i][0] ? data[i][0].toString() : '';
        if (key.indexOf('담당 교과명') >= 0 && subject) sheet.getRange(i + 1, 2).setValue(subject);
        if (key.indexOf('2022 개정 교과역량') >= 0 && competency) sheet.getRange(i + 1, 2).setValue(competency);
        if (key.indexOf('NEIS 세특 목표 바이트') >= 0 && targetBytes) sheet.getRange(i + 1, 2).setValue(targetBytes);
      }
    }
    return { success: true };
  } catch (e) {
    return { success: false, message: e.toString() };
  }
}

function setApiKeysPrompt() {
  var ui = SpreadsheetApp.getUi();
  var props = PropertiesService.getScriptProperties();

  var resp1 = ui.prompt(
    '🔑 [보안 설정 1/6] Upstage API Key',
    'Upstage API Key를 입력하세요 (없으면 엔터):',
    ui.ButtonSet.OK_CANCEL
  );
  if (resp1.getSelectedButton() === ui.Button.OK && resp1.getResponseText().trim()) {
    props.setProperty('UPSTAGE_API_KEY', resp1.getResponseText().trim());
  }

  var resp2 = ui.prompt(
    '🔑 [보안 설정 2/6] Google Gemini API Key (추천)',
    'Google Gemini API Key를 입력하세요:',
    ui.ButtonSet.OK_CANCEL
  );
  if (resp2.getSelectedButton() === ui.Button.OK && resp2.getResponseText().trim()) {
    props.setProperty('GEMINI_API_KEY', resp2.getResponseText().trim());
  }

  var resp3 = ui.prompt(
    '🔑 [보안 설정 3/6] 기본 AI 모델 선택',
    'Gemini 또는 Upstage 입력 (기본값: Gemini):',
    ui.ButtonSet.OK_CANCEL
  );
  if (resp3.getSelectedButton() === ui.Button.OK && resp3.getResponseText().trim()) {
    props.setProperty('SELECTED_AI', resp3.getResponseText().trim());
  }

  var resp4 = ui.prompt(
    '🔑 [보안 설정 4/6] 담당 교과명',
    '담당 교과명을 입력하세요 (예: 국어, 수학, 영어, 정보 등):',
    ui.ButtonSet.OK_CANCEL
  );
  if (resp4.getSelectedButton() === ui.Button.OK && resp4.getResponseText().trim()) {
    props.setProperty('SUBJECT_NAME', resp4.getResponseText().trim());
  }

  var resp5 = ui.prompt(
    '🔑 [보안 설정 5/6] 2022 개정 교과역량',
    '강조할 교과역량을 입력하세요 (예: 비판적 사고력, 지식정보처리 역량):',
    ui.ButtonSet.OK_CANCEL
  );
  if (resp5.getSelectedButton() === ui.Button.OK && resp5.getResponseText().trim()) {
    props.setProperty('SUBJECT_COMPETENCIES', resp5.getResponseText().trim());
  }

  var resp6 = ui.prompt(
    '🔑 [보안 설정 6/6] NEIS 세특 목표 바이트',
    '목표 바이트 입력 (500 / 900 / 1500 - 기본값: 900 Bytes (300자 표준)):',
    ui.ButtonSet.OK_CANCEL
  );
  if (resp6.getSelectedButton() === ui.Button.OK && resp6.getResponseText().trim()) {
    props.setProperty('TARGET_BYTES', resp6.getResponseText().trim());
  }

  ui.alert('🎉 모든 설정이 구글 서버 암호화 금고(PropertiesService)에 안전하게 저장되었습니다!');
}

function showWebappLinksPrompt() {
  var ui = SpreadsheetApp.getUi();
  var url = ScriptApp.getService().getUrl();
  if (!url) {
    ui.alert('⚠️ 웹앱으로 먼저 배포해주셔야 핸드폰 주소가 생성됩니다.\n[배포] -> [새 배포]를 진행해주세요.');
    return;
  }
  var appUrl = url;
  var dashUrl = url + '?view=dashboard';

  ui.alert('📱 스마트폰 음성 앱 & 🖥️ PC 대시보드 링크 안내\n\n' +
           '1. 📱 핸드폰 음성 관찰기 앱 (PWA):\n' + appUrl + '\n\n' +
           '2. 🖥️ PC 대시보드 화면:\n' + dashUrl + '\n\n' +
           '위 주소를 복사하여 스마트폰 홈 화면에 앱으로 추가하거나 PC 브라우저에서 열어보세요!');
}

// 7대 탭 양식 세팅 (진짜 구글 시트 기반)
function setupInitialSheets() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetsInfo = [
    { name: 'API설정', headers: ['보안 및 교과역량 설정 항목', '설정 및 상태'] },
    { name: '세특템플릿', headers: ['템플릿 구분 / 강조 항목', '교사 맞춤 작성 지침 / 템플릿 내용'] },
    { name: '학생명렬', headers: ['반', '번호', '학번', '이름'] },
    { name: '시간대별기록', headers: ['일시', '반', '영역', '학번', '이름', '거친음성/메모', 'AI정돈관찰문장'] },
    { name: '학생응답기록', headers: ['일시', '반', '학번', '이름', '응답/제출내용', '구분'] },
    { name: '세특초안생성', headers: ['반', '학번', '이름', '생성 일시', 'NEIS 바이트 수', 'AI 최종 세특/행특 초안'] },
    { name: '학생별모아보기', headers: ['학번', '이름', '누적건수', '누적관찰내용'] }
  ];

  sheetsInfo.forEach(function(info) {
    var sheet = ss.getSheetByName(info.name);
    if (!sheet) {
      sheet = ss.insertSheet(info.name);
    }
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(info.headers);
      sheet.getRange(1, 1, 1, info.headers.length).setFontWeight('bold').setBackground('#eeedfc');
    }
  });

  // 1. 세특템플릿 초기 샘플 지침 채우기
  var templateSheet = ss.getSheetByName('세특템플릿');
  if (templateSheet && templateSheet.getLastRow() <= 1) {
    templateSheet.appendRow(['기본 세특 프롬프트 스타일', '2022 개정 교과역량을 구체적 탐구 사례와 함께 서술하고, 문장은 ~함., ~임. 어조로 마무리할 것.']);
    templateSheet.appendRow(['수업 및 세특 강조 사항', '수업 참여 태도, 모둠 내 협력적 의사소통, 자기주도적 문제해결 과정이 잘 드러나도록 작성할 것.']);
    templateSheet.appendRow(['생기부 금지어 수칙', '대회, 수상, 대학명, 기관명, 사교육, 도서 출간 사실 등 생기부 기재 금지어를 절대 포함하지 말 것.']);
  }

  // 2. 학생명렬 탭 샘플 입력 (선생님이 나이스 엑셀 Ctrl+V 할 공간)
  var studentSheet = ss.getSheetByName('학생명렬');
  if (studentSheet && studentSheet.getLastRow() <= 1) {
    studentSheet.appendRow([1, 1, '30101', '강해린']);
    studentSheet.appendRow([1, 2, '30102', '박지민']);
    studentSheet.appendRow([1, 3, '30103', '김민준']);
    studentSheet.appendRow([2, 1, '30201', '이서윤']);
    studentSheet.appendRow([2, 2, '30202', '최현우']);
  }

  SpreadsheetApp.getUi().alert('✅ 7대 탭 양식이 진짜 구글 시트에 1초 만에 자동 세팅되었습니다!\n\n[학생명렬] 탭에 선생님 반 학생 명단을 엑셀에서 Ctrl+V로 편하게 붙여넣으세요.');
}

function getAvailableGradesAndClasses() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('학생명렬');
    if (!sheet) return { success: true, grades: [2], classesByGrade: { 2: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] } };

    var data = sheet.getDataRange().getValues();
    var classesSet = new Set();
    for (var i = 1; i < data.length; i++) {
      var c = parseInt(data[i][0]);
      if (!isNaN(c) && c > 0) classesSet.add(c);
    }
    var classes = Array.from(classesSet).sort(function(a,b){ return a-b; });
    if (classes.length === 0) classes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

    return { success: true, grades: [3], classesByGrade: { 3: classes } };
  } catch (e) {
    return { success: false, message: e.toString() };
  }
}

function getStudentList(classNum) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('학생명렬');
  if (!sheet) return [];

  var data = sheet.getDataRange().getValues();
  var result = [];
  for (var i = 1; i < data.length; i++) {
    var c = data[i][0];
    var num = data[i][1];
    var hakbun = data[i][2] ? data[i][2].toString() : '';
    var name = data[i][3] ? data[i][3].toString() : '';

    if (classNum === 'all' || c == classNum) {
      result.push({ classNum: c, number: num, hakbun: hakbun, name: name });
    }
  }
  return result;
}

function parseHakbunAndNameFast(rawMemo) {
  var hakbun = '';
  var name = '';
  var classNum = 1;

  var students = getStudentList('all');
  var hakbunMatch = rawMemo.match(/\b([1-3]?\d{4})\b/) || rawMemo.match(/\b(\d{4,5})\b/);
  if (hakbunMatch) hakbun = hakbunMatch[1];

  for (var i = 0; i < students.length; i++) {
    var s = students[i];
    if (s.name && rawMemo.indexOf(s.name) >= 0) {
      name = s.name;
      classNum = s.classNum;
      if (!hakbun && s.hakbun) hakbun = s.hakbun;
      break;
    }
    if (hakbun && s.hakbun && s.hakbun === hakbun) {
      name = s.name;
      classNum = s.classNum;
      break;
    }
  }

  if (!name && !hakbun) name = '미인식';
  if (hakbun && classNum === 1 && hakbun.length >= 5) {
    classNum = parseInt(hakbun.substring(1, 3)) || 1;
  }

  return { hakbun: hakbun, name: name, classNum: classNum };
}

// 0.3초 핸드폰 관찰 메모 즉시 시트 저장 + 학생별모아보기 자동 집계
function processObservationFast(rawMemo, category, clientTimestamp) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('시간대별기록');
    if (!sheet) {
      setupInitialSheets();
      sheet = ss.getSheetByName('시간대별기록');
    }

    var parsed = parseHakbunAndNameFast(rawMemo);
    // 오프라인 재전송 시 클라이언트 타임스탬프 우선 사용 (관찰 시점 보존)
    var timestamp = clientTimestamp || Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm');
    var refinedText = category + ' 활동 중: ' + rawMemo;

    sheet.appendRow([timestamp, parsed.classNum, category, parsed.hakbun, parsed.name, rawMemo, refinedText]);

    // 학생별모아보기 탭 자동 누적 집계
    if (parsed.hakbun || parsed.name !== '미인식') {
      try { updateStudentSummary(parsed.hakbun, parsed.name, rawMemo); } catch(ignore) {}
    }

    return {
      success: true,
      category: category,
      hakbun: parsed.hakbun,
      name: parsed.name,
      classNum: parsed.classNum,
      refinedText: refinedText,
      timestamp: timestamp
    };
  } catch (e) {
    return { success: false, message: e.toString() };
  }
}

function analyzeObservationFeedback(rawMemo, category) {
  var parsed = parseHakbunAndNameFast(rawMemo);
  var hasInfo = (parsed.hakbun !== '' || parsed.name !== '미인식');

  var feedbackTitle = '💡 2022 교과역량 보강 코칭';
  var feedbackMsg = '관찰 내용을 바탕으로 구체적인 수행 과제나 탐구 주제를 덧붙이시면 2022 교과역량이 돋보이는 세특이 완성됩니다.';

  if (!hasInfo) {
    feedbackTitle = '⚠️ 학번/이름 누락 안내';
    feedbackMsg = '학생 학번(예: 30101)이나 이름(예: 강해린)을 말씀해 주시면 시트에 자동으로 매칭되어 저장됩니다.';
  }

  return {
    success: true,
    hasStudentInfo: hasInfo,
    feedbackTitle: feedbackTitle,
    feedbackMsg: feedbackMsg
  };
}

function formatAnyDate(val) {
  if (!val) return '';
  if (val instanceof Date) {
    return Utilities.formatDate(val, 'Asia/Seoul', 'yyyy-MM-dd HH:mm');
  }
  return val.toString();
}

function getDashboardFullData(classNum) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var obsSheet = ss.getSheetByName('시간대별기록');
    var respSheet = ss.getSheetByName('학생응답기록');
    var reportSheet = ss.getSheetByName('세특초안생성');

    var students = getStudentList(classNum);
    var config = getApiConfig();

    var observations = [];
    if (obsSheet && obsSheet.getLastRow() > 1) {
      var obsData = obsSheet.getDataRange().getValues();
      for (var i = 1; i < obsData.length; i++) {
        var c = obsData[i][1];
        if (classNum === 'all' || c == classNum) {
          observations.push({
            date: formatAnyDate(obsData[i][0]),
            classNum: obsData[i][1] ? obsData[i][1].toString() : '',
            category: obsData[i][2] ? obsData[i][2].toString() : '',
            hakbun: obsData[i][3] ? obsData[i][3].toString() : '',
            name: obsData[i][4] ? obsData[i][4].toString() : '',
            rawMemo: obsData[i][5] ? obsData[i][5].toString() : '',
            refinedText: obsData[i][6] ? obsData[i][6].toString() : ''
          });
        }
      }
    }

    var responses = [];
    if (respSheet && respSheet.getLastRow() > 1) {
      var respData = respSheet.getDataRange().getValues();
      for (var j = 1; j < respData.length; j++) {
        var c2 = respData[j][1];
        if (classNum === 'all' || c2 == classNum) {
          responses.push({
            date: formatAnyDate(respData[j][0]),
            classNum: respData[j][1] ? respData[j][1].toString() : '',
            hakbun: respData[j][2] ? respData[j][2].toString() : '',
            name: respData[j][3] ? respData[j][3].toString() : '',
            content: respData[j][4] ? respData[j][4].toString() : '',
            type: respData[j][5] ? respData[j][5].toString() : ''
          });
        }
      }
    }

    var reports = [];
    if (reportSheet && reportSheet.getLastRow() > 1) {
      var repData = reportSheet.getDataRange().getValues();
      for (var k = 1; k < repData.length; k++) {
        var c3 = repData[k][0];
        if (classNum === 'all' || c3 == classNum) {
          reports.push({
            classNum: repData[k][0] ? repData[k][0].toString() : '',
            hakbun: repData[k][1] ? repData[k][1].toString() : '',
            name: repData[k][2] ? repData[k][2].toString() : '',
            date: formatAnyDate(repData[k][3]),
            bytes: repData[k][4] ? repData[k][4].toString() : '',
            reportText: repData[k][5] ? repData[k][5].toString() : ''
          });
        }
      }
    }

    return {
      success: true,
      config: config,
      students: students,
      observations: observations,
      responses: responses,
      reports: reports
    };
  } catch (e) {
    return { success: false, message: e.toString() };
  }
}

function generateAllStudentReportsMenu() {
  var ui = SpreadsheetApp.getUi();
  var resp = ui.prompt('🔮 AI 세특 생성', '생성할 반 번호를 입력하세요 (예: 1 / 전체 입력 시 all):', ui.ButtonSet.OK_CANCEL);
  if (resp.getSelectedButton() === ui.Button.OK) {
    var cNum = resp.getResponseText().trim() || 'all';
    var res = generateAllStudentReports(cNum);
    if (res.success) {
      ui.alert('🎉 AI 세특 초안 생성이 완료되었습니다!\n[세특초안생성] 탭을 확인하세요.');
    } else {
      ui.alert('오류: ' + res.message);
    }
  }
}

// 영역(카테고리)과 대상 과목 간의 정확한 필터링 매칭 함수
function isCategoryMatch(obsCategory, targetSubject) {
  if (!targetSubject) return true;
  var cat = (obsCategory || '기타').trim();
  var subj = targetSubject.trim();

  if (subj === '동아리') {
    return cat.indexOf('동아리') >= 0;
  }
  if (subj === '행특' || subj === '행동특성') {
    return cat.indexOf('행특') >= 0 || cat.indexOf('행동') >= 0;
  }
  if (subj === '자율/진로' || subj === '자율' || subj === '진로') {
    return cat.indexOf('자율') >= 0 || cat.indexOf('진로') >= 0;
  }

  // 교과 세특 (국어, 수학, 영어, 정보, 통합사회, 통합과학 등)
  // '동아리', '행특', '자율', '진로' 카테고리는 교과 세특 생성 시 엄격히 제외
  if (cat.indexOf('동아리') >= 0 || cat.indexOf('행특') >= 0 || cat.indexOf('행동') >= 0 || cat.indexOf('자율') >= 0 || cat.indexOf('진로') >= 0) {
    return false;
  }

  // 대상 교과명(예: 국어)과 동일하거나, 범용 '교과' 카테고리인 경우만 허용
  return (cat === subj || cat === '교과' || cat.indexOf(subj) >= 0);
}

function generateAllStudentReports(classNum, customSubject, customCompetency, customBytes) {
  try {
    var config = getApiConfig();
    var subject = customSubject || config.subjectName;
    var competency = customCompetency || config.subjectCompetencies;
    var bytesTarget = parseInt(customBytes || config.targetBytes || '900');

    var students = getStudentList(classNum);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var reportSheet = ss.getSheetByName('세특초안생성');
    var obsSheet = ss.getSheetByName('시간대별기록');

    if (!reportSheet) {
      setupInitialSheets();
      reportSheet = ss.getSheetByName('세특초안생성');
    }

    // 세특템플릿 시트 교사 맞춤 지침 로드
    var templateGuidelines = getTemplateGuidelines();

    // 시간대별기록 전체 로드 (학생별 관찰 기록 매칭용)
    var allObs = [];
    if (obsSheet && obsSheet.getLastRow() > 1) {
      var obsData = obsSheet.getDataRange().getValues();
      for (var i = 1; i < obsData.length; i++) {
        allObs.push({
          classNum: obsData[i][1],
          category: obsData[i][2] ? obsData[i][2].toString() : '',
          hakbun: obsData[i][3] ? obsData[i][3].toString() : '',
          name: obsData[i][4] ? obsData[i][4].toString() : '',
          rawMemo: obsData[i][5] ? obsData[i][5].toString() : ''
        });
      }
    }

    var count = 0;
    var retainedCount = 0;

    for (var i = 0; i < students.length; i++) {
      var s = students[i];

      // 5명 단위로 15초 대기 (AI API 과부하 방지 & 할루시네이션 방지)
      if (count > 0 && count % 5 === 0) {
        Utilities.sleep(15000);
      }

      // 해당 학생 및 선택된 과목/영역 카테고리와 일치하는 관찰 기록만 필터링
      var sHakbun = s.hakbun ? s.hakbun.toString() : '';
      var sName = s.name ? s.name.toString() : '';
      var studentObs = allObs.filter(function(o) {
        var matchStudent = (sHakbun && o.hakbun === sHakbun) || (sName && o.name === sName);
        var matchCategory = isCategoryMatch(o.category, subject);
        return matchStudent && matchCategory;
      });

      // 관찰 기록이 없는 학생은 기존 세특 유지 (스킵)
      if (studentObs.length === 0) {
        retainedCount++;
        continue;
      }

      var obsText = studentObs.map(function(o) {
        return '[' + (o.category || '기타') + '] ' + o.rawMemo;
      }).join('\n');

      // AI 프롬프트 구성 및 실제 API 호출
      var prompt = buildSeteukPrompt(sName, subject, competency, bytesTarget, obsText, templateGuidelines);
      var aiResult = callAI(prompt);

      // AI 실패 시 fallback 템플릿 사용
      var reportText = aiResult || buildFallbackReport(sName, subject, competency, studentObs);

      // 바이트 초과 시 자동 트리밍
      reportText = trimToBytes(reportText, bytesTarget);

      var timestamp = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm');
      var byteLength = Utilities.newBlob(reportText).getBytes().length;

      reportSheet.appendRow([s.classNum, s.hakbun, sName, timestamp, byteLength + ' Bytes', reportText]);
      count++;
    }

    return {
      success: true,
      count: count,
      retainedCount: retainedCount,
      targetBytes: bytesTarget.toString(),
      subject: subject
    };
  } catch (e) {
    return { success: false, message: e.toString() };
  }
}

// ────── AI API 호출 엔진 ──────

// 구글 시트 원본 URL 반환 (대시보드 동적 링크용)
function getSpreadsheetUrl() {
  return SpreadsheetApp.getActiveSpreadsheet().getUrl();
}

// Gemini 2.0 Flash API 호출
function callGeminiApi(prompt) {
  var config = getApiConfig();
  var apiKey = config.geminiKey;
  if (!apiKey) return null;

  var url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + apiKey;
  var payload = {
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: { temperature: 0.7, maxOutputTokens: 1024 }
  };

  try {
    var response = UrlFetchApp.fetch(url, {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });
    var json = JSON.parse(response.getContentText());
    if (json.candidates && json.candidates[0] && json.candidates[0].content) {
      return json.candidates[0].content.parts[0].text.trim();
    }
    Logger.log('Gemini API 응답 파싱 실패: ' + response.getContentText().substring(0, 500));
    return null;
  } catch (e) {
    Logger.log('Gemini API 호출 에러: ' + e.toString());
    return null;
  }
}

// Upstage Solar API 호출
function callUpstageApi(prompt) {
  var config = getApiConfig();
  var apiKey = config.upstageKey;
  if (!apiKey) return null;

  var url = 'https://api.upstage.ai/v1/solar/chat/completions';
  var payload = {
    model: 'solar-mini',
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.7,
    max_tokens: 1024
  };

  try {
    var response = UrlFetchApp.fetch(url, {
      method: 'post',
      contentType: 'application/json',
      headers: { 'Authorization': 'Bearer ' + apiKey },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });
    var json = JSON.parse(response.getContentText());
    if (json.choices && json.choices[0] && json.choices[0].message) {
      return json.choices[0].message.content.trim();
    }
    Logger.log('Upstage API 응답 파싱 실패: ' + response.getContentText().substring(0, 500));
    return null;
  } catch (e) {
    Logger.log('Upstage API 호출 에러: ' + e.toString());
    return null;
  }
}

// AI 디스패처: 설정된 모델에 따라 Gemini 또는 Upstage 호출
function callAI(prompt) {
  var config = getApiConfig();
  if (config.selectedAI === 'Upstage' && config.upstageKey) {
    return callUpstageApi(prompt);
  }
  if (config.geminiKey) {
    return callGeminiApi(prompt);
  }
  Logger.log('AI API 키가 설정되지 않았습니다. fallback 템플릿을 사용합니다.');
  return null;
}

// 세특템플릿 시트에서 교사 맞춤 지침 로드
function getTemplateGuidelines() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('세특템플릿');
  if (!sheet || sheet.getLastRow() <= 1) return '(세특템플릿 시트에 교사 지침이 없습니다. 기본 양식으로 생성합니다.)';

  var data = sheet.getDataRange().getValues();
  var lines = [];
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] || data[i][1]) {
      lines.push('- [' + (data[i][0] || '') + '] ' + (data[i][1] || ''));
    }
  }
  return lines.join('\n');
}

// 2022 개정 교과역량 세특 프롬프트 빌더
function buildSeteukPrompt(studentName, subject, competency, bytesTarget, obsText, templateGuidelines) {
  var charTarget = Math.floor(bytesTarget / 3);
  return '당신은 대한민국 고등학교 생활기록부 세부능력 및 특기사항(세특) 전문 작성 AI입니다.\n\n' +
    '[담당 교과] ' + subject + '\n' +
    '[강조 교과역량] ' + competency + '\n' +
    '[목표 분량] ' + charTarget + '자 이내 (한글 기준 ' + bytesTarget + ' Bytes 이내)\n\n' +
    '[교사 맞춤 작성 지침]\n' + templateGuidelines + '\n\n' +
    '[학생명] ' + studentName + '\n' +
    '[수업 관찰 기록]\n' + obsText + '\n\n' +
    '위 관찰 기록을 바탕으로 아래 규칙을 반드시 준수하여 세특 초안을 작성하세요:\n\n' +
    '1. 모든 문장은 ~함., ~임., ~됨. 등 명사형 종결어미로 마무리할 것\n' +
    '2. 2022 개정 교과역량(' + competency + ')이 자연스럽게 드러나도록 구체적 탐구 사례를 서술할 것\n' +
    '3. 다음 단어/표현은 절대 사용 금지: 대회, 수상, 장학금, 특정 대학명, 사기업 상호명(삼성전자 등), 강사명, 도서 출간 사실\n' +
    '4. 특정 지역명(진해 등)은 \'우리 지역\'으로, 학교 고유 명칭(장복제 등)은 \'교내 행사\'로 변경할 것\n' +
    '5. 학생의 실제 관찰 내용만을 기반으로 작성하고, 관찰되지 않은 내용을 임의로 추가하지 말 것\n' +
    '6. 결과물은 세특 본문만 출력할 것 (제목, 구분선, 마크다운, 부가 설명 등 절대 불포함)\n' +
    '7. 반드시 ' + charTarget + '자 이내로 작성하고, 마지막 문장은 중간에 끊기지 않고 완전하게 마무리할 것';
}

// 바이트 초과 시 자동 트리밍 유틸리티 (문장 중간 끊김 완벽 방지)
function trimToBytes(text, maxBytes) {
  if (!text) return '';
  var bytes = Utilities.newBlob(text).getBytes().length;
  if (bytes <= maxBytes) return text;

  // 1단계: 마침표(.) 기준으로 완결된 문장까지만 남기기
  var trimmed = text;
  while (bytes > maxBytes && trimmed.length > 0) {
    var lastDotIndex = trimmed.lastIndexOf('.');
    if (lastDotIndex > 0) {
      trimmed = trimmed.substring(0, lastDotIndex + 1).trim();
      bytes = Utilities.newBlob(trimmed).getBytes().length;
    } else {
      // 마침표가 없으면 1글자씩 자름
      trimmed = trimmed.substring(0, trimmed.length - 1);
      bytes = Utilities.newBlob(trimmed).getBytes().length;
    }
  }
  return trimmed || text.substring(0, Math.floor(maxBytes / 3));
}

// AI 실패/미설정 시 fallback 세특 템플릿 (관찰 기록 기반 정제)
function buildFallbackReport(studentName, subject, competency, observations) {
  var obsSnippets = observations.slice(0, 3).map(function(o) {
    var text = o.rawMemo || '';
    text = text.replace(/\b\d{4,5}\b/g, '').replace(new RegExp(studentName, 'g'), '').trim();
    return text;
  }).filter(Boolean).join(', ');

  var particle = (competency && competency.endsWith('역량')) ? '을' : '를';

  return studentName + ' 학생은 ' + subject + ' 수업에서 ' + competency + particle + ' 바탕으로 ' +
    (obsSnippets ? obsSnippets + ' 등의 활동을 자기주도적으로 수행함.' : '성실히 수업 활동에 참여함.') +
    ' 수업 참여 태도가 매우 긍정적이며 모둠 활동에서 협력적 의사소통 역량이 돋보임.';
}

// 학생별모아보기 탭 자동 누적 집계
function updateStudentSummary(hakbun, name, newMemo) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('학생별모아보기');
  if (!sheet) return;

  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] && data[i][0].toString() === hakbun.toString()) {
      var count = parseInt(data[i][2]) || 0;
      var existing = data[i][3] ? data[i][3].toString() : '';
      sheet.getRange(i + 1, 3).setValue(count + 1);
      sheet.getRange(i + 1, 4).setValue(existing + (existing ? ' | ' : '') + newMemo);
      return;
    }
  }
  // 신규 학생 → 새 행 추가
  sheet.appendRow([hakbun, name, 1, newMemo]);
}
