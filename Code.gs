/**
 * 3학년 화법과작문 수행평가 답변 수집 시스템 - 백엔드
 * 
 * 제작: Antigravity
 * 목적: 학생들의 서답형 답변을 안전하고 깔끔하게 시트에 실시간 기록합니다.
 */

function doGet() {
  return HtmlService.createTemplateFromFile('Index')
      .evaluate()
      .setTitle('3학년 화법과작문 수행평가 답변 제출')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * '명렬' 시트에서 학급별 동적 드롭다운용 명렬 리스트를 로드합니다.
 * 시트가 수정되면 웹 앱에도 실시간으로 반영됩니다.
 */
function getRoster() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("명렬");
    if (!sheet) {
      return { success: false, error: "'명렬' 시트를 찾을 수 없습니다." };
    }
    
    var lastRow = sheet.getLastRow();
    if (lastRow < 2) {
      return {};
    }
    
    // 반, 번호, 이름 열(1~3열) 데이터 읽기
    var data = sheet.getRange(2, 1, lastRow - 1, 3).getValues();
    var roster = {};
    
    // 1반부터 10반까지 배열 초기화
    for (var b = 1; b <= 10; b++) {
      roster[b] = [];
    }
    
    for (var i = 0; i < data.length; i++) {
      var ban = parseInt(data[i][0]);
      var num = parseInt(data[i][1]);
      var name = data[i][2] ? data[i][2].toString().trim() : "";
      
      if (!isNaN(ban) && ban >= 1 && ban <= 10 && name) {
        roster[ban].push({
          num: num,
          name: name
        });
      }
    }
    
    // 번호순 정렬
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
 * 학생들이 제출한 수행평가 서답형 답안을 '수행평가_응답' 시트에 누적 기록합니다.
 */
function submitAnswer(formData) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("수행평가_응답");
    if (!sheet) {
      // 혹시 시트가 없으면 헤더행과 함께 생성
      sheet = ss.insertSheet("수행평가_응답");
      var headers = [
        "제출일시", "반", "번호", "이름",
        "16번 답변 (세런디피티)", 
        "17번 답변 (연구 수행자)", 
        "18번 답변 (개발 동기)", 
        "19번 답변 (페니실린 박테리아 억제)", 
        "20번 답변 (그람 음성균 효과 없음)"
      ];
      sheet.appendRow(headers);
    }
    
    var timestamp = new Date();
    var ban = parseInt(formData.ban);
    var num = parseInt(formData.num);
    var name = formData.name.trim();
    var q16 = formData.q16 ? formData.q16.trim() : "";
    var q17 = formData.q17 ? formData.q17.trim() : "";
    var q18 = formData.q18 ? formData.q18.trim() : "";
    var q19 = formData.q19 ? formData.q19.trim() : "";
    var q20 = formData.q20 ? formData.q20.trim() : "";
    
    // 입력 필수값 검증
    if (isNaN(ban) || isNaN(num) || !name) {
      return { success: false, error: "학급/번호/이름 정보가 유효하지 않습니다." };
    }
    
    // 새 답변 행 추가
    sheet.appendRow([
      timestamp,
      ban,
      num,
      name,
      q16,
      q17,
      q18,
      q19,
      q20
    ]);
    
    // 자동 스크롤/정렬을 돕기 위해 서식 강제 적용을 피하고 값만 추가
    return { success: true, message: name + " 학생의 답안이 성공적으로 저장되었습니다." };
  } catch (e) {
    return { success: false, error: e.toString() };
  }
}
