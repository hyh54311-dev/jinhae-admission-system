/**
 * 3학년 화법과작문 수행평가 - 구글 폼 자동 생성 스크립트 (구문 안정성 확보 버전)
 * 
 * [사용 방법]
 * 1. 이 스크립트를 실행하고자 하는 아무 구글 스프레드시트(예: 현재 열려있는 새 시트)를 엽니다.
 * 2. 상단 메뉴에서 [확장 프로그램] -> [Apps Script]를 클릭합니다.
 * 3. 기존 코드를 모두 지우고 이 스크립트 전체를 복사하여 붙여넣습니다.
 * 4. 상단의 [저장] 단추(디스켓 아이콘)를 클릭합니다.
 * 5. 실행 함수 목록에서 "createPerformanceAssessmentForm"을 선택한 후 [실행] 단추(재생 아이콘)를 누릅니다.
 * 6. 완료되면 구글 시트 화면에 팝업창이 뜨며 설문지 편집 링크와 학생용 배포 링크가 즉시 나타납니다!
 */

function createPerformanceAssessmentForm() {
  // 1. 현재 열려있는 활성 스프레드시트 (이 시트에 학생들의 답변이 저장됩니다)
  var ssActive = SpreadsheetApp.getActiveSpreadsheet();
  
  // 2. 명렬표가 들어있는 원본 출석부 스프레드시트의 고유 ID
  var rosterSpreadsheetId = "1-TMsohbrUwaifTPpnSbrlU72nOjqiPIvYbKluSjLBsk";
  var ssRoster;
  
  try {
    ssRoster = SpreadsheetApp.openById(rosterSpreadsheetId);
  } catch (err) {
    throw new Error(
      "원본 출석부 스프레드시트를 열 수 없습니다.\n" +
      "선생님의 구글 드라이브에 '2026학년도 3학년 1학기 독서(수능특강) 출석부' 파일이 존재하는지, " +
      "혹은 구글 스프레드시트 형식으로 정상 변환되었는지 확인해 주세요.\n(에러 세부사항: " + err.toString() + ")"
    );
  }
  
  var sheets = ssRoster.getSheets();
  var sheetNames = sheets.map(function(s) { return s.getName(); });
  
  // 3. 구글 설문지 생성 및 현재 활성 스프레드시트와 연동
  var form = FormApp.create("3학년 화법과작문 수행평가");
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ssActive.getId());
  form.setDescription("3학년 화법과작문 수행평가 서답형 답변 수집 양식입니다.\n자신의 반과 이름을 정확히 선택한 후 답변을 제출해 주세요.");
  
  // [1단계] 반 선택 문항 추가 (첫 번째 페이지)
  var classItem = form.addMultipleChoiceItem();
  classItem.setTitle("반을 선택해 주세요.").setRequired(true);
  
  var classSections = {};
  var classChoices = [];
  var skippedSheets = [];
  var parsedSummary = [];
  
  // [2단계] 원본 출석부 시트의 '1반'~'10반' 탭에서 실시간 학생 명단 로드 및 설문지 섹션 생성
  for (var b = 1; b <= 10; b++) {
    var sheetName = b + "반";
    var sheet = ssRoster.getSheetByName(sheetName);
    if (!sheet) {
      // 혹시 시트명에 공백이 들어갔을 경우를 대비한 유연한 매칭
      var matchedSheet = null;
      for (var s = 0; s < sheets.length; s++) {
        var cleanName = sheets[s].getName().replace(/\s+/g, "");
        if (cleanName === sheetName || cleanName === (b + "반")) {
          matchedSheet = sheets[s];
          sheetName = sheets[s].getName();
          break;
        }
      }
      sheet = matchedSheet;
    }
    
    if (!sheet) {
      skippedSheets.push(sheetName + " (시트 없음)");
      continue;
    }
    
    var lastRow = sheet.getLastRow();
    if (lastRow < 3) {
      skippedSheets.push(sheetName + " (행수가 3 미만: " + lastRow + ")");
      continue;
    }
    
    // A열(번호), B열(이름) 데이터 추출 (3행부터 데이터 시작)
    var numRange = sheet.getRange(3, 1, lastRow - 2, 1).getValues();
    var nameRange = sheet.getRange(3, 2, lastRow - 2, 1).getValues();
    
    var studentList = [];
    for (var i = 0; i < numRange.length; i++) {
      var num = numRange[i][0];
      var name = nameRange[i][0] ? nameRange[i][0].toString().trim() : "";
      if (num !== "" && num !== null && name !== "") {
        // 번호로 변환 가능한 경우만 추가
        var parsedNum = parseInt(num);
        if (!isNaN(parsedNum)) {
          studentList.push(parsedNum + "번 " + name);
        }
      }
    }
    
    if (studentList.length === 0) {
      skippedSheets.push(sheetName + " (학생 정보 없음: A열 번호, B열 이름 확인 필)");
      continue;
    }
    
    // 번호 순서로 오름차순 정렬
    studentList.sort(function(x, y) {
      return parseInt(x.split("번")[0]) - parseInt(y.split("번")[0]);
    });
    
    // 학급별 이름 선택용 전용 섹션(Page Break) 생성
    var sec = form.addPageBreakItem().setTitle("3학년 " + b + "반 이름 선택");
    var nameItem = form.addMultipleChoiceItem().setTitle("자신의 이름을 선택해 주세요.").setRequired(true);
    nameItem.setChoiceValues(studentList);
    
    classSections[b] = sec;
    classChoices.push(classItem.createChoice(b + "반", sec));
    parsedSummary.push(b + "반 (" + studentList.length + "명)");
  }
  
  // 만약 명렬 시트가 단 하나도 로드되지 않았다면 상세한 원인 설명 후 중단
  if (classChoices.length === 0) {
    var errorMsg = "원본 출석부 시트에서 학급 정보를 찾지 못했습니다.\n\n" +
                   "[진단 결과]\n" +
                   "1. 원본 출석부 내 시트 목록: " + JSON.stringify(sheetNames) + "\n" +
                   "2. 제외된 이유들:\n- " + skippedSheets.join("\n- ") + "\n\n" +
                   "[해결 방법]\n" +
                   "- 원본 출석부 파일의 각 시트의 A열 3행부터 번호, B열 3행부터 학생 이름이 들어있는지 확인해 주세요.";
    throw new Error(errorMsg);
  }
  
  // [3단계] 수행평가 문항 섹션 추가 (반드시 명렬 섹션들보다 뒤에 추가해야 폼의 가장 마지막 페이지가 됩니다!)
  var qSection = form.addPageBreakItem()
      .setTitle("수행평가 서술형 문항")
      .setHelpText("각 문항에 맞게 답안을 작성해 주세요. 글자 수 제한이 없으나 조리 있고 논리적으로 작성해 주시기 바랍니다.");
  
  var q16 = form.addParagraphTextItem().setTitle("16. 세런디피티의 개념을 한 문장으로 쓰시오.").setRequired(true);
  var q17 = form.addParagraphTextItem().setTitle("17. <보기>의 연구를 수행한 사람의 이름을 쓰시오.").setRequired(true);
  var q18 = form.addParagraphTextItem().setTitle("18. 플레이밍이 항박테리아 제제를 개발하려는 동기가 약했던 까닭을 두 가지를 <조건>에 맞게 쓰시오.").setRequired(true);
  var q19 = form.addParagraphTextItem().setTitle("19. 페니실린이 박테리아를 억제하는 까닭을 조건에 맞게 서술하시오.").setRequired(true);
  var q20 = form.addParagraphTextItem().setTitle("20. 그람 음성균이 페니실린에 효과가 없는 까닭을 <조건>에 맞게 서술하시오.").setRequired(true);
  
  // [4단계] 각 반 이름 선택 섹션에서 다음을 누르면 무조건 마지막 질문 섹션으로 건너뛰도록 분기 경로 일괄 지정
  for (var b = 1; b <= 10; b++) {
    if (classSections[b]) {
      classSections[b].setGoToPage(qSection);
    }
  }
  
  // [5단계] 1페이지의 반 선택 시, 해당 반의 이름 선택 페이지로 점프하도록 1단계 문항의 이동 경로 연결
  classItem.setChoices(classChoices);
  
  Logger.log("구글 설문지 생성 성공!");
  Logger.log("설문지 편집 링크: " + form.getEditUrl());
  Logger.log("설문지 배포 링크 (학생 공유용): " + form.getPublishedUrl());
  
  // 구글 시트 내에 모달창으로 완료 안내 및 링크 표시
  var htmlOutput = HtmlService.createHtmlOutput(
    "<div style='font-family: sans-serif; padding: 15px; line-height: 1.6; font-size: 14px;'>" +
    "<h3 style='color: #1e3a8a; border-bottom: 2px solid #3b82f6; padding-bottom: 8px;'>[완료] 구글 설문지(Google Form) 생성 완료!</h3>" +
    "<p style='margin: 12px 0;'>선생님의 3학년 명렬을 분석하여 <b>[반 선택 -> 이름 선택 -> 답변 작성]</b> 분기가 적용된 구글 폼이 자동으로 완성되었습니다.</p>" +
    "<p style='color: #16a34a; font-weight: bold;'>동기화 완료: " + parsedSummary.join(", ") + "</p>" +
    "<div style='background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 8px; margin: 12px 0;'>" +
    "  <p style='margin-bottom: 8px;'><b>1. 설문지 편집 & 관리 주소 (선생님용):</b><br>" +
    "  <a href='" + form.getEditUrl() + "' target='_blank' style='color:#2563eb; font-weight:bold; word-break:break-all;'>" + form.getEditUrl() + "</a></p>" +
    "  <p style='margin: 0;'><b>2. 학생용 배포 주소 (학생들에게 보내는 링크):</b><br>" +
    "  <a href='" + form.getPublishedUrl() + "' target='_blank' style='color:#15803d; font-weight:bold; word-break:break-all;'>" + form.getPublishedUrl() + "</a></p>" +
    "</div>" +
    "<p style='color: #475569; font-size: 13px;'>* 학생들이 제출한 모든 수행평가 답변은 본 스프레드시트의 <b>새로운 탭(설문지 응답 1)</b>에 실시간으로 안전하게 자동 기록됩니다.</p>" +
    "</div>"
  ).setWidth(600).setHeight(380);
  SpreadsheetApp.getUi().showModalDialog(htmlOutput, "3학년 화법과작문 수행평가 폼 연동 완료");
}
