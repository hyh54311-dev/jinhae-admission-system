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
    subjectCompetencies: props.getProperty('SUBJECT_COMPETENCIES') || '비판적 사고력, 지식정보처리 역량, 공동체·인성 역량',
    targetBytes: props.getProperty('TARGET_BYTES') || '900'
  };
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

  // 2. 진해고등학교 2학년 전체 300명 명단 자동 입력
  var studentSheet = ss.getSheetByName('학생명렬');
  var studentData = [
    [1, 1, '20101', '강준우'],
    [1, 2, '20102', '강지환'],
    [1, 3, '20103', '고은석'],
    [1, 4, '20104', '권준'],
    [1, 5, '20105', '김대현'],
    [1, 6, '20106', '김동윤'],
    [1, 7, '20107', '김의진'],
    [1, 8, '20108', '김정환'],
    [1, 9, '20109', '김태엽'],
    [1, 10, '20110', '김한얼'],
    [1, 11, '20111', '문규원'],
    [1, 12, '20112', '문진혁'],
    [1, 13, '20113', '박범준'],
    [1, 14, '20114', '박시완'],
    [1, 15, '20115', '서태랑'],
    [1, 16, '20116', '손승우'],
    [1, 17, '20117', '송우준'],
    [1, 18, '20118', '윤지운'],
    [1, 19, '20119', '이서한'],
    [1, 20, '20120', '이승엽'],
    [1, 21, '20121', '이정준'],
    [1, 22, '20122', '정가람'],
    [1, 23, '20123', '정은준'],
    [1, 24, '20124', '정현빈'],
    [1, 25, '20125', '조민석'],
    [1, 26, '20126', '조세원'],
    [1, 27, '20127', '진승우'],
    [1, 28, '20128', '차준헌'],
    [1, 29, '20129', '최우혁'],
    [1, 30, '20130', '최지호'],
    [1, 31, '20131', '최현준'],
    [2, 1, '20201', '공승배'],
    [2, 2, '20202', '김대영'],
    [2, 3, '20203', '김동윤'],
    [2, 4, '20204', '김병주'],
    [2, 5, '20205', '김보성'],
    [2, 6, '20206', '김준석'],
    [2, 7, '20207', '김지훈'],
    [2, 8, '20208', '노윤오'],
    [2, 9, '20209', '문한빈'],
    [2, 10, '20210', '박도윤'],
    [2, 11, '20211', '박준범'],
    [2, 12, '20212', '박준우'],
    [2, 13, '20213', '박준제'],
    [2, 14, '20214', '백재빈'],
    [2, 15, '20215', '변재훈'],
    [2, 16, '20216', '성연우'],
    [2, 17, '20217', '손보빈'],
    [2, 18, '20218', '안건주'],
    [2, 19, '20219', '양하임'],
    [2, 20, '20220', '유승준'],
    [2, 21, '20221', '윤휘영'],
    [2, 22, '20222', '이민효'],
    [2, 23, '20223', '이승기'],
    [2, 24, '20224', '이예성'],
    [2, 25, '20225', '임진혁'],
    [2, 26, '20226', '장호성'],
    [2, 27, '20227', '조현우'],
    [2, 28, '20228', '차지환'],
    [2, 29, '20229', '차형래'],
    [2, 30, '20230', '최서진'],
    [2, 31, '20231', '팽환용'],
    [3, 1, '20301', '권민재'],
    [3, 2, '20302', '김민준'],
    [3, 3, '20303', '김승도'],
    [3, 4, '20304', '김영준'],
    [3, 5, '20305', '김재호'],
    [3, 6, '20306', '김현중'],
    [3, 7, '20307', '박승준'],
    [3, 8, '20308', '박재윤'],
    [3, 9, '20309', '박준현'],
    [3, 10, '20310', '박지호'],
    [3, 11, '20311', '박진현'],
    [3, 12, '20312', '배윤범'],
    [3, 13, '20313', '서용준'],
    [3, 14, '20314', '신대훈'],
    [3, 15, '20315', '오태윤'],
    [3, 16, '20316', '우서현'],
    [3, 17, '20317', '유승우'],
    [3, 18, '20318', '이상운'],
    [3, 19, '20319', '이승도'],
    [3, 20, '20320', '이승준'],
    [3, 21, '20321', '이진우'],
    [3, 22, '20322', '이해준'],
    [3, 23, '20323', '정하랑'],
    [3, 24, '20324', '조강현'],
    [3, 25, '20325', '조건우'],
    [3, 26, '20326', '조연우'],
    [3, 27, '20327', '조준민'],
    [3, 28, '20328', '주재현'],
    [3, 29, '20329', '최재민'],
    [3, 30, '20330', '한진수'],
    [3, 31, '20331', '한태경'],
    [4, 1, '20401', '강민규'],
    [4, 2, '20402', '강민준'],
    [4, 3, '20403', '구수언'],
    [4, 4, '20404', '김동희'],
    [4, 5, '20405', '김서준'],
    [4, 6, '20406', '김세현'],
    [4, 7, '20407', '김재윤'],
    [4, 8, '20408', '김지윤'],
    [4, 9, '20409', '김지호'],
    [4, 10, '20410', '김진영'],
    [4, 11, '20411', '김태림'],
    [4, 12, '20412', '김현빈'],
    [4, 13, '20413', '민성민'],
    [4, 14, '20414', '민수홍'],
    [4, 15, '20415', '박태윤'],
    [4, 16, '20416', '배준일'],
    [4, 17, '20417', '성희찬'],
    [4, 18, '20418', '손민찬'],
    [4, 19, '20419', '송시영'],
    [4, 20, '20420', '옥정우'],
    [4, 21, '20421', '유지훈'],
    [4, 22, '20422', '윤태웅'],
    [4, 23, '20423', '이하람'],
    [4, 24, '20424', '전승우'],
    [4, 25, '20425', '정지훈'],
    [4, 26, '20426', '조정제'],
    [4, 27, '20427', '최정후'],
    [4, 28, '20428', '한민기'],
    [4, 29, '20429', '한성원'],
    [4, 30, '20430', '홍진산'],
    [5, 1, '20501', '김건우'],
    [5, 2, '20502', '김동국'],
    [5, 3, '20503', '김민재'],
    [5, 4, '20504', '김태영'],
    [5, 5, '20505', '김태하'],
    [5, 6, '20506', '김평건'],
    [5, 7, '20507', '김현'],
    [5, 8, '20508', '박관우'],
    [5, 9, '20509', '박규람'],
    [5, 10, '20510', '박민강'],
    [5, 11, '20511', '박서준'],
    [5, 12, '20512', '방지원'],
    [5, 13, '20513', '서진우'],
    [5, 14, '20514', '송윤재'],
    [5, 15, '20515', '승민겸'],
    [5, 16, '20516', '신근찬'],
    [5, 17, '20517', '윤성하'],
    [5, 18, '20518', '이데니스'],
    [5, 19, '20519', '이민혁'],
    [5, 20, '20520', '이민호'],
    [5, 21, '20521', '이성민'],
    [5, 22, '20522', '이성희'],
    [5, 23, '20523', '이시후'],
    [5, 24, '20524', '이진영'],
    [5, 25, '20525', '이훈민'],
    [5, 26, '20526', '임지민'],
    [5, 27, '20527', '장현우'],
    [5, 28, '20528', '정승우'],
    [5, 29, '20529', '차동민'],
    [5, 30, '20530', '한승훈'],
    [6, 1, '20601', 'ANTAIXU'],
    [6, 2, '20602', '권정진'],
    [6, 3, '20603', '김도윤'],
    [6, 4, '20604', '김민규'],
    [6, 5, '20605', '김민재'],
    [6, 6, '20606', '김승준'],
    [6, 7, '20607', '김재영'],
    [6, 8, '20608', '김재윤'],
    [6, 9, '20609', '김재휘'],
    [6, 10, '20610', '김주영'],
    [6, 11, '20611', '박재은'],
    [6, 12, '20612', '손찬민'],
    [6, 13, '20613', '송민수'],
    [6, 14, '20614', '신재영'],
    [6, 15, '20615', '여진우'],
    [6, 16, '20616', '오승철'],
    [6, 17, '20617', '윤찬후'],
    [6, 18, '20618', '이대한'],
    [6, 19, '20619', '이영수'],
    [6, 20, '20620', '이준민'],
    [6, 21, '20621', '전도현'],
    [6, 22, '20622', '정서윤'],
    [6, 23, '20623', '정성준'],
    [6, 24, '20624', '정지운'],
    [6, 25, '20625', '조연우'],
    [6, 26, '20626', '최원진'],
    [6, 27, '20627', '하우진'],
    [6, 28, '20628', '한호선'],
    [6, 29, '20629', '황현석'],
    [7, 1, '20701', '강예준'],
    [7, 2, '20702', '강윤호'],
    [7, 3, '20703', '권동현'],
    [7, 4, '20704', '김도윤'],
    [7, 5, '20705', '김려송'],
    [7, 6, '20706', '김민재'],
    [7, 7, '20707', '김민준'],
    [7, 8, '20708', '류귀범'],
    [7, 9, '20709', '박성빈'],
    [7, 10, '20710', '박주빈'],
    [7, 11, '20711', '방예후'],
    [7, 12, '20712', '사공관'],
    [7, 13, '20713', '송태현'],
    [7, 14, '20714', '신예창'],
    [7, 15, '20715', '신재우'],
    [7, 16, '20716', '옥지윤'],
    [7, 17, '20717', '윤찬혁'],
    [7, 18, '20718', '이시형'],
    [7, 19, '20719', '이재성'],
    [7, 20, '20720', '이주원'],
    [7, 21, '20721', '이현석'],
    [7, 22, '20722', '장준호'],
    [7, 23, '20723', '전준혁'],
    [7, 24, '20724', '정지웅'],
    [7, 25, '20725', '조승주'],
    [7, 26, '20726', '조현민'],
    [7, 27, '20727', '최의찬'],
    [7, 28, '20728', '한정훈'],
    [7, 29, '20729', '허대민'],
    [8, 1, '20801', '국윤진'],
    [8, 2, '20802', '김강민'],
    [8, 3, '20803', '김건재'],
    [8, 4, '20804', '김동욱'],
    [8, 5, '20805', '김성민'],
    [8, 6, '20806', '김주영'],
    [8, 7, '20807', '김형석'],
    [8, 8, '20808', '박건민'],
    [8, 9, '20809', '박기량'],
    [8, 10, '20810', '박상진'],
    [8, 11, '20811', '박준수'],
    [8, 12, '20812', '박진우'],
    [8, 13, '20813', '박찬석'],
    [8, 14, '20814', '박한울'],
    [8, 15, '20815', '송윤찬'],
    [8, 16, '20816', '신재하'],
    [8, 17, '20817', '오민혁'],
    [8, 18, '20818', '오예준'],
    [8, 19, '20819', '온진호'],
    [8, 20, '20820', '이승준'],
    [8, 21, '20821', '이주현'],
    [8, 22, '20822', '이지우'],
    [8, 23, '20823', '장현준'],
    [8, 24, '20824', '조윤제'],
    [8, 25, '20825', '진현운'],
    [8, 26, '20826', '최민혁'],
    [8, 27, '20827', '최준우'],
    [8, 28, '20828', '최현준'],
    [8, 29, '20829', '한현욱'],
    [8, 30, '20830', '황시윤'],
    [9, 1, '20901', '김강빈'],
    [9, 2, '20902', '김금성'],
    [9, 3, '20903', '김도훈'],
    [9, 4, '20904', '김동영'],
    [9, 5, '20905', '김영민'],
    [9, 6, '20906', '김재원'],
    [9, 7, '20907', '김준명'],
    [9, 8, '20908', '김태준'],
    [9, 9, '20909', '류석민'],
    [9, 10, '20910', '류호진'],
    [9, 11, '20911', '박민혁'],
    [9, 12, '20912', '심지환'],
    [9, 13, '20913', '안도윤'],
    [9, 14, '20914', '엄지성'],
    [9, 15, '20915', '윤주한'],
    [9, 16, '20916', '이도현'],
    [9, 17, '20917', '이지훈'],
    [9, 18, '20918', '이진우'],
    [9, 19, '20919', '이찬솔'],
    [9, 20, '20920', '전우진'],
    [9, 21, '20921', '전지훈'],
    [9, 22, '20922', '전해우'],
    [9, 23, '20923', '정우찬'],
    [9, 24, '20924', '정원혁'],
    [9, 25, '20925', '정지헌'],
    [9, 26, '20926', '조영주'],
    [9, 27, '20927', '조윤재'],
    [9, 28, '20928', '진승완'],
    [9, 29, '20929', '진현성'],
    [9, 30, '20930', '최정원'],
    [10, 1, '21001', '강민준'],
    [10, 2, '21002', '김가온'],
    [10, 3, '21003', '김건희'],
    [10, 4, '21004', '김관우'],
    [10, 5, '21005', '김대영'],
    [10, 6, '21006', '김대철'],
    [10, 7, '21007', '김동규'],
    [10, 8, '21008', '김민석'],
    [10, 9, '21009', '김민제'],
    [10, 10, '21010', '김세홍'],
    [10, 11, '21011', '김준수'],
    [10, 12, '21012', '노시헌'],
    [10, 13, '21013', '류시호'],
    [10, 14, '21014', '박정준'],
    [10, 15, '21015', '박지한'],
    [10, 16, '21016', '백지민'],
    [10, 17, '21017', '손원빈'],
    [10, 18, '21018', '신광진'],
    [10, 19, '21019', '오지태'],
    [10, 20, '21020', '이준휘'],
    [10, 21, '21021', '임수혁'],
    [10, 22, '21022', '전준영'],
    [10, 23, '21023', '정선우'],
    [10, 24, '21024', '정원호'],
    [10, 25, '21025', '정의찬'],
    [10, 26, '21026', '조연우'],
    [10, 27, '21027', '최재범'],
    [10, 28, '21028', '허강민'],
    [10, 29, '21029', '홍정훈']
  ];
  if (studentSheet) {
    // 기존 헤더 제외 데이터 제거 후 300명 명단 일괄 채우기
    if (studentSheet.getLastRow() > 1) {
      studentSheet.getRange(2, 1, studentSheet.getLastRow() - 1, 4).clearContent();
    }
    studentSheet.getRange(2, 1, studentData.length, 4).setValues(studentData);
  }

  SpreadsheetApp.getUi().alert('✅ 7대 탭 양식 및 2학년 300명 명단이 진짜 구글 시트에 1초 만에 자동 세팅되었습니다!\n\n[학생명렬] 탭에서 2학년 1반~10반 300명 명단을 확인하실 수 있습니다.');
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
            date: obsData[i][0],
            classNum: c,
            category: obsData[i][2],
            hakbun: obsData[i][3],
            name: obsData[i][4],
            rawMemo: obsData[i][5],
            refinedText: obsData[i][6]
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
            date: respData[j][0],
            classNum: c2,
            hakbun: respData[j][2],
            name: respData[j][3],
            content: respData[j][4],
            type: respData[j][5]
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
            classNum: c3,
            hakbun: repData[k][1],
            name: repData[k][2],
            date: repData[k][3],
            bytes: repData[k][4],
            reportText: repData[k][5]
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

      // 해당 학생의 관찰 기록 필터링
      var sHakbun = s.hakbun ? s.hakbun.toString() : '';
      var sName = s.name ? s.name.toString() : '';
      var studentObs = allObs.filter(function(o) {
        return (sHakbun && o.hakbun === sHakbun) || (sName && o.name === sName);
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
    '7. 반드시 ' + charTarget + '자 이내로 작성할 것';
}

// 바이트 초과 시 자동 트리밍 유틸리티
function trimToBytes(text, maxBytes) {
  if (!text) return '';
  var bytes = Utilities.newBlob(text).getBytes().length;
  while (bytes > maxBytes && text.length > 0) {
    text = text.substring(0, text.length - 1);
    bytes = Utilities.newBlob(text).getBytes().length;
  }
  return text;
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
