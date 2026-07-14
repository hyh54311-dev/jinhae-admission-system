/**
 * 2026학년도 입학생 3개년 교육과정 편성표 의견 수렴 커스텀 웹앱 - 백엔드
 * 
 * 제작: Antigravity
 * 목적: 구글 설문지 느낌이 나지 않는 세련된 단독 웹 애플리케이션으로 설문을 제공하며,
 *       제출된 답변을 연동된 스프레드시트에 직접 누적 저장합니다.
 */

function doGet() {
  // '교육과정_웹앱_화면.html' 파일을 로드하여 평가 및 웹앱 서빙
  return HtmlService.createTemplateFromFile('교육과정_웹앱_화면')
      .evaluate()
      .setTitle('2026학년도 입학생 3개년 교육과정 편성표 의견 수렴')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * 교사가 제출한 웹앱 설문 응답을 '교육과정_웹앱_응답' 시트에 실시간 기록합니다.
 * 
 * @param {Object} formData 제출된 설문 데이터 객체
 * @return {Object} 성공 여부 및 결과 메시지 객체
 */
function submitCurriculumResponse(formData) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("교육과정_웹앱_응답");
    
    // 시트가 없으면 신규 생성하고 헤더 배치
    if (!sheet) {
      sheet = ss.insertSheet("교육과정_웹앱_응답");
      var headers = [
        "제출일시", 
        "선생님 성함", 
        "최종 선택 안", 
        "1안 의견 및 건의사항", 
        "2안 의견 및 건의사항", 
        "3안 의견 및 건의사항", 
        "4안 의견 및 건의사항"
      ];
      sheet.appendRow(headers);
      
      // 디자인 가독성을 위해 첫 행 고정 및 굵은 글씨, 연회색 배경 지정
      sheet.getRange(1, 1, 1, headers.length)
           .setFontWeight("bold")
           .setBackground("#f1f5f9")
           .setHorizontalAlignment("center");
      sheet.setFrozenRows(1);
    }
    
    var timestamp = new Date();
    var name = formData.name ? formData.name.trim() : "";
    var selectedOption = formData.selectedOption || "";
    var opinion1 = formData.opinion1 ? formData.opinion1.trim() : "";
    var opinion2 = formData.opinion2 ? formData.opinion2.trim() : "";
    var opinion3 = formData.opinion3 ? formData.opinion3.trim() : "";
    var opinion4 = formData.opinion4 ? formData.opinion4.trim() : "";
    
    // 유효성 검사
    if (!name) {
      return { success: false, error: "선생님 성함이 선택되지 않았습니다." };
    }
    if (!selectedOption) {
      return { success: false, error: "선택하신 안이 없습니다. 한 가지 안을 반드시 선택해야 합니다." };
    }
    
    // 새 응답 행 삽입
    sheet.appendRow([
      timestamp,
      name,
      selectedOption,
      opinion1,
      opinion2,
      opinion3,
      opinion4
    ]);
    
    // 열 너비 자동 맞춤 조정 (시트 편의용)
    try {
      sheet.autoResizeColumns(1, 7);
    } catch (e) {
      // 자동 크기 조절 오류 시 무시
    }
    
    return { success: true, message: name + " 선생님의 의견이 성공적으로 기록되었습니다." };
  } catch (err) {
    return { success: false, error: err.toString() };
  }
}
