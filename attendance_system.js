/**
 * 2026학년도 진해고등학교 3학년 출석 시스템 (완전 자동화 및 맞춤형 스마트 버전)
 * - 상단 메뉴 버튼 삭제 (트리거 충돌 방지)
 * - 요일 한글 강제 고정 로직 (GMT+9 타임존 완전 무결 설계)
 * - 조퇴/결과 세분화 및 자퇴 추가 (총 12종 드롭다운 옵션 즉시 반영)
 * - 자퇴/위탁교육 학생 식별 시 오늘 열 생성 시 자동 기본값 입력 적용
 * - A열(학번), B열(이름) 및 확정된 출결 데이터 100% 안전 보호 보장
 */

// 매일 자정에 트리거로 실행되거나, 수동으로 실행할 핵심 함수
function refreshAttendanceSystem() {
  let ss = null;
  
  // 1차 시도: 활성화된 스프레드시트 가져오기
  try {
    ss = SpreadsheetApp.getActiveSpreadsheet();
  } catch (e) {
    Logger.log("getActiveSpreadsheet 실패, 백업 ID 접근 시도: " + e.toString());
  }

  // 2차 백업 시도: 구글 서버 버그 예방용 ID 직접 오픈 (100% 안전 보장)
  if (!ss) {
    const spreadsheetId = "1iIM8J_tG6-E77bjvkTX5HJpJJnCS6WHl7hwTmTWJync";
    ss = SpreadsheetApp.openById(spreadsheetId);
  }

  const sheets = ss.getSheets();

  sheets.forEach(function(sheet) {
    const sheetName = sheet.getName();
    // 시트명에 "반"이 들어가는 학급 시트만 순회 처리
    if (sheetName.includes("반")) {
      cleanUpUnusedColumnsInSheet(sheet); // 1. 과거 열 정리 (속도 개선 버전)
      addTodayColumn(sheet);              // 2. 오늘 열 생성 및 스마트 기본값 입력
      SpreadsheetApp.flush();             // 구글 시트 강제 동기화
      applyDropdownRetroactively(sheet);  // 3. 전체 드롭다운 최신화 (12종 옵션)
    }
  });
}

function getKoreanDateStr() {
  const date = new Date();
  const mmdd = Utilities.formatDate(date, "GMT+9", "MM/dd");
  const dayNum = parseInt(Utilities.formatDate(date, "GMT+9", "u"), 10); // 1=월, ..., 7=일
  const days = ["", "월", "화", "수", "목", "금", "토", "일"];
  const dayName = days[dayNum];
  return `${mmdd}(${dayName})`; // 예: 05/20(수)
}

function cleanUpUnusedColumnsInSheet(sheet) {
  const todayStr = getKoreanDateStr(); 
  const lastCol = sheet.getLastColumn();
  if (lastCol < 3) return; 

  for (let col = lastCol; col >= 3; col--) {
    const dateValue = sheet.getRange(2, col).getDisplayValue(); 
    const isChecked = sheet.getRange(1, col).getValue();        
    
    // 과거 날짜 중 날짜가 비어있지 않고, 체크 안 된 열만 삭제
    if (dateValue !== "" && dateValue !== todayStr && isChecked === false) {
      sheet.deleteColumn(col);
    }
  }
}

function addTodayColumn(sheet) {
  const todayStr = getKoreanDateStr(); 
  let lastCol = sheet.getLastColumn();
  if (lastCol < 2) lastCol = 2;

  const dateRange = sheet.getRange(2, 1, 1, lastCol);
  const dateValues = dateRange.getDisplayValues()[0];

  let todayColIndex = -1;
  for (let i = 0; i < dateValues.length; i++) {
    if (dateValues[i] === todayStr) {
      todayColIndex = i + 1;
      break;
    }
  }

  // 오늘 날짜가 없다면 새로 생성
  if (todayColIndex === -1) {
    const newCol = lastCol + 1;

    // 빈 열 부족 시 삽입
    if (newCol > sheet.getMaxColumns()) {
      sheet.insertColumnAfter(lastCol);
    }

    sheet.getRange(1, newCol).insertCheckboxes();
    sheet.getRange(2, newCol)
         .setValue(todayStr)
         .setBackground("#e1f5fe")
         .setFontWeight("bold")
         .setHorizontalAlignment("center");
    
    sheet.setColumnWidth(newCol, 120);

    let lastRow = sheet.getLastRow();
    if (lastRow < 32) lastRow = 34; // 넉넉하게 기본 32명 보장

    // B열(학생 이름) 전체 데이터 읽어와 스마트 매칭 진행
    const studentNames = sheet.getRange(3, 2, lastRow - 2, 1).getValues();
    const defaultAttendance = [];

    for (let r = 0; r < studentNames.length; r++) {
      const name = studentNames[r][0] ? studentNames[r][0].toString().trim() : "";
      
      if (name === "") {
        defaultAttendance.push([""]); // 이름이 없는 빈 명렬 줄
      } else if (name.includes("자퇴")) {
        defaultAttendance.push(["자퇴"]); // 이름에 '자퇴' 키워드 매칭
      } else if (name.includes("위탁교육")) {
        defaultAttendance.push(["위탁교육"]); // 이름에 '위탁교육' 키워드 매칭
      } else {
        defaultAttendance.push(["출석"]); // 일반 학생 기본값
      }
    }

    // 신규 열에 맞춤형 기본값 일괄 고속 입력
    sheet.getRange(3, newCol, lastRow - 2, 1)
         .setValues(defaultAttendance)
         .setHorizontalAlignment("center");
  }
}

function applyDropdownRetroactively(sheet) {
  const lastCol = sheet.getLastColumn();
  if (lastCol <= 2) return;

  let lastRow = sheet.getLastRow();
  if (lastRow < 32) lastRow = 34; 

  const dropDownOptions = [
    "출석", "인정결석", "병결석", "미인정결석", 
    "인정조퇴", "병조퇴", "미인정조퇴", 
    "인정결과", "병결과", "미인정결과", 
    "위탁교육", "자퇴"
  ];

  const rule = SpreadsheetApp.newDataValidation()
                 .requireValueInList(dropDownOptions)
                 .setAllowInvalid(false)
                 .build();

  const attendanceRange = sheet.getRange(3, 3, lastRow - 2, lastCol - 2);
  attendanceRange.setDataValidation(rule);
}

// Node.js 모듈로 내보내기 (테스트 환경인 경우에만)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    refreshAttendanceSystem,
    getKoreanDateStr,
    cleanUpUnusedColumnsInSheet,
    addTodayColumn,
    applyDropdownRetroactively
  };
}
