/**
 * ═══════════════════════════════════════════════════════════════════
 *  📱 모바일 생생세특 (Live Seteuk) v2.1 — 백엔드 엔진
 * ═══════════════════════════════════════════════════════════════════
 *
 *  v2.0 → v2.1 수정 내역. 각 항목의 [FIX #n]은
 *  「모바일생생세특_코드검토보고서.md」의 번호와 1:1로 대응합니다.
 *
 *  🔴 치명적
 *   #1  동명이인 오매칭        학번 우선 → 이름(긴 이름 우선) → 추정 / 모호하면 확정하지 않음
 *   #2  연도 오탐지 가드 무효   원문에서 연도·날짜를 먼저 제거한 뒤 학번 추출
 *   #3  6분 실행시간 초과      generateReportsBatch() 배치 + 이어하기, 대기 15초→3초
 *   #4  세특 중복 누적         학번 인덱스로 기존 행 갱신, 진짜 Diff(신규 관찰 있을 때만)
 *   #6  웹앱에서 메모 유실      ensureSheets_() (UI 없음) / setupInitialSheets() (메뉴용) 분리
 *
 *  🟠 중요
 *   #8  시트 전체 스캔 폭주     getStudentListCached() — CacheService 6시간
 *   #10 세특 분량 35~59%       trimToBytes() 문장 + 어절 채움 + 이진탐색
 *   #11 조사 오류 "해결력를"    josaEulReul_() 받침 판정
 *   #12 조용한 fallback        fallbackCount 반환 + [생성로그] 탭 기록
 *   #13 집계 락/빈 학번        LockService + 이름 키 대체 + 셀 5만자 방어
 *
 *  🟡 개선 / 🔵 구조·보안
 *   #16 목표 바이트 NaN        parseInt 방어
 *   #17 '진로와 직업' 오매칭    영역(domain)과 과목(subject) 분리
 *   #18 미인식 기록 방치        getUnmatchedObservations() / reassignObservation()
 *   #22 접근 제어 없음          ACCESS_PIN + assertPin_()
 *   #23 실명 외부 전송          AI 전송 전 ○○ 가명화 → 응답에서 복원
 *   #25 미사용 탭              학생응답기록 구글폼 연동, 학생별모아보기 재계산 함수
 *   #27 학년 하드코딩/시각      학번 첫 자리로 학년 추출, 서버 시각 병기, doGet 방어
 *
 *  ✨ 신규
 *   반 고정 모드              수업 전 반을 고정하면 그 반 안에서만 매칭 → 동명이인 원천 차단
 *   기록 수정/삭제            기록ID 기반 (앱 '오늘 기록')
 * ═══════════════════════════════════════════════════════════════════
 */

// ═══════════════════════════════════════════════════════════════════
//  0. 상수
// ═══════════════════════════════════════════════════════════════════

var VERSION = 'v2.1';
var TZ = 'Asia/Seoul';

/**
 * ═══════════════════════════════════════════════════════════════════
 *  ⭐ 배포 모드 — 이 한 줄만 바꾸면 개인용/배포용이 전환됩니다.
 * ═══════════════════════════════════════════════════════════════════
 *
 *   'PERSONAL' … 선생님 본인용 (jinhae_ai_seteuk_teacher_pack)
 *                · 실제 학생 명렬 사용, 샘플 데이터를 넣지 않음
 *                · 설정이 이미 되어 있다고 가정하고 바로 사용
 *                · 텔레그램 알림 등 개인 편의 기능 노출
 *
 *   'SHARED'   … 다른 선생님 배포용 (jinhae_ai_seteuk_teacher_pack_clean)
 *                · 실제 학생 이름이 절대 들어가지 않음 (가상 명단만 시드)
 *                · 최초 실행 시 설정 마법사를 강제 안내
 *                · API 키 발급 방법·PIN 설정을 단계별로 안내
 *
 *  ⚠️ 두 버전은 이 상수 하나만 다릅니다. 로직을 따로 관리하지 마세요.
 *     (v2.0에서 두 폴더의 파일이 바이트 단위로 완전히 동일했던 것은,
 *      복사본이 갈라지지 않은 것이 아니라 분기 자체가 없었기 때문입니다.)
 *
 *  🔐 API 키·PIN·텔레그램 토큰은 코드가 아니라 PropertiesService
 *     (구글 서버 암호화 저장소)에 들어갑니다. 따라서 이 파일을 그대로
 *     배포해도 키가 유출되지 않습니다. 배포 시 주의할 것은 코드가 아니라
 *     ① 학생 명렬 TSV/시트  ② 이미 쌓인 관찰 기록  두 가지입니다.
 * ═══════════════════════════════════════════════════════════════════
 */
var DEPLOY_MODE = 'PERSONAL';

function isShared_()   { return DEPLOY_MODE === 'SHARED'; }
function isPersonal_() { return DEPLOY_MODE !== 'SHARED'; }

var SHEET = {
  CONFIG:   'API설정',
  TEMPLATE: '세특템플릿',
  ROSTER:   '학생명렬',
  OBS:      '시간대별기록',
  RESP:     '학생응답기록',
  REPORT:   '세특초안생성',
  SUMMARY:  '학생별모아보기',
  LOG:      '생성로그'
};

// [FIX #27] 기록ID·확신도·서버시각 컬럼을 뒤에 추가 (기존 데이터 위치 불변)
var HEADERS = {};
HEADERS[SHEET.CONFIG]   = ['보안 및 교과역량 설정 항목', '설정 및 상태'];
HEADERS[SHEET.TEMPLATE] = ['템플릿 구분 / 강조 항목', '교사 맞춤 작성 지침 / 템플릿 내용'];
HEADERS[SHEET.ROSTER]   = ['반', '번호', '학번', '이름'];
HEADERS[SHEET.OBS]      = ['일시', '반', '영역', '학번', '이름', '거친음성/메모', 'AI정돈관찰문장', '기록ID', '매칭확신도', '서버수신시각'];
HEADERS[SHEET.RESP]     = ['일시', '반', '학번', '이름', '응답/제출내용', '구분'];
HEADERS[SHEET.REPORT]   = ['반', '학번', '이름', '생성 일시', 'NEIS 바이트 수', 'AI 최종 세특/행특 초안', '생성 엔진', '반영 관찰 최종시각'];
HEADERS[SHEET.SUMMARY]  = ['학번', '이름', '누적건수', '누적관찰내용'];
HEADERS[SHEET.LOG]      = ['일시', '구분', '대상', '내용'];

// 시간대별기록 컬럼 인덱스
var OBS_COL = { DATE:0, CLASS:1, CAT:2, HAKBUN:3, NAME:4, MEMO:5, REFINED:6, ID:7, CONF:8, SRVTS:9 };
var REP_COL = { CLASS:0, HAKBUN:1, NAME:2, DATE:3, BYTES:4, TEXT:5, ENGINE:6, OBSAT:7 };

var ROSTER_CACHE_KEY = 'LS_ROSTER_ALL_v21';
var ROSTER_CACHE_SEC = 21600;          // 6시간

// [FIX #3] 배치 파라미터
var BATCH_MAX_STUDENTS = 20;
var BATCH_TIME_LIMIT_MS = 4 * 60 * 1000;   // 6분 한도 대비 4분에서 안전 중단
var AI_PAUSE_EVERY = 5;
var AI_PAUSE_MS = 3000;                    // [FIX #3] 15초 → 3초 (레이트리밋 회피면 충분)

var SUMMARY_CELL_MAX = 45000;              // [FIX #13] 시트 셀 5만자 한도 방어
var DASHBOARD_MAX_ROWS = 3000;             // [FIX #27] 대시보드 1회 전송 상한

var NAME_TOKEN = '○○';                     // [FIX #23] AI 전송용 가명 토큰


// ═══════════════════════════════════════════════════════════════════
//  1. 진입점 / 메뉴
// ═══════════════════════════════════════════════════════════════════

function doGet(e) {
  // [FIX #27] e 또는 e.parameter 가 없을 때 예외 방지
  var view = (e && e.parameter && e.parameter.view) ? String(e.parameter.view) : '';

  if (view === 'dashboard') {
    return HtmlService.createHtmlOutputFromFile('dashboard')
      .setTitle('모바일 생생세특 ' + VERSION + ' - AI 세특 대시보드')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
      .addMetaTag('viewport', 'width=device-width, initial-scale=1');
  }
  return HtmlService.createHtmlOutputFromFile('app')
    .setTitle('모바일 생생세특 ' + VERSION + ' - 현장 관찰 AI 기록기')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no');
}

function onOpen() {
  SpreadsheetApp.getUi().createMenu('📱 모바일 생생세특 ' + VERSION)
    .addItem('1. 🔑 API 키 및 교과역량/바이트 설정', 'setApiKeysPrompt')
    .addItem('2. 📋 시트 자동 양식 세팅', 'setupInitialSheets')
    .addItem('3. 📱 앱 & 🖥️ 대시보드 링크 안내', 'showWebappLinksPrompt')
    .addSeparator()
    .addItem('4. 🔮 선택된 반 AI 세특 초안 생성', 'generateAllStudentReportsMenu')
    .addSeparator()
    .addItem('5. 🔄 학생명렬 캐시 새로고침', 'refreshRosterCacheMenu')
    .addItem('6. 🔒 접근 PIN 설정 / 해제', 'setAccessPinPrompt')
    .addItem('7. 📥 구글 폼 응답 자동수집 연결', 'installFormTriggerPrompt')
    .addItem('8. 🧮 학생별모아보기 다시 계산', 'rebuildStudentSummaryMenu')
    .addSeparator()
    .addItem('9. 💬 텔레그램 완료 알림 설정', 'setTelegramPrompt')
    .addItem('10. 📨 텔레그램 알림 테스트', 'testTelegramMenu')
    .addToUi();
}


// ═══════════════════════════════════════════════════════════════════
//  2. 설정 (Script Properties)
// ═══════════════════════════════════════════════════════════════════

function getApiConfig() {
  var props = PropertiesService.getScriptProperties();
  return {
    upstageKey:           props.getProperty('UPSTAGE_API_KEY') || '',
    geminiKey:            props.getProperty('GEMINI_API_KEY') || '',
    selectedAI:           props.getProperty('SELECTED_AI') || 'Gemini',
    // [FIX #17] 영역(domain)과 세부 과목명(subjectName)을 분리 저장
    domain:               props.getProperty('DOMAIN') || '교과',
    subjectName:          props.getProperty('SUBJECT_NAME') || '국어',
    subjectCompetencies:  props.getProperty('SUBJECT_COMPETENCIES') || '비판적·창의적 사고 역량, 지식정보처리 역량',
    targetBytes:          props.getProperty('TARGET_BYTES') || '900',
    // [FIX #12] 모델명 하드코딩 제거 — 단종되면 속성만 바꾸면 됨
    geminiModel:          props.getProperty('GEMINI_MODEL') || 'gemini-2.0-flash',
    upstageModel:         props.getProperty('UPSTAGE_MODEL') || 'solar-mini',
    // [FIX #23] 최종 초안에 실명을 넣을지 여부 (AI 전송 시에는 항상 가명 처리)
    nameInReport:         props.getProperty('NAME_IN_REPORT') || 'Y',
    pinRequired:          !!(props.getProperty('ACCESS_PIN') || '')
  };
}

// [FIX #17] domain 인자 추가 — 대시보드가 영역/과목을 따로 저장
function saveDashboardConfig(domain, subject, competency, targetBytes) {
  try {
    assertPin_();
    var props = PropertiesService.getScriptProperties();
    if (domain)      props.setProperty('DOMAIN', String(domain));
    if (subject)     props.setProperty('SUBJECT_NAME', String(subject));
    if (competency)  props.setProperty('SUBJECT_COMPETENCIES', String(competency));

    // [FIX #16] 목표 바이트 NaN / 비정상값 방어
    var tb = parseInt(targetBytes, 10);
    if (tb && tb >= 100 && tb <= 3000) props.setProperty('TARGET_BYTES', String(tb));

    syncConfigSheet_();
    return { success: true };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  }
}

function syncConfigSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET.CONFIG);
  if (!sheet) return;

  var c = getApiConfig();
  var map = {
    '생성 영역':                c.domain,
    '담당 교과명':              c.subjectName,
    '2022 개정 교과역량':        c.subjectCompetencies,
    'NEIS 세특 목표 바이트':      c.targetBytes,
    'Upstage API Key 설정 여부': c.upstageKey ? '✅ 설정됨' : '❌ 미설정',
    'Gemini API Key 설정 여부':  c.geminiKey ? '✅ 설정됨' : '❌ 미설정',
    '기본 AI 모델':             c.selectedAI + ' (' + (c.selectedAI === 'Upstage' ? c.upstageModel : c.geminiModel) + ')',
    '접근 PIN':                c.pinRequired ? '🔒 설정됨' : '⚠️ 미설정 (URL을 아는 사람은 누구나 열람 가능)'
  };

  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    var key = data[i][0] ? String(data[i][0]).trim() : '';
    if (map.hasOwnProperty(key)) {
      sheet.getRange(i + 1, 2).setValue(map[key]);
      delete map[key];
    }
  }
  for (var k in map) if (map.hasOwnProperty(k)) sheet.appendRow([k, map[k]]);
}

function setApiKeysPrompt() {
  var ui = SpreadsheetApp.getUi();
  var props = PropertiesService.getScriptProperties();

  var steps = [
    ['UPSTAGE_API_KEY',      '🔑 [1/6] Upstage API Key',        'Upstage API Key를 입력하세요 (없으면 그대로 확인):'],
    ['GEMINI_API_KEY',       '🔑 [2/6] Google Gemini API Key',   'Google Gemini API Key를 입력하세요 (추천):'],
    ['SELECTED_AI',          '🔑 [3/6] 기본 AI 모델',            'Gemini 또는 Upstage 입력 (기본값: Gemini):'],
    ['SUBJECT_NAME',         '🔑 [4/6] 담당 교과명',             '담당 교과명 (예: 국어, 화법과 작문, 미적분):'],
    ['SUBJECT_COMPETENCIES', '🔑 [5/6] 2022 개정 교과역량',       '강조할 교과역량 (예: 비판적 사고력, 지식정보처리 역량):'],
    ['TARGET_BYTES',         '🔑 [6/6] NEIS 세특 목표 바이트',     '목표 바이트 (500 / 900 / 1500 — 기본값 900):']
  ];

  for (var i = 0; i < steps.length; i++) {
    var r = ui.prompt(steps[i][1], steps[i][2], ui.ButtonSet.OK_CANCEL);
    if (r.getSelectedButton() !== ui.Button.OK) break;
    var v = r.getResponseText().trim();
    if (!v) continue;
    // [FIX #16] 바이트만 숫자 검증
    if (steps[i][0] === 'TARGET_BYTES') {
      var tb = parseInt(v, 10);
      if (!tb || tb < 100 || tb > 3000) { ui.alert('⚠️ 목표 바이트는 100~3000 사이 숫자여야 합니다. 이 항목은 건너뜁니다.'); continue; }
      v = String(tb);
    }
    props.setProperty(steps[i][0], v);
  }

  ensureSheets_();
  syncConfigSheet_();
  ui.alert('🎉 설정이 저장되었습니다.\n\n' +
           (getApiConfig().pinRequired ? '' : '⚠️ 접근 PIN이 아직 설정되지 않았습니다.\n메뉴 [6. 🔒 접근 PIN 설정]에서 꼭 설정해 주세요.\n웹앱 주소를 아는 사람은 누구나 학생 명렬과 관찰 기록을 볼 수 있습니다.'));
}

function showWebappLinksPrompt() {
  var ui = SpreadsheetApp.getUi();
  var url = ScriptApp.getService().getUrl();
  if (!url) {
    ui.alert('⚠️ 먼저 웹앱으로 배포해 주세요.\n[배포] → [새 배포] → 유형 [웹 앱]\n\n' +
             '• 실행 사용자: 나(배포자)\n' +
             '• 액세스 권한: 학교 도메인 사용자 또는 본인만 (전체 공개는 권장하지 않습니다)');
    return;
  }
  ui.alert('📱 스마트폰 앱 & 🖥️ PC 대시보드\n\n' +
           '1. 📱 음성 관찰기:\n' + url + '\n\n' +
           '2. 🖥️ PC 대시보드:\n' + url + '?view=dashboard\n\n' +
           '⚠️ 이 주소를 아는 사람은 학생 개인정보에 접근할 수 있습니다.\n' +
           '   메뉴 [6. 🔒 접근 PIN 설정]을 반드시 함께 사용하세요.');
}


// ═══════════════════════════════════════════════════════════════════
//  3. [FIX #22] 접근 PIN
// ═══════════════════════════════════════════════════════════════════

function getAccessPin_() {
  return PropertiesService.getScriptProperties().getProperty('ACCESS_PIN') || '';
}

/** 클라이언트가 최초에 호출 — PIN이 필요한지 여부만 알려줌 */
function isPinRequired() {
  return { required: !!getAccessPin_(), version: VERSION };
}

/** PIN 검증 성공 시 사용자 캐시에 통과 표시를 남김 (6시간) */
function verifyPin(pin) {
  var p = getAccessPin_();
  if (!p) return { success: true };
  if (String(pin || '').trim() === p) {
    try { CacheService.getUserCache().put('LS_PIN_OK', '1', 21600); } catch (e) {}
    return { success: true };
  }
  return { success: false, message: 'PIN이 올바르지 않습니다.' };
}

/** 모든 데이터 함수 앞단에서 호출 */
function assertPin_() {
  if (!getAccessPin_()) return;
  var ok = '';
  try { ok = CacheService.getUserCache().get('LS_PIN_OK'); } catch (e) {}
  if (ok !== '1') throw new Error('PIN_REQUIRED');
}

function setAccessPinPrompt() {
  var ui = SpreadsheetApp.getUi();
  var props = PropertiesService.getScriptProperties();
  var r = ui.prompt('🔒 접근 PIN 설정',
                    '웹앱 접속에 필요한 PIN(4~8자리)을 입력하세요.\n비우고 확인하면 PIN이 해제됩니다.',
                    ui.ButtonSet.OK_CANCEL);
  if (r.getSelectedButton() !== ui.Button.OK) return;

  var v = r.getResponseText().trim();
  if (!v) {
    props.deleteProperty('ACCESS_PIN');
    ui.alert('⚠️ 접근 PIN이 해제되었습니다. 주소를 아는 누구나 접근할 수 있습니다.');
  } else if (v.length < 4 || v.length > 8) {
    ui.alert('PIN은 4~8자리여야 합니다.');
    return;
  } else {
    props.setProperty('ACCESS_PIN', v);
    ui.alert('🔒 접근 PIN이 설정되었습니다.\n앱과 대시보드를 처음 열 때 한 번 입력하면 6시간 유지됩니다.');
  }
  syncConfigSheet_();
}


// ═══════════════════════════════════════════════════════════════════
//  4. [FIX #6] 시트 생성 — UI 없는 코어 / 메뉴용 래퍼 분리
// ═══════════════════════════════════════════════════════════════════

/**
 * [FIX #6] UI를 전혀 쓰지 않는 시트 보장 함수.
 * 웹앱(google.script.run) 컨텍스트에서는 SpreadsheetApp.getUi()가
 * 예외를 던지므로, 서버 로직에서는 반드시 이 함수만 호출해야 합니다.
 */
function ensureSheets_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  for (var name in HEADERS) {
    if (!HEADERS.hasOwnProperty(name)) continue;
    var sheet = ss.getSheetByName(name);
    if (!sheet) sheet = ss.insertSheet(name);

    var want = HEADERS[name];
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(want);
      sheet.getRange(1, 1, 1, want.length).setFontWeight('bold').setBackground('#eeedfc');
      sheet.setFrozenRows(1);
    } else {
      // 기존 시트에 새로 추가된 컬럼만 뒤에 덧붙임 (기존 데이터 위치 불변)
      var have = sheet.getRange(1, 1, 1, Math.max(sheet.getLastColumn(), 1)).getValues()[0];
      if (have.length < want.length) {
        var add = want.slice(have.length);
        sheet.getRange(1, have.length + 1, 1, add.length)
             .setValues([add]).setFontWeight('bold').setBackground('#eeedfc');
      }
    }
  }

  seedDefaults_(ss);
  return ss;
}

function seedDefaults_(ss) {
  var cfg = ss.getSheetByName(SHEET.CONFIG);
  if (cfg && cfg.getLastRow() <= 1) syncConfigSheet_();

  var tpl = ss.getSheetByName(SHEET.TEMPLATE);
  if (tpl && tpl.getLastRow() <= 1) {
    tpl.appendRow(['기본 세특 프롬프트 스타일', '2022 개정 교과역량을 구체적 탐구 사례와 함께 서술하고, 문장은 ~함., ~임. 어조로 마무리할 것.']);
    tpl.appendRow(['수업 및 세특 강조 사항', '수업 참여 태도, 모둠 내 협력적 의사소통, 자기주도적 문제해결 과정이 잘 드러나도록 작성할 것.']);
    tpl.appendRow(['생기부 금지어 수칙', '대회, 수상, 대학명, 기관명, 사교육, 도서 출간 사실 등 생기부 기재 금지어를 절대 포함하지 말 것.']);
  }

  var ros = ss.getSheetByName(SHEET.ROSTER);
  if (ros && ros.getLastRow() <= 1) {
    if (isShared_()) {
      // 배포용: 누가 봐도 예시임이 분명한 가상 이름만. 실제 학생 이름 금지.
      ros.appendRow([1, 1, '10101', '예시학생가']);
      ros.appendRow([1, 2, '10102', '예시학생나']);
      ros.appendRow([2, 1, '10201', '예시학생다']);
      ros.getRange(2, 1, 3, 4).setBackground('#fff7ed').setFontColor('#9a3412');
      ros.getRange(5, 1).setValue('↑ 위 3줄은 예시입니다. 삭제하고 실제 명단을 붙여넣으세요.')
         .setFontColor('#9a3412').setFontWeight('bold');
    }
    // 개인용(PERSONAL)은 아무것도 넣지 않습니다 — 실제 명렬을 바로 붙여넣으면 됩니다.
  }
}


// ═══════════════════════════════════════════════════════════════════
//  4-b. 최초 설정 점검 (배포용 온보딩)
// ═══════════════════════════════════════════════════════════════════

/** 대시보드/앱이 시작할 때 호출 — 무엇이 아직 안 되어 있는지 알려줍니다 */
function getSetupStatus() {
  try {
    var cfg = getApiConfig();
    var roster = getStudentListCached();
    var realRoster = roster.filter(function (s) { return s.name && s.name.indexOf('예시학생') !== 0; });

    var items = [
      { key: 'apiKey', label: 'AI API 키 등록',
        done: !!(cfg.geminiKey || cfg.upstageKey),
        help: '시트 메뉴 [1. 🔑 API 키 설정] → Gemini 키는 aistudio.google.com/apikey 에서 무료로 발급받을 수 있습니다.' },
      { key: 'roster', label: '학생 명렬 입력',
        done: realRoster.length > 0,
        help: '[학생명렬] 탭에 나이스/엑셀 명단을 붙여넣으세요. 컬럼 순서: 반 · 번호 · 학번 · 이름' },
      { key: 'subject', label: '담당 교과·교과역량 설정',
        done: !!(cfg.subjectName && cfg.subjectCompetencies),
        help: '대시보드 상단 컨트롤 바에서 영역·과목·교과역량을 지정하세요.' },
      { key: 'pin', label: '접근 PIN 설정 (개인정보 보호)',
        done: cfg.pinRequired,
        help: '시트 메뉴 [6. 🔒 접근 PIN 설정]. PIN이 없으면 웹앱 주소를 아는 누구나 학생 정보를 볼 수 있습니다.' }
    ];

    var pending = items.filter(function (i) { return !i.done; });
    return {
      success: true,
      mode: DEPLOY_MODE,
      version: VERSION,
      ready: pending.length === 0,
      // 배포용은 설정이 끝날 때까지 체크리스트를 계속 띄웁니다
      forceWizard: isShared_() && pending.length > 0,
      items: items,
      pendingCount: pending.length,
      studentCount: realRoster.length
    };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  }
}

/** 메뉴에서만 호출되는 래퍼 — 여기서만 UI를 씁니다 */
function setupInitialSheets() {
  ensureSheets_();
  refreshRosterCache_();
  SpreadsheetApp.getUi().alert(
    '✅ 시트 양식이 세팅되었습니다.\n\n' +
    '[학생명렬] 탭에 나이스/엑셀 명단을 Ctrl+V로 붙여넣으세요.\n' +
    '(컬럼 순서: 반 · 번호 · 학번 · 이름)\n\n' +
    '명단을 바꾼 뒤에는 메뉴 [5. 🔄 학생명렬 캐시 새로고침]을 눌러주세요.');
}


// ═══════════════════════════════════════════════════════════════════
//  5. 학생 명렬 + [FIX #8] 캐싱
// ═══════════════════════════════════════════════════════════════════

function getStudentList(classNum) {
  var all = getStudentListCached();
  if (classNum === 'all' || classNum === '' || classNum == null) return all;
  var target = String(classNum);
  return all.filter(function (s) { return String(s.classNum) === target; });
}

/**
 * [FIX #8] 명렬을 6시간 캐시.
 * v2.0은 타이핑 한 글자마다 300행 시트를 통째로 읽어 스크립트 실행시간
 * 한도(개인 계정 90분/일)를 빠르게 소진했습니다.
 */
function getStudentListCached() {
  var cache = null;
  try { cache = CacheService.getScriptCache(); } catch (e) {}

  if (cache) {
    var hit = cache.get(ROSTER_CACHE_KEY);
    if (hit) { try { return JSON.parse(hit); } catch (e) {} }
  }

  var list = readRosterFromSheet_();

  if (cache) {
    // 캐시 항목은 100KB 제한 — 초과 시 조용히 통과 (다음 호출에서 다시 읽음)
    try { cache.put(ROSTER_CACHE_KEY, JSON.stringify(list), ROSTER_CACHE_SEC); } catch (e) {}
  }
  return list;
}

function readRosterFromSheet_() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET.ROSTER);
  if (!sheet || sheet.getLastRow() < 2) return [];

  var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 4).getValues();
  var out = [];
  for (var i = 0; i < data.length; i++) {
    var name = data[i][3] != null ? String(data[i][3]).trim() : '';
    var hakbun = data[i][2] != null ? String(data[i][2]).trim() : '';
    if (!name && !hakbun) continue;

    var cls = parseInt(data[i][0], 10);
    // [FIX #27] 반 칸이 비어 있으면 학번에서 유추 (예: 20707 → 7반)
    if (!cls && hakbun.length >= 5) cls = parseInt(hakbun.substr(1, 2), 10);

    out.push({
      classNum: cls || '',
      number:   parseInt(data[i][1], 10) || '',
      hakbun:   hakbun,
      name:     name,
      // [FIX #27] 학년 하드코딩(3) 제거 — 학번 첫 자리에서 추출
      grade:    hakbun.length >= 5 ? parseInt(hakbun.charAt(0), 10) || '' : ''
    });
  }
  return out;
}

function refreshRosterCache_() {
  try { CacheService.getScriptCache().remove(ROSTER_CACHE_KEY); } catch (e) {}
  return getStudentListCached();
}

function refreshRosterCacheMenu() {
  var list = refreshRosterCache_();
  SpreadsheetApp.getUi().alert('🔄 명렬 캐시를 새로 읽었습니다.\n\n등록 학생: ' + list.length + '명');
}

/** [FIX #27] 학번 첫 자리로 실제 학년 추출 */
function getAvailableGradesAndClasses() {
  try {
    assertPin_();
    var students = getStudentListCached();
    var byGrade = {};
    var gradeSet = {};

    for (var i = 0; i < students.length; i++) {
      var g = students[i].grade || 0;
      var c = students[i].classNum;
      if (!c) continue;
      gradeSet[g] = true;
      if (!byGrade[g]) byGrade[g] = {};
      byGrade[g][c] = true;
    }

    var grades = Object.keys(gradeSet).map(Number).sort(function (a, b) { return a - b; });
    var classesByGrade = {};
    for (var g2 in byGrade) {
      classesByGrade[g2] = Object.keys(byGrade[g2]).map(Number).sort(function (a, b) { return a - b; });
    }

    if (!grades.length) { grades = [0]; classesByGrade = { 0: [1,2,3,4,5,6,7,8,9,10] }; }
    return { success: true, grades: grades, classesByGrade: classesByGrade, total: students.length };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  }
}

/** 앱의 반 고정 모드 / 학생 직접 선택용 */
function getRosterForApp() {
  try {
    assertPin_();
    var students = getStudentListCached();
    var classes = {};
    for (var i = 0; i < students.length; i++) {
      var c = students[i].classNum;
      if (!c) continue;
      if (!classes[c]) classes[c] = [];
      classes[c].push({ hakbun: students[i].hakbun, name: students[i].name, number: students[i].number });
    }
    return {
      success: true,
      names: students.map(function (s) { return s.name; }).filter(Boolean),
      classes: classes,
      classList: Object.keys(classes).map(Number).sort(function (a, b) { return a - b; })
    };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  }
}


// ═══════════════════════════════════════════════════════════════════
//  6. [FIX #1][FIX #2] 학번/이름 파싱 — 핵심 수정
// ═══════════════════════════════════════════════════════════════════

/**
 * v2.0의 치명적 문제:
 *   ① 이름 매칭이 학번 매칭을 덮어써서, 학번을 정확히 말해도 무시됨
 *   ② 이름 검색이 명렬 위에서부터 first-match + break → 동명이인은 항상 앞 반 학생
 *   ③ 연도 배제 정규식이 숫자만 담긴 match[0]을 검사해 절대 동작하지 않음
 *
 * 실제 명렬(2학년 300명) 재현 결과:
 *   "20828 최현준 …"  → 1반 최현준(20131) 로 오저장
 *   "21026 조연우 …"  → 3반 조연우(20326) 로 오저장
 *   "20707 김민준 …"  → 3반 김민준(20302) 로 오저장
 *
 * v2.1 우선순위: ① 명렬에 실재하는 학번  ② 이름(긴 이름 우선)  ③ 숫자 추정
 * 동명이인이 걸리면 임의 선택하지 않고 ambiguous 로 돌려보내 앱에서 선택하게 합니다.
 *
 * @param {string} rawMemo   음성/텍스트 원문
 * @param {number|string} classHint  반 고정 모드에서 넘어온 반 (없으면 '')
 */
function parseHakbunAndNameFast(rawMemo, classHint) {
  var memo = String(rawMemo == null ? '' : rawMemo);
  var pool = getStudentListCached();

  // ── 반 고정 모드: 후보를 해당 반으로 한정 → 동명이인 문제 원천 차단
  var hintClass = (classHint === 0 || classHint) ? String(classHint) : '';
  if (hintClass && hintClass !== 'all') {
    var scoped = pool.filter(function (s) { return String(s.classNum) === hintClass; });
    if (scoped.length) pool = scoped;
  }

  // ── [FIX #2] 연도·날짜 표현을 원문에서 먼저 제거한 뒤 숫자 추출
  //    v2.0은 정규식이 뽑은 숫자만("2026") 검사해 "년"을 보지 못했습니다.
  var cleaned = memo
    .replace(/\d{4}\s*(?:년도|학년도|년)/g, ' ')
    .replace(/\d{1,2}\s*(?:학년|교시|월|일|시|분|초|번째|명|개|점)/g, ' ')
    .replace(/\d{1,2}\s*[-/.]\s*\d{1,2}/g, ' ');
  var candidates = cleaned.match(/\d{4,5}/g) || [];

  // ── ① 명렬에 실재하는 학번이면 즉시 확정 (최우선)
  for (var i = 0; i < candidates.length; i++) {
    for (var j = 0; j < pool.length; j++) {
      if (pool[j].hakbun && pool[j].hakbun === candidates[i]) {
        return ok_(pool[j], 'high');
      }
    }
  }

  // ── ② 이름 매칭. 긴 이름부터 검사해 '김현' ⊂ '김현빈' 오매칭을 방지
  var byLen = pool.slice().sort(function (a, b) {
    return String(b.name).length - String(a.name).length;
  });

  var matchedName = '';
  var hits = [];
  for (var k = 0; k < byLen.length; k++) {
    var s = byLen[k];
    if (!s.name) continue;
    if (memo.indexOf(s.name) < 0) continue;
    if (!matchedName) matchedName = s.name;
    if (s.name === matchedName) hits.push(s);   // 동일 이름의 모든 학생을 수집
  }

  if (hits.length === 1) return ok_(hits[0], 'high');

  if (hits.length > 1) {
    // ⚠️ 동명이인 — 임의 선택 금지. 앱이 선택 UI를 띄우도록 후보를 함께 반환
    return {
      hakbun: '', name: matchedName, classNum: '',
      confidence: 'ambiguous', ambiguous: true,
      candidates: hits.map(function (s) {
        return { hakbun: s.hakbun, name: s.name, classNum: s.classNum };
      })
    };
  }

  // ── ③ 명렬에 없는 숫자만 있는 경우 (전학생·오타 등)
  if (candidates.length) {
    var h = candidates[0];
    return {
      hakbun: h, name: '',
      classNum: hintClass || (h.length >= 5 ? (parseInt(h.substr(1, 2), 10) || '') : ''),
      confidence: 'low', ambiguous: false, candidates: []
    };
  }

  return { hakbun: '', name: '미인식', classNum: hintClass || '', confidence: 'none', ambiguous: false, candidates: [] };

  function ok_(s, conf) {
    return { hakbun: s.hakbun, name: s.name, classNum: s.classNum, confidence: conf, ambiguous: false, candidates: [] };
  }
}


// ═══════════════════════════════════════════════════════════════════
//  7. 관찰 기록 저장 / 수정 / 삭제
// ═══════════════════════════════════════════════════════════════════

/**
 * @param {string} rawMemo
 * @param {string} category         교과 / 행특 / 자율 / 진로 / 동아리
 * @param {string} clientTimestamp  앱이 만든 표시용 시각
 * @param {string|number} classHint 반 고정 모드
 * @param {string} forcedHakbun     동명이인 선택 결과 등, 학생을 확정해 보낼 때
 */
function processObservationFast(rawMemo, category, clientTimestamp, classHint, forcedHakbun) {
  try {
    assertPin_();

    var memo = String(rawMemo == null ? '' : rawMemo).trim();
    if (!memo) return { success: false, message: '메모 내용이 비어 있습니다.' };

    // [FIX #6] UI 없는 ensureSheets_() 사용 — v2.0은 여기서 getUi() 예외로 메모가 소실됐습니다
    var ss = ensureSheets_();
    var sheet = ss.getSheetByName(SHEET.OBS);

    var parsed;
    if (forcedHakbun) {
      // 앱에서 학생을 직접 지정한 경우 (동명이인 선택 / 리스트 선택)
      var picked = null;
      var all = getStudentListCached();
      for (var i = 0; i < all.length; i++) {
        if (all[i].hakbun === String(forcedHakbun)) { picked = all[i]; break; }
      }
      parsed = picked
        ? { hakbun: picked.hakbun, name: picked.name, classNum: picked.classNum, confidence: 'confirmed', ambiguous: false }
        : parseHakbunAndNameFast(memo, classHint);
    } else {
      parsed = parseHakbunAndNameFast(memo, classHint);
    }

    // ⚠️ 동명이인이면 저장하지 않고 앱에 선택을 요청
    if (parsed.ambiguous) {
      return {
        success: false, needsChoice: true, name: parsed.name,
        candidates: parsed.candidates,
        message: '"' + parsed.name + '" 학생이 ' + parsed.candidates.length + '명입니다. 반을 선택해 주세요.'
      };
    }

    var now = new Date();
    var serverTs = Utilities.formatDate(now, TZ, 'yyyy-MM-dd HH:mm:ss');
    // [FIX #27] 클라이언트 시각을 표시용으로 쓰되 서버 시각을 함께 남김
    var displayTs = clientTimestamp || Utilities.formatDate(now, TZ, 'yyyy-MM-dd HH:mm');
    var recordId = 'OBS' + now.getTime() + '-' + Math.floor(Math.random() * 10000);
    var refined = '[' + category + '] ' + memo;

    var row = [];
    row[OBS_COL.DATE]    = displayTs;
    row[OBS_COL.CLASS]   = parsed.classNum || '';
    row[OBS_COL.CAT]     = category || '교과';
    row[OBS_COL.HAKBUN]  = parsed.hakbun || '';
    row[OBS_COL.NAME]    = parsed.name || '';
    row[OBS_COL.MEMO]    = memo;
    row[OBS_COL.REFINED] = refined;
    row[OBS_COL.ID]      = recordId;
    row[OBS_COL.CONF]    = parsed.confidence;
    row[OBS_COL.SRVTS]   = serverTs;
    sheet.appendRow(row);

    if (parsed.hakbun || (parsed.name && parsed.name !== '미인식')) {
      try { updateStudentSummary(parsed.hakbun, parsed.name, memo); } catch (ignore) {}
    }

    return {
      success: true,
      recordId: recordId,
      category: category,
      hakbun: parsed.hakbun,
      name: parsed.name,
      classNum: parsed.classNum,
      confidence: parsed.confidence,
      refinedText: refined,
      timestamp: displayTs
    };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  }
}

/**
 * 📱 PWA 오프라인 큐 일괄 동기화 (Batch Sync)
 * 오프라인 상태에서 스마트폰에 누적된 복수 관찰 메모를 한번에 시트에 기록
 * @param {Array<Object>} items [{id, rawMemo, category, timestamp, classHint, forcedHakbun}]
 */
function syncOfflineObservationsBatch(items) {
  try {
    assertPin_();
    if (!Array.isArray(items) || !items.length) {
      return { success: true, processedCount: 0, results: [] };
    }
    var results = [];
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      var res = processObservationFast(it.rawMemo, it.category, it.timestamp, it.classHint, it.forcedHakbun);
      results.push({ id: it.id, res: res });
    }
    return { success: true, processedCount: results.length, results: results };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  }
}

/** 앱 '오늘 기록' — 최근 N건 조회 */
function getRecentObservations(limit) {
  try {
    assertPin_();
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET.OBS);
    if (!sheet || sheet.getLastRow() < 2) return { success: true, items: [] };

    var n = Math.min(parseInt(limit, 10) || 20, 100);
    var last = sheet.getLastRow();
    var start = Math.max(2, last - n + 1);
    var width = Math.max(sheet.getLastColumn(), 10);
    var data = sheet.getRange(start, 1, last - start + 1, width).getValues();

    var items = [];
    for (var i = data.length - 1; i >= 0; i--) {
      items.push({
        rowIndex:  start + i,
        recordId:  String(data[i][OBS_COL.ID] || ''),
        date:      formatAnyDate(data[i][OBS_COL.DATE]),
        classNum:  String(data[i][OBS_COL.CLASS] || ''),
        category:  String(data[i][OBS_COL.CAT] || ''),
        hakbun:    String(data[i][OBS_COL.HAKBUN] || ''),
        name:      String(data[i][OBS_COL.NAME] || ''),
        rawMemo:   String(data[i][OBS_COL.MEMO] || ''),
        confidence:String(data[i][OBS_COL.CONF] || '')
      });
    }
    return { success: true, items: items };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  }
}

/** 기록 삭제 (기록ID 기준) */
function deleteObservation(recordId) {
  var lock = LockService.getScriptLock();
  try {
    assertPin_();
    try { lock.waitLock(15000); } catch (e) { return { success: false, message: '다른 작업이 진행 중입니다. 잠시 후 다시 시도해 주세요.' }; }

    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET.OBS);
    if (!sheet || sheet.getLastRow() < 2) return { success: false, message: '기록이 없습니다.' };

    var ids = sheet.getRange(2, OBS_COL.ID + 1, sheet.getLastRow() - 1, 1).getValues();
    for (var i = 0; i < ids.length; i++) {
      if (String(ids[i][0]) === String(recordId)) {
        sheet.deleteRow(i + 2);
        return { success: true };
      }
    }
    return { success: false, message: '해당 기록을 찾을 수 없습니다.' };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  } finally {
    try { lock.releaseLock(); } catch (e) {}
  }
}

/**
 * [FIX #18] 미인식·저확신 기록 재배정.
 * v2.0에서는 '미인식'으로 저장된 기록이 어떤 세특에도 반영되지 않고 방치됐습니다.
 */
function getUnmatchedObservations() {
  try {
    assertPin_();
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET.OBS);
    if (!sheet || sheet.getLastRow() < 2) return { success: true, items: [] };

    var width = Math.max(sheet.getLastColumn(), 10);
    var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, width).getValues();
    var roster = getStudentListCached();
    var known = {};
    for (var r = 0; r < roster.length; r++) if (roster[r].hakbun) known[roster[r].hakbun] = true;

    var items = [];
    for (var i = 0; i < data.length; i++) {
      var hak = String(data[i][OBS_COL.HAKBUN] || '');
      var nm  = String(data[i][OBS_COL.NAME] || '');
      var bad = (!hak || !known[hak] || !nm || nm === '미인식');
      if (!bad) continue;
      items.push({
        recordId: String(data[i][OBS_COL.ID] || ''),
        date:     formatAnyDate(data[i][OBS_COL.DATE]),
        category: String(data[i][OBS_COL.CAT] || ''),
        hakbun:   hak, name: nm,
        rawMemo:  String(data[i][OBS_COL.MEMO] || '')
      });
    }
    return { success: true, items: items, count: items.length };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  }
}

function reassignObservation(recordId, hakbun) {
  var lock = LockService.getScriptLock();
  try {
    assertPin_();
    try { lock.waitLock(15000); } catch (e) { return { success: false, message: '다른 작업이 진행 중입니다.' }; }

    var target = null;
    var roster = getStudentListCached();
    for (var r = 0; r < roster.length; r++) if (roster[r].hakbun === String(hakbun)) { target = roster[r]; break; }
    if (!target) return { success: false, message: '명렬에서 학번 ' + hakbun + ' 을 찾을 수 없습니다.' };

    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET.OBS);
    var ids = sheet.getRange(2, OBS_COL.ID + 1, sheet.getLastRow() - 1, 1).getValues();
    for (var i = 0; i < ids.length; i++) {
      if (String(ids[i][0]) !== String(recordId)) continue;
      var row = i + 2;
      sheet.getRange(row, OBS_COL.CLASS + 1).setValue(target.classNum);
      sheet.getRange(row, OBS_COL.HAKBUN + 1).setValue(target.hakbun);
      sheet.getRange(row, OBS_COL.NAME + 1).setValue(target.name);
      sheet.getRange(row, OBS_COL.CONF + 1).setValue('confirmed');
      return { success: true, name: target.name, classNum: target.classNum, hakbun: target.hakbun };
    }
    return { success: false, message: '해당 기록을 찾을 수 없습니다.' };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  } finally {
    try { lock.releaseLock(); } catch (e) {}
  }
}

/** 앱 코칭 카드 — 디바운스는 클라이언트에서 처리 (#8) */
function analyzeObservationFeedback(rawMemo, category, classHint) {
  try {
    assertPin_();
    var parsed = parseHakbunAndNameFast(rawMemo, classHint);

    if (parsed.ambiguous) {
      return {
        success: true, hasStudentInfo: false, ambiguous: true,
        candidates: parsed.candidates,
        feedbackTitle: '👥 동명이인 확인 필요',
        feedbackMsg: '"' + parsed.name + '" 학생이 ' + parsed.candidates.length + '명입니다. 학번을 함께 말씀하시거나 저장 시 반을 선택해 주세요.'
      };
    }

    var has = !!(parsed.hakbun || (parsed.name && parsed.name !== '미인식'));
    if (!has) {
      return {
        success: true, hasStudentInfo: false, ambiguous: false, candidates: [],
        feedbackTitle: '⚠️ 학번/이름 누락',
        feedbackMsg: '학번(예: 20707)이나 이름을 말씀해 주시면 자동으로 매칭됩니다.'
      };
    }
    if (parsed.confidence === 'low') {
      return {
        success: true, hasStudentInfo: true, ambiguous: false, candidates: [],
        matchedName: parsed.name, matchedHakbun: parsed.hakbun,
        feedbackTitle: '❓ 명렬에 없는 학번',
        feedbackMsg: '학번 ' + parsed.hakbun + ' 은 명렬에 없습니다. 저장은 되지만 세특에는 반영되지 않으니 확인해 주세요.'
      };
    }
    return {
      success: true, hasStudentInfo: true, ambiguous: false, candidates: [],
      matchedName: parsed.name, matchedHakbun: parsed.hakbun, matchedClass: parsed.classNum,
      feedbackTitle: '💡 ' + parsed.classNum + '반 ' + parsed.name + ' 확인됨',
      feedbackMsg: '구체적인 탐구 주제·사용 자료·수행 과정을 덧붙이시면 2022 교과역량이 잘 드러나는 세특이 됩니다.'
    };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  }
}


// ═══════════════════════════════════════════════════════════════════
//  8. [FIX #13] 학생별모아보기 집계
// ═══════════════════════════════════════════════════════════════════

function updateStudentSummary(hakbun, name, newMemo) {
  // 학번이 없으면 이름을 키로 사용 (v2.0은 빈 학번마다 새 행이 계속 쌓였습니다)
  var key = String(hakbun || '') || (name ? 'name:' + name : '');
  if (!key) return;

  var lock = LockService.getScriptLock();
  // 읽고-수정하고-쓰는 구조라 동시 저장 시 누적 건수가 유실될 수 있어 락이 필요합니다
  try { lock.waitLock(10000); } catch (e) { return; }

  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET.SUMMARY);
    if (!sheet) return;

    var last = sheet.getLastRow();
    if (last >= 2) {
      var data = sheet.getRange(2, 1, last - 1, 4).getValues();
      for (var i = 0; i < data.length; i++) {
        var rowKey = String(data[i][0] || '') || (data[i][1] ? 'name:' + String(data[i][1]) : '');
        if (rowKey !== key) continue;

        var existing = String(data[i][3] || '');
        var merged = existing + (existing ? ' | ' : '') + newMemo;
        if (merged.length > SUMMARY_CELL_MAX) merged = merged.slice(-SUMMARY_CELL_MAX);   // 셀 5만자 한도 방어
        sheet.getRange(i + 2, 3, 1, 2).setValues([[(parseInt(data[i][2], 10) || 0) + 1, merged]]);
        return;
      }
    }
    sheet.appendRow([hakbun || '', name || '', 1, newMemo]);
  } finally {
    try { lock.releaseLock(); } catch (e) {}
  }
}

/** [FIX #25] 중복 관리로 어긋난 집계를 시간대별기록에서 다시 계산 */
function rebuildStudentSummary_() {
  var ss = ensureSheets_();
  var obs = ss.getSheetByName(SHEET.OBS);
  var sum = ss.getSheetByName(SHEET.SUMMARY);
  if (!obs || !sum) return 0;

  sum.clear();
  sum.appendRow(HEADERS[SHEET.SUMMARY]);
  sum.getRange(1, 1, 1, 4).setFontWeight('bold').setBackground('#eeedfc');
  if (obs.getLastRow() < 2) return 0;

  var width = Math.max(obs.getLastColumn(), 10);
  var data = obs.getRange(2, 1, obs.getLastRow() - 1, width).getValues();
  var map = {}, order = [];

  for (var i = 0; i < data.length; i++) {
    var hak = String(data[i][OBS_COL.HAKBUN] || '');
    var nm  = String(data[i][OBS_COL.NAME] || '');
    var key = hak || (nm ? 'name:' + nm : '');
    if (!key || nm === '미인식' && !hak) continue;

    if (!map[key]) { map[key] = { hakbun: hak, name: nm, count: 0, memos: [] }; order.push(key); }
    map[key].count++;
    map[key].memos.push(String(data[i][OBS_COL.MEMO] || ''));
  }

  var rows = order.map(function (k) {
    var t = map[k].memos.join(' | ');
    if (t.length > SUMMARY_CELL_MAX) t = t.slice(-SUMMARY_CELL_MAX);
    return [map[k].hakbun, map[k].name, map[k].count, t];
  });
  if (rows.length) sum.getRange(2, 1, rows.length, 4).setValues(rows);
  return rows.length;
}

function rebuildStudentSummaryMenu() {
  var n = rebuildStudentSummary_();
  SpreadsheetApp.getUi().alert('🧮 [학생별모아보기]를 다시 계산했습니다.\n\n집계된 학생: ' + n + '명');
}


// ═══════════════════════════════════════════════════════════════════
//  9. [FIX #25] 구글 폼 → 학생응답기록 자동 수집
// ═══════════════════════════════════════════════════════════════════

/**
 * v2.0에서 [학생응답기록] 탭은 만들어지기만 하고 아무도 쓰지 않았습니다.
 * 스프레드시트에 연결된 구글 폼의 제출을 이 탭으로 옮깁니다.
 *
 * 폼 문항 예시: 학번 / 이름 / 자기평가·소감 / 구분(자율/진로/동아리…)
 */
function onFormSubmitHandler(e) {
  try {
    if (!e || !e.namedValues) return;
    var nv = e.namedValues;
    var pick = function (keys) {
      for (var i = 0; i < keys.length; i++) {
        for (var k in nv) {
          if (nv.hasOwnProperty(k) && k.replace(/\s/g, '').indexOf(keys[i]) >= 0) {
            return (nv[k] && nv[k][0]) ? String(nv[k][0]).trim() : '';
          }
        }
      }
      return '';
    };

    var hakbun = pick(['학번']);
    var name   = pick(['이름', '성명']);
    var type   = pick(['구분', '영역', '유형']) || '자기평가';
    var body   = pick(['내용', '소감', '응답', '답변', '평가']);

    var roster = getStudentListCached();
    var cls = '';
    for (var i = 0; i < roster.length; i++) {
      if (hakbun && roster[i].hakbun === hakbun) { cls = roster[i].classNum; name = name || roster[i].name; break; }
      if (!hakbun && name && roster[i].name === name) { cls = roster[i].classNum; hakbun = roster[i].hakbun; break; }
    }

    var ss = ensureSheets_();
    ss.getSheetByName(SHEET.RESP).appendRow([
      Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd HH:mm'),
      cls, hakbun, name, body, type
    ]);
  } catch (err) {
    log_('폼수집오류', '', err.message || String(err));
  }
}

function installFormTriggerPrompt() {
  var ui = SpreadsheetApp.getUi();
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  var existing = ScriptApp.getProjectTriggers().filter(function (t) {
    return t.getHandlerFunction() === 'onFormSubmitHandler';
  });
  if (existing.length) {
    ui.alert('이미 폼 응답 자동수집이 연결되어 있습니다.');
    return;
  }

  var resp = ui.alert('📥 구글 폼 응답 자동수집',
    '이 스프레드시트에 연결된 구글 폼의 응답을 [학생응답기록] 탭으로 자동 수집합니다.\n\n' +
    '먼저 [도구] → [설문지 만들기]로 폼을 연결하고,\n' +
    '문항 제목에 "학번", "이름", "구분", "내용" 이 들어가게 만들어 주세요.\n\n' +
    '지금 연결할까요?', ui.ButtonSet.YES_NO);
  if (resp !== ui.Button.YES) return;

  ScriptApp.newTrigger('onFormSubmitHandler').forSpreadsheet(ss).onFormSubmit().create();
  ensureSheets_();
  ui.alert('✅ 연결되었습니다. 이제 폼 응답이 [학생응답기록] 탭에 자동으로 쌓입니다.');
}


// ═══════════════════════════════════════════════════════════════════
//  10. 대시보드 데이터
// ═══════════════════════════════════════════════════════════════════

function formatAnyDate(val) {
  if (val === null || val === undefined || val === '') return '';
  if (val instanceof Date) return Utilities.formatDate(val, TZ, 'yyyy-MM-dd HH:mm');
  return String(val);
}

function toTime_(val) {
  if (!val) return 0;
  if (val instanceof Date) return val.getTime();
  var t = new Date(String(val).replace(/-/g, '/')).getTime();
  return isNaN(t) ? 0 : t;
}

/**
 * [FIX #27] 1년치 수천 행을 매번 통째로 보내던 구조를 최근 N행으로 제한.
 * @param {string|number} classNum
 * @param {number} days  최근 N일만 (0 = 전체)
 */
function getDashboardFullData(classNum, days) {
  try {
    assertPin_();
    var ss = ensureSheets_();
    var students = getStudentList(classNum);
    var config = getApiConfig();

    var since = 0;
    var d = parseInt(days, 10);
    if (d && d > 0) since = new Date().getTime() - d * 24 * 60 * 60 * 1000;

    var observations = readRows_(ss.getSheetByName(SHEET.OBS), function (r) {
      var c = r[OBS_COL.CLASS];
      if (!(classNum === 'all' || String(c) === String(classNum))) return null;
      if (since && toTime_(r[OBS_COL.DATE]) && toTime_(r[OBS_COL.DATE]) < since) return null;
      return {
        recordId:   String(r[OBS_COL.ID] || ''),
        date:       formatAnyDate(r[OBS_COL.DATE]),
        classNum:   r[OBS_COL.CLASS] != null ? String(r[OBS_COL.CLASS]) : '',
        category:   String(r[OBS_COL.CAT] || ''),
        hakbun:     String(r[OBS_COL.HAKBUN] || ''),
        name:       String(r[OBS_COL.NAME] || ''),
        rawMemo:    String(r[OBS_COL.MEMO] || ''),
        refinedText:String(r[OBS_COL.REFINED] || ''),
        confidence: String(r[OBS_COL.CONF] || '')
      };
    });

    var responses = readRows_(ss.getSheetByName(SHEET.RESP), function (r) {
      if (!(classNum === 'all' || String(r[1]) === String(classNum))) return null;
      return {
        date: formatAnyDate(r[0]), classNum: r[1] != null ? String(r[1]) : '',
        hakbun: String(r[2] || ''), name: String(r[3] || ''),
        content: String(r[4] || ''), type: String(r[5] || '')
      };
    });

    var reports = readRows_(ss.getSheetByName(SHEET.REPORT), function (r) {
      if (!(classNum === 'all' || String(r[REP_COL.CLASS]) === String(classNum))) return null;
      return {
        classNum: r[REP_COL.CLASS] != null ? String(r[REP_COL.CLASS]) : '',
        hakbun: String(r[REP_COL.HAKBUN] || ''), name: String(r[REP_COL.NAME] || ''),
        date: formatAnyDate(r[REP_COL.DATE]), bytes: String(r[REP_COL.BYTES] || ''),
        reportText: String(r[REP_COL.TEXT] || ''), engine: String(r[REP_COL.ENGINE] || '')
      };
    });

    var unmatched = 0;
    for (var i = 0; i < observations.length; i++) {
      if (!observations[i].hakbun || observations[i].name === '미인식') unmatched++;
    }

    return {
      success: true, version: VERSION, config: config,
      students: students, observations: observations,
      responses: responses, reports: reports,
      unmatchedCount: unmatched
    };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  }
}

function readRows_(sheet, mapFn) {
  if (!sheet || sheet.getLastRow() < 2) return [];
  var last = sheet.getLastRow();
  var start = Math.max(2, last - DASHBOARD_MAX_ROWS + 1);
  var width = Math.max(sheet.getLastColumn(), 1);
  var data = sheet.getRange(start, 1, last - start + 1, width).getValues();
  var out = [];
  for (var i = 0; i < data.length; i++) {
    var m = mapFn(data[i]);
    if (m) out.push(m);
  }
  return out;
}

function getSpreadsheetUrl() {
  try { assertPin_(); return SpreadsheetApp.getActiveSpreadsheet().getUrl(); }
  catch (e) { return ''; }
}


// ═══════════════════════════════════════════════════════════════════
//  11. [FIX #17] 영역 매칭
// ═══════════════════════════════════════════════════════════════════

/**
 * v2.0은 과목명 문자열만 보고 판정해서 '진로와 직업', '자율탐구' 같은
 * 정규 교과목을 창의적체험활동으로 오인했습니다.
 * v2.1은 대시보드가 보내는 영역(domain)만으로 판정합니다.
 */
function isCategoryMatch(obsCategory, domain) {
  var cat = String(obsCategory || '교과').trim();
  var dom = String(domain || '교과').trim();

  if (dom === '동아리') return cat.indexOf('동아리') >= 0;
  if (dom === '행특')   return cat.indexOf('행특') >= 0 || cat.indexOf('행동') >= 0;
  if (dom === '자율')   return cat.indexOf('자율') >= 0;
  if (dom === '진로')   return cat.indexOf('진로') >= 0;
  if (dom === '자율/진로') return cat.indexOf('자율') >= 0 || cat.indexOf('진로') >= 0;
  if (dom === '전체')   return true;

  // 교과: 창체 4영역을 제외한 나머지
  return !(cat.indexOf('동아리') >= 0 || cat.indexOf('행특') >= 0 || cat.indexOf('행동') >= 0 ||
           cat.indexOf('자율') >= 0 || cat.indexOf('진로') >= 0);
}


// ═══════════════════════════════════════════════════════════════════
//  12. [FIX #3][FIX #4] 세특 생성 — 배치 + 갱신
// ═══════════════════════════════════════════════════════════════════

/**
 * [FIX #3] v2.0은 300명 기준 sleep 만 14분 45초, AI 호출까지 25~40분이라
 * Apps Script 실행 한도(개인 6분 / Workspace 30분)를 반드시 초과했습니다.
 * v2.1은 한 번에 최대 20명 또는 4분까지만 처리하고 nextIndex를 돌려줍니다.
 * 대시보드가 finished === false 인 동안 반복 호출하며 진행률을 표시합니다.
 *
 * [FIX #4] v2.0은 appendRow만 해서 재생성할 때마다 행이 중복 누적됐고,
 * README의 "변경 없는 학생 기존 세특 100% 유지"는 구현되어 있지 않았습니다.
 * v2.1은 학번으로 기존 행을 찾아 갱신하고, 마지막 생성 시각 이후 신규
 * 관찰이 없으면 실제로 건너뜁니다.
 */
function generateReportsBatch(classNum, domain, subject, competency, targetBytes, startIndex) {
  var t0 = new Date().getTime();
  try {
    assertPin_();
    var ss = ensureSheets_();
    var reportSheet = ss.getSheetByName(SHEET.REPORT);
    var obsSheet = ss.getSheetByName(SHEET.OBS);

    var cfg = getApiConfig();
    var dom  = String(domain || cfg.domain || '교과');
    var subj = String(subject || cfg.subjectName || '교과');
    var comp = String(competency || cfg.subjectCompetencies);

    // [FIX #16] NaN 방어
    var bytesTarget = parseInt(targetBytes, 10);
    if (!bytesTarget || bytesTarget < 100 || bytesTarget > 3000) bytesTarget = parseInt(cfg.targetBytes, 10) || 900;

    var students = getStudentList(classNum);
    var guidelines = getTemplateGuidelines();

    // ── 관찰 기록을 한 번만 읽어 학번/이름 키로 색인
    var obsByKey = {};
    if (obsSheet && obsSheet.getLastRow() > 1) {
      var w = Math.max(obsSheet.getLastColumn(), 10);
      var od = obsSheet.getRange(2, 1, obsSheet.getLastRow() - 1, w).getValues();
      for (var i = 0; i < od.length; i++) {
        var hak = String(od[i][OBS_COL.HAKBUN] || '');
        var nm  = String(od[i][OBS_COL.NAME] || '');
        var cls = String(od[i][OBS_COL.CLASS] || '');
        var item = {
          category: String(od[i][OBS_COL.CAT] || ''),
          memo:     String(od[i][OBS_COL.MEMO] || ''),
          at:       toTime_(od[i][OBS_COL.SRVTS]) || toTime_(od[i][OBS_COL.DATE])   // [FIX #4] 일시 포함
        };
        if (hak) push_(obsByKey, 'H:' + hak, item);
        if (nm && nm !== '미인식') push_(obsByKey, 'N:' + cls + '/' + nm, item);
      }
    }

    // ── [FIX #4] 기존 세특 행 색인 (학번 → 행번호, 마지막 반영 관찰시각)
    var rowByHakbun = {}, prevObsAt = {};
    if (reportSheet.getLastRow() > 1) {
      var rw = Math.max(reportSheet.getLastColumn(), 8);
      var rd = reportSheet.getRange(2, 1, reportSheet.getLastRow() - 1, rw).getValues();
      for (var r = 0; r < rd.length; r++) {
        var k = String(rd[r][REP_COL.HAKBUN] || '');
        if (!k) continue;
        rowByHakbun[k] = r + 2;
        prevObsAt[k] = toTime_(rd[r][REP_COL.OBSAT]) || toTime_(rd[r][REP_COL.DATE]);
      }
    }

    var idx = parseInt(startIndex, 10) || 0;
    var created = 0, updated = 0, retained = 0, skipped = 0, fallback = 0;
    var aiCalls = 0;
    var engineName = (cfg.selectedAI === 'Upstage' && cfg.upstageKey) ? ('Upstage/' + cfg.upstageModel)
                   : (cfg.geminiKey ? ('Gemini/' + cfg.geminiModel) : '템플릿');

    for (; idx < students.length; idx++) {
      if (new Date().getTime() - t0 > BATCH_TIME_LIMIT_MS) break;
      if (aiCalls >= BATCH_MAX_STUDENTS) break;

      var s = students[idx];
      var sHakbun = String(s.hakbun || '');
      var sName = String(s.name || '');
      var sClass = String(s.classNum || '');

      var raw = (obsByKey['H:' + sHakbun] || []).concat(obsByKey['N:' + sClass + '/' + sName] || []);

      // 중복 제거 (학번+이름 양쪽에 걸린 기록)
      var seen = {}, mine = [];
      for (var q = 0; q < raw.length; q++) {
        var sig = raw[q].at + '|' + raw[q].memo;
        if (seen[sig]) continue;
        seen[sig] = true;
        if (isCategoryMatch(raw[q].category, dom)) mine.push(raw[q]);
      }

      if (!mine.length) { skipped++; continue; }

      // [FIX #4] 진짜 Diff — 지난 생성 이후 신규 관찰이 없으면 기존 초안 유지
      var lastObsAt = 0;
      for (var m = 0; m < mine.length; m++) if (mine[m].at > lastObsAt) lastObsAt = mine[m].at;
      if (rowByHakbun[sHakbun] && lastObsAt <= (prevObsAt[sHakbun] || 0)) { retained++; continue; }

      // ── [FIX #23] AI에는 실명·학번을 보내지 않음
      var obsText = mine.map(function (o) {
        return '[' + (o.category || '기타') + '] ' + maskPii_(o.memo, sName);
      }).join('\n');

      if (aiCalls > 0 && aiCalls % AI_PAUSE_EVERY === 0) Utilities.sleep(AI_PAUSE_MS);

      var prompt = buildSeteukPrompt(NAME_TOKEN, dom, subj, comp, bytesTarget, obsText, guidelines);
      var aiResult = callAI(prompt);
      aiCalls++;

      var usedEngine = engineName;
      if (!aiResult) {
        fallback++;
        usedEngine = '템플릿(AI실패)';
        log_('AI실패', sClass + '반 ' + sName, 'API 호출 실패 또는 빈 응답 — 임시 템플릿으로 대체');
        aiResult = buildFallbackReport(NAME_TOKEN, subj, comp, mine, sName);
      }

      // 가명 복원
      var reportText = String(aiResult)
        .replace(/^```[a-z]*\s*/i, '').replace(/```\s*$/,'')   // 마크다운 코드펜스 제거
        .trim();
      reportText = (cfg.nameInReport === 'N')
        ? reportText.replace(new RegExp(NAME_TOKEN + '\\s*(학생)?\\s*(은|는|이|가)?\\s*', 'g'), '')
        : reportText.replace(new RegExp(NAME_TOKEN, 'g'), sName);

      reportText = trimToBytes(reportText, bytesTarget);

      var ts = Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd HH:mm');
      var bytes = byteLen_(reportText);
      var row = [s.classNum, s.hakbun, sName, ts, bytes + ' Bytes', reportText, usedEngine,
                 Utilities.formatDate(new Date(lastObsAt || new Date().getTime()), TZ, 'yyyy-MM-dd HH:mm:ss')];

      if (rowByHakbun[sHakbun]) {
        reportSheet.getRange(rowByHakbun[sHakbun], 1, 1, row.length).setValues([row]);   // [FIX #4] 갱신
        updated++;
      } else {
        reportSheet.appendRow(row);
        rowByHakbun[sHakbun] = reportSheet.getLastRow();
        created++;
      }
      prevObsAt[sHakbun] = lastObsAt;
    }

    var finished = idx >= students.length;
    if (finished) {
      var label = String(classNum) + ' / ' + dom + (dom === '교과' ? '(' + subj + ')' : '');
      log_('생성완료', label,
           '신규 ' + created + ' · 갱신 ' + updated + ' · 유지 ' + retained + ' · 관찰없음 ' + skipped + ' · AI실패 ' + fallback);

      // 💬 텔레그램 완료 알림 (설정된 경우에만)
      notifyTelegram_(
        '🔮 <b>AI 세특 생성 완료</b>\n' +
        '━━━━━━━━━━━━━━\n' +
        '📚 대상: ' + label + '\n' +
        '👥 전체: ' + students.length + '명\n' +
        '✨ 신규: ' + created + '명   🔄 갱신: ' + updated + '명\n' +
        '🛡️ 유지: ' + retained + '명   ⚪ 관찰없음: ' + skipped + '명\n' +
        (fallback ? '⚠️ <b>AI 실패: ' + fallback + '명</b> (임시 템플릿 — 재생성 필요)\n' : '') +
        '📏 목표: ' + bytesTarget + ' Bytes\n' +
        '🕒 ' + Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd HH:mm')
      );
    }

    return {
      success: true,
      nextIndex: idx, finished: finished,
      total: students.length, processed: idx,
      created: created, updated: updated, retained: retained,
      skipped: skipped, fallbackCount: fallback,
      targetBytes: String(bytesTarget), domain: dom, subject: subj,
      engine: engineName
    };
  } catch (e) {
    return { success: false, message: e.message || String(e), nextIndex: parseInt(startIndex, 10) || 0, finished: false };
  }
}

function push_(obj, key, item) {
  if (!obj[key]) obj[key] = [];
  obj[key].push(item);
}

/** 메뉴에서 실행 — 배치를 반복 호출해 완주 */
function generateAllStudentReportsMenu() {
  var ui = SpreadsheetApp.getUi();
  var cfg = getApiConfig();

  var r = ui.prompt('🔮 AI 세특 생성', '생성할 반 번호를 입력하세요 (예: 3 / 전체는 all):', ui.ButtonSet.OK_CANCEL);
  if (r.getSelectedButton() !== ui.Button.OK) return;
  var cNum = r.getResponseText().trim() || 'all';

  var idx = 0, guard = 0;
  var tot = { created: 0, updated: 0, retained: 0, skipped: 0, fallbackCount: 0, total: 0 };

  while (guard++ < 60) {
    var res = generateReportsBatch(cNum, cfg.domain, cfg.subjectName, cfg.subjectCompetencies, cfg.targetBytes, idx);
    if (!res.success) { ui.alert('오류: ' + res.message); return; }
    tot.created += res.created; tot.updated += res.updated; tot.retained += res.retained;
    tot.skipped += res.skipped; tot.fallbackCount += res.fallbackCount; tot.total = res.total;
    if (res.finished) break;
    idx = res.nextIndex;
  }

  ui.alert('🎉 AI 세특 초안 생성 완료\n\n' +
           '• 대상: ' + tot.total + '명\n' +
           '• 신규 생성: ' + tot.created + '명\n' +
           '• 갱신: ' + tot.updated + '명\n' +
           '• 변경 없어 유지: ' + tot.retained + '명\n' +
           '• 관찰 기록 없음: ' + tot.skipped + '명\n' +
           (tot.fallbackCount ? '\n⚠️ AI 호출 실패 ' + tot.fallbackCount + '명은 임시 템플릿으로 작성되었습니다.\n   API 키와 잔여 할당량을 확인한 뒤 다시 실행해 주세요.' : ''));
}

/** v2.0 호환용 래퍼 (기존 코드/북마크가 호출해도 동작) */
function generateAllStudentReports(classNum, subject, competency, bytes) {
  var cfg = getApiConfig();
  var idx = 0, guard = 0, agg = null;
  var tot = { created: 0, updated: 0, retained: 0, skipped: 0, fallbackCount: 0 };
  while (guard++ < 60) {
    agg = generateReportsBatch(classNum, cfg.domain, subject, competency, bytes, idx);
    if (!agg.success) return agg;
    tot.created += agg.created; tot.updated += agg.updated; tot.retained += agg.retained;
    tot.skipped += agg.skipped; tot.fallbackCount += agg.fallbackCount;
    if (agg.finished) break;
    idx = agg.nextIndex;
  }
  return {
    success: true, count: tot.created + tot.updated, retainedCount: tot.retained,
    fallbackCount: tot.fallbackCount, targetBytes: agg ? agg.targetBytes : '900',
    subject: agg ? agg.subject : subject
  };
}

/** 학생 한 명만 다시 생성 */
function regenerateOneStudent(hakbun, domain, subject, competency, targetBytes) {
  try {
    assertPin_();
    var all = getStudentListCached();
    var target = null, classNum = '';
    for (var i = 0; i < all.length; i++) if (all[i].hakbun === String(hakbun)) { target = all[i]; classNum = all[i].classNum; break; }
    if (!target) return { success: false, message: '명렬에서 학생을 찾을 수 없습니다.' };

    // 해당 학생의 기존 반영시각을 지워 강제 재생성
    var ss = ensureSheets_();
    var rs = ss.getSheetByName(SHEET.REPORT);
    if (rs.getLastRow() > 1) {
      var hs = rs.getRange(2, REP_COL.HAKBUN + 1, rs.getLastRow() - 1, 1).getValues();
      for (var r = 0; r < hs.length; r++) {
        if (String(hs[r][0]) === String(hakbun)) { rs.getRange(r + 2, REP_COL.OBSAT + 1).setValue(''); break; }
      }
    }

    var students = getStudentList(classNum);
    var pos = 0;
    for (var p = 0; p < students.length; p++) if (students[p].hakbun === String(hakbun)) { pos = p; break; }

    var res = generateReportsBatchSingle_(classNum, pos, domain, subject, competency, targetBytes);
    return res;
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  }
}

function generateReportsBatchSingle_(classNum, pos, domain, subject, competency, targetBytes) {
  var saved = BATCH_MAX_STUDENTS;
  BATCH_MAX_STUDENTS = 1;
  try {
    return generateReportsBatch(classNum, domain, subject, competency, targetBytes, pos);
  } finally {
    BATCH_MAX_STUDENTS = saved;
  }
}

/** 대시보드 인라인 편집 저장 */
function saveReportText(hakbun, newText) {
  var lock = LockService.getScriptLock();
  try {
    assertPin_();
    try { lock.waitLock(15000); } catch (e) { return { success: false, message: '다른 작업이 진행 중입니다.' }; }

    var rs = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET.REPORT);
    if (!rs || rs.getLastRow() < 2) return { success: false, message: '세특 초안이 없습니다.' };

    var hs = rs.getRange(2, REP_COL.HAKBUN + 1, rs.getLastRow() - 1, 1).getValues();
    for (var r = 0; r < hs.length; r++) {
      if (String(hs[r][0]) !== String(hakbun)) continue;
      var text = String(newText || '').trim();
      rs.getRange(r + 2, REP_COL.TEXT + 1).setValue(text);
      rs.getRange(r + 2, REP_COL.BYTES + 1).setValue(byteLen_(text) + ' Bytes');
      rs.getRange(r + 2, REP_COL.DATE + 1).setValue(Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd HH:mm'));
      rs.getRange(r + 2, REP_COL.ENGINE + 1).setValue('교사 직접 수정');
      return { success: true, bytes: byteLen_(text) };
    }
    return { success: false, message: '해당 학생의 초안을 찾을 수 없습니다.' };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  } finally {
    try { lock.releaseLock(); } catch (e) {}
  }
}


// ═══════════════════════════════════════════════════════════════════
//  13. AI 호출
// ═══════════════════════════════════════════════════════════════════

function callGeminiApi(prompt) {
  var cfg = getApiConfig();
  if (!cfg.geminiKey) return null;

  var url = 'https://generativelanguage.googleapis.com/v1beta/models/' +
            encodeURIComponent(cfg.geminiModel) + ':generateContent';
  var payload = {
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    generationConfig: { temperature: 0.7, maxOutputTokens: 2048 }   // 1024 → 2048 (1500B 목표 대비 여유)
  };

  try {
    var res = UrlFetchApp.fetch(url, {
      method: 'post',
      contentType: 'application/json',
      headers: { 'x-goog-api-key': cfg.geminiKey },   // 키를 URL이 아닌 헤더로 전송
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });

    var code = res.getResponseCode();
    var body = res.getContentText();
    if (code < 200 || code >= 300) {
      Logger.log('Gemini HTTP ' + code + ': ' + body.substring(0, 400));
      return null;
    }

    var json = JSON.parse(body);
    var cand = json.candidates && json.candidates[0];
    if (cand && cand.content && cand.content.parts && cand.content.parts.length) {
      var text = cand.content.parts.map(function (p) { return p.text || ''; }).join('').trim();
      if (text) return text;
    }
    Logger.log('Gemini 응답 파싱 실패(finishReason=' + (cand && cand.finishReason) + '): ' + body.substring(0, 400));
    return null;
  } catch (e) {
    Logger.log('Gemini 호출 에러: ' + e);
    return null;
  }
}

function callUpstageApi(prompt) {
  var cfg = getApiConfig();
  if (!cfg.upstageKey) return null;

  try {
    var res = UrlFetchApp.fetch('https://api.upstage.ai/v1/solar/chat/completions', {
      method: 'post',
      contentType: 'application/json',
      headers: { 'Authorization': 'Bearer ' + cfg.upstageKey },
      payload: JSON.stringify({
        model: cfg.upstageModel,
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.7,
        max_tokens: 2048
      }),
      muteHttpExceptions: true
    });

    var code = res.getResponseCode();
    var body = res.getContentText();
    if (code < 200 || code >= 300) { Logger.log('Upstage HTTP ' + code + ': ' + body.substring(0, 400)); return null; }

    var json = JSON.parse(body);
    if (json.choices && json.choices[0] && json.choices[0].message) {
      var t = String(json.choices[0].message.content || '').trim();
      if (t) return t;
    }
    Logger.log('Upstage 응답 파싱 실패: ' + body.substring(0, 400));
    return null;
  } catch (e) {
    Logger.log('Upstage 호출 에러: ' + e);
    return null;
  }
}

function callAI(prompt) {
  var cfg = getApiConfig();
  if (cfg.selectedAI === 'Upstage' && cfg.upstageKey) {
    return callUpstageApi(prompt) || (cfg.geminiKey ? callGeminiApi(prompt) : null);
  }
  if (cfg.geminiKey) {
    return callGeminiApi(prompt) || (cfg.upstageKey ? callUpstageApi(prompt) : null);
  }
  if (cfg.upstageKey) return callUpstageApi(prompt);
  Logger.log('AI API 키 미설정 — 템플릿으로 대체합니다.');
  return null;
}

/** API 키가 실제로 살아 있는지 대시보드에서 확인 */
function testAiConnection() {
  try {
    assertPin_();
    var cfg = getApiConfig();
    if (!cfg.geminiKey && !cfg.upstageKey) return { success: false, message: 'API 키가 설정되어 있지 않습니다. 시트 메뉴 [1. 🔑 API 키 설정]에서 입력해 주세요.' };
    var t = callAI('다음 문장을 그대로 한 번만 출력하세요: 연결 정상');
    if (!t) return { success: false, message: 'API 호출에 실패했습니다. 키 오타, 할당량 초과, 모델명(' + cfg.geminiModel + ') 단종 여부를 확인해 주세요.' };
    return { success: true, message: '✅ 연결 정상 (' + (cfg.selectedAI === 'Upstage' ? cfg.upstageModel : cfg.geminiModel) + ')', sample: t.substring(0, 40) };
  } catch (e) {
    return { success: false, message: e.message || String(e) };
  }
}


// ═══════════════════════════════════════════════════════════════════
//  14. 프롬프트 / 후처리
// ═══════════════════════════════════════════════════════════════════

function getTemplateGuidelines() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET.TEMPLATE);
  if (!sheet || sheet.getLastRow() <= 1) return '(교사 지침 없음 — 기본 양식으로 생성)';

  var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 2).getValues();
  var lines = [];
  for (var i = 0; i < data.length; i++) {
    if (data[i][0] || data[i][1]) lines.push('- [' + (data[i][0] || '') + '] ' + (data[i][1] || ''));
  }
  return lines.length ? lines.join('\n') : '(교사 지침 없음 — 기본 양식으로 생성)';
}

/** [FIX #23] 실명·학번을 가명 토큰으로 치환 */
function maskPii_(text, studentName) {
  var t = String(text || '').replace(/\d{4,5}/g, '');
  if (studentName) t = t.replace(new RegExp(escapeRe_(studentName), 'g'), NAME_TOKEN);
  return t.replace(/\s{2,}/g, ' ').trim();
}

function escapeRe_(s) {
  return String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/** [FIX #10] 분량 미달 방지 — 목표의 90% 이상을 채우도록 명시 */
function buildSeteukPrompt(nameToken, domain, subject, competency, bytesTarget, obsText, guidelines) {
  var charTarget = Math.floor(bytesTarget / 3);
  var minChars = Math.floor(charTarget * 0.9);
  var label = (domain === '교과') ? ('교과 세특 (' + subject + ')')
            : (domain === '행특') ? '행동특성 및 종합의견'
            : (domain + ' 활동 특기사항');

  return '당신은 대한민국 고등학교 생활기록부 작성 전문 AI입니다.\n\n' +
    '[작성 영역] ' + label + '\n' +
    '[강조 역량] ' + competency + '\n' +
    '[목표 분량] ' + minChars + '자 이상 ' + charTarget + '자 이내 (한글 기준 ' + bytesTarget + ' Bytes 이내)\n\n' +
    '[교사 맞춤 작성 지침]\n' + guidelines + '\n\n' +
    '[대상 학생] ' + nameToken + ' (개인정보 보호를 위해 익명 처리됨)\n' +
    '[관찰 기록]\n' + obsText + '\n\n' +
    '아래 규칙을 반드시 지켜 초안을 작성하세요.\n\n' +
    '1. 모든 문장을 ~함., ~임., ~됨. 등 명사형 종결어미로 마무리할 것\n' +
    '2. ' + competency + ' 이(가) 자연스럽게 드러나도록 구체적 탐구 사례를 서술할 것\n' +
    '3. 다음은 절대 사용 금지: 대회, 수상, 등급, 점수, 장학금, 특정 대학명, 기업 상호명, 강사명, 도서 출간 사실, 교외 활동, 부모 직업\n' +
    '4. 특정 지역명은 \'우리 지역\'으로, 학교 고유 행사명은 \'교내 행사\'로 바꿔 쓸 것\n' +
    '5. 관찰 기록에 없는 내용을 지어내지 말 것\n' +
    '6. 학생을 지칭할 때는 ' + nameToken + ' 을 그대로 사용할 것 (다른 이름을 만들지 말 것)\n' +
    '7. 본문만 출력할 것 — 제목, 머리말, 구분선, 마크다운 기호, 부가 설명 금지\n' +
    '8. 반드시 ' + minChars + '자 이상 ' + charTarget + '자 이내로 작성하고, 마지막 문장을 완전하게 마무리할 것';
}

function byteLen_(s) {
  return Utilities.newBlob(String(s == null ? '' : s)).getBytes().length;
}

/**
 * [FIX #10] v2.0은 문장 단위로만 잘라 목표의 35~59%밖에 채우지 못했습니다.
 * (실측: 900B 목표 → 528B, 1500B 목표 → 528B)
 * v2.1은 ① 문장으로 최대한 채우고 ② 남은 공간을 다음 문장의 어절로 채운 뒤
 * ③ '~함.' 으로 마무리합니다. 첫 문장부터 초과하는 경우에만 이진 탐색으로
 * 자르므로 글자 단위 while 루프(느림)를 타지 않습니다.
 */
function trimToBytes(text, maxBytes) {
  if (!text) return '';
  var max = parseInt(maxBytes, 10);
  if (!max || max < 60) max = 900;

  var t = String(text).replace(/\s+/g, ' ').trim();
  if (byteLen_(t) <= max) return t;

  var sents = t.match(/[^.!?]+[.!?]+/g);
  if (!sents || !sents.length) sents = [t];

  var out = '', idx = 0;
  for (; idx < sents.length; idx++) {
    if (byteLen_(out + sents[idx]) > max) break;
    out += sents[idx];
  }

  // 남은 공간을 어절 단위로 채우고 '함.' 으로 종결
  if (idx < sents.length) {
    var words = sents[idx].trim().split(/\s+/);
    var filled = out;
    for (var w = 0; w < words.length; w++) {
      var cand = filled + ((filled && !/\s$/.test(filled)) ? ' ' : '') + words[w];
      if (byteLen_(cand.replace(/[,\s]+$/, '') + '함.') > max) break;
      filled = cand;
    }
    if (filled !== out) out = filled.replace(/[,\s]+$/, '') + '함.';
  }

  if (out) return out.trim();

  // 첫 문장조차 한도를 넘는 극단 케이스 — 이진 탐색
  var lo = 0, hi = t.length;
  while (lo < hi) {
    var mid = Math.ceil((lo + hi) / 2);
    if (byteLen_(t.slice(0, mid) + '함.') <= max) lo = mid; else hi = mid - 1;
  }
  return t.slice(0, lo).replace(/[,\s]+$/, '') + '함.';
}

/** [FIX #11] 받침 판정 — "해결력를", "사고력를" 오류 수정 */
function josaEulReul_(word) {
  var w = String(word || '').trim();
  if (!w) return '를';
  var ch = w.charCodeAt(w.length - 1);
  if (ch < 0xAC00 || ch > 0xD7A3) return '를';
  return ((ch - 0xAC00) % 28) ? '을' : '를';
}

/**
 * [FIX #12] AI 실패 시 대체 문장.
 * v2.0은 음성 원문("어 그러니까 발표를 좀")을 그대로 이어붙여 구어체가
 * 생기부 초안에 들어갔습니다. v2.1은 간투사·군말을 걸러냅니다.
 */
function buildFallbackReport(nameToken, subject, competency, observations, realName) {
  var FILLER = /(^|\s)(어+|음+|그+니까|그러니까|저기|뭐지|아니|잠깐|자|응|네|예)(\s|$)/g;

  var snippets = (observations || []).slice(0, 4).map(function (o) {
    var t = String(o.memo || o.rawMemo || '');
    t = t.replace(/\d{4,5}/g, '');
    if (realName) t = t.replace(new RegExp(escapeRe_(realName), 'g'), '');
    t = t.replace(FILLER, ' ').replace(/\s{2,}/g, ' ').replace(/[.。]+$/, '').trim();
    return t.length >= 4 ? t : '';
  }).filter(Boolean);

  var particle = josaEulReul_(competency);
  var body = snippets.length
    ? snippets.join(', ') + ' 등의 활동을 자기주도적으로 수행함.'
    : '수업 활동에 성실히 참여함.';

  return nameToken + ' 학생은 ' + subject + ' 수업에서 ' + competency + particle +
         ' 바탕으로 ' + body +
         ' 수업 참여 태도가 긍정적이며 모둠 활동에서 협력적 의사소통 역량이 드러남.' +
         ' ※ 이 문장은 AI 호출 실패로 자동 생성된 임시 초안이므로 반드시 교사가 검토·수정해야 함.';
}


// ═══════════════════════════════════════════════════════════════════
//  15. [FIX #12] 생성 로그
// ═══════════════════════════════════════════════════════════════════

function log_(kind, target, message) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET.LOG);
    if (!sheet) return;
    sheet.appendRow([Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd HH:mm:ss'), kind, target, message]);
    // 로그가 2000행을 넘으면 오래된 것부터 정리
    if (sheet.getLastRow() > 2000) sheet.deleteRows(2, 500);
  } catch (e) {}
}


// ═══════════════════════════════════════════════════════════════════
//  16. 💬 텔레그램 완료 알림 (선택 기능)
// ═══════════════════════════════════════════════════════════════════
/**
 *  300명 세특 생성은 수 분이 걸리므로, 끝나면 휴대폰으로 알려주면 편합니다.
 *
 *  ⚠️ 봇 토큰은 절대 코드에 적지 마세요.
 *     아래 [9. 💬 텔레그램 완료 알림 설정] 메뉴에서 입력하면
 *     PropertiesService(구글 암호화 저장소)에만 저장됩니다.
 *
 *  준비 방법 (5분):
 *   1) 텔레그램에서 @BotFather 검색 → /newbot → 봇 이름 입력 → 토큰 발급
 *   2) 만든 봇과 대화 시작 후 아무 메시지나 전송
 *   3) 브라우저에서 https://api.telegram.org/bot<토큰>/getUpdates 열기
 *      → result[0].message.chat.id 숫자가 chat_id
 *   4) 시트 메뉴 [9. 💬 텔레그램 완료 알림 설정]에 토큰과 chat_id 입력
 */

function getTelegramConfig_() {
  var p = PropertiesService.getScriptProperties();
  return {
    token:  p.getProperty('TELEGRAM_BOT_TOKEN') || '',
    chatId: p.getProperty('TELEGRAM_CHAT_ID') || '',
    enabled: !!(p.getProperty('TELEGRAM_BOT_TOKEN') && p.getProperty('TELEGRAM_CHAT_ID'))
  };
}

function notifyTelegram_(text) {
  var tg = getTelegramConfig_();
  if (!tg.enabled) return false;
  try {
    var res = UrlFetchApp.fetch('https://api.telegram.org/bot' + tg.token + '/sendMessage', {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({ chat_id: tg.chatId, text: text, parse_mode: 'HTML' }),
      muteHttpExceptions: true
    });
    if (res.getResponseCode() !== 200) {
      Logger.log('텔레그램 전송 실패 ' + res.getResponseCode() + ': ' + res.getContentText().substring(0, 200));
      return false;
    }
    return true;
  } catch (e) {
    Logger.log('텔레그램 전송 에러: ' + e);
    return false;
  }
}

function setTelegramPrompt() {
  var ui = SpreadsheetApp.getUi();
  var p = PropertiesService.getScriptProperties();

  ui.alert('💬 텔레그램 완료 알림 설정\n\n' +
    '[준비]\n' +
    '1. 텔레그램에서 @BotFather 검색 → /newbot → 토큰 발급\n' +
    '2. 만든 봇과 대화를 시작하고 아무 메시지나 보내기\n' +
    '3. 브라우저에서 아래 주소 열기\n' +
    '   https://api.telegram.org/bot<발급받은토큰>/getUpdates\n' +
    '4. result[0].message.chat.id 숫자를 메모\n\n' +
    '이어서 토큰과 chat_id를 입력받습니다.\n' +
    '입력값은 구글 암호화 저장소에만 저장되며 시트에는 남지 않습니다.');

  var r1 = ui.prompt('💬 [1/2] 봇 토큰',
                     '@BotFather가 준 토큰을 붙여넣으세요.\n(비우고 확인하면 알림이 해제됩니다)',
                     ui.ButtonSet.OK_CANCEL);
  if (r1.getSelectedButton() !== ui.Button.OK) return;

  var token = r1.getResponseText().trim();
  if (!token) {
    p.deleteProperty('TELEGRAM_BOT_TOKEN');
    p.deleteProperty('TELEGRAM_CHAT_ID');
    ui.alert('텔레그램 알림이 해제되었습니다.');
    return;
  }
  if (!/^\d+:[A-Za-z0-9_-]{20,}$/.test(token)) {
    ui.alert('토큰 형식이 올바르지 않습니다.\n예: 1234567890:AAH...형태여야 합니다.');
    return;
  }

  var r2 = ui.prompt('💬 [2/2] chat_id', 'getUpdates에서 확인한 chat.id 숫자를 입력하세요:', ui.ButtonSet.OK_CANCEL);
  if (r2.getSelectedButton() !== ui.Button.OK) return;
  var chatId = r2.getResponseText().trim();
  if (!/^-?\d+$/.test(chatId)) { ui.alert('chat_id는 숫자여야 합니다.'); return; }

  p.setProperty('TELEGRAM_BOT_TOKEN', token);
  p.setProperty('TELEGRAM_CHAT_ID', chatId);

  var ok = notifyTelegram_('✅ <b>모바일 생생세특 ' + VERSION + '</b>\n텔레그램 알림이 연결되었습니다.');
  ui.alert(ok ? '🎉 연결 성공! 텔레그램을 확인해 보세요.\n\n이제 세특 생성이 끝나면 자동으로 알림이 갑니다.'
              : '⚠️ 저장은 되었지만 전송에 실패했습니다.\n토큰과 chat_id를 다시 확인해 주세요.\n(봇과 먼저 대화를 시작해야 chat_id가 생깁니다)');
}

function testTelegramMenu() {
  var ui = SpreadsheetApp.getUi();
  var tg = getTelegramConfig_();
  if (!tg.enabled) { ui.alert('먼저 [9. 💬 텔레그램 완료 알림 설정]을 진행해 주세요.'); return; }
  var ok = notifyTelegram_('📨 <b>테스트 메시지</b>\n모바일 생생세특 ' + VERSION + ' 알림이 정상 동작합니다.\n' +
                           Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd HH:mm'));
  ui.alert(ok ? '✅ 전송했습니다. 텔레그램을 확인해 보세요.' : '❌ 전송 실패. 토큰/chat_id를 확인해 주세요.');
}

/** 대시보드에서 호출하는 상태 확인용 */
function getTelegramStatus() {
  try { assertPin_(); return { success: true, enabled: getTelegramConfig_().enabled }; }
  catch (e) { return { success: false, enabled: false }; }
}
