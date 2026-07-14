/**
 * 2026학년도 입학생 3개년 교육과정 편성표(1학년) 의견 수렴 설문지 자동 생성 스크립트 (기존 설문지 덮어쓰기 버전)
 * 
 * [사용 방법]
 * 1. 이 설문 응답을 수집하고 있는 구글 스프레드시트(연동된 시트)를 엽니다.
 * 2. 상단 메뉴에서 [확장 프로그램] -> [Apps Script]를 클릭합니다.
 * 3. 기존 코드를 모두 지우고 이 스크립트 전체를 복사하여 붙여넣습니다.
 * 4. 상단의 [저장] 단추(디스켓 아이콘)를 클릭합니다.
 * 5. 실행 함수 목록에서 "createCurriculumForm"을 선택한 후 [실행] 단추(재생 아이콘)를 누릅니다.
 * 6. 스크립트가 실행되면 이미 연동된 기존 설문지를 찾아서 기존 문항을 모두 초기화(삭제)한 뒤, 신규 문항으로 덮어씁니다!
 */

function createCurriculumForm() {
  var ssActive = SpreadsheetApp.getActiveSpreadsheet();
  var form = null;
  var formUrl = ssActive.getFormUrl();
  var targetFolderId = "10J5UAVLICOx6i3V7_IRmibUO_DDBXRe7";
  
  // 1. 스프레드시트에 이미 연동된 설문지가 있는지 확인
  if (formUrl) {
    try {
      form = FormApp.openByUrl(formUrl);
      Logger.log("스프레드시트에 연동된 기존 설문지를 열었습니다.");
    } catch (err) {
      Logger.log("연동된 설문지 URL을 열 수 없습니다: " + err.toString());
    }
  }
  
  // 2. 연동된 설문지가 없거나 열지 못한 경우, 드라이브 폴더에서 기존 설문지 검색
  if (!form) {
    try {
      var folder = DriveApp.getFolderById(targetFolderId);
      var files = folder.getFiles();
      while (files.hasNext()) {
        var file = files.next();
        // MIME 타입이 구글 설문지이고 이름에 '교육과정'이 포함되어 있는지 확인
        if (file.getMimeType() === MimeType.GOOGLE_FORMS && file.getName().indexOf("교육과정") !== -1) {
          try {
            form = FormApp.openById(file.getId());
            Logger.log("드라이브 폴더에서 기존 교육과정 설문지(" + file.getName() + ")를 발견하여 엽니다.");
            // 스프레드시트와 연동 설정
            form.setDestination(FormApp.DestinationType.SPREADSHEET, ssActive.getId());
            Logger.log("발견된 설문지를 스프레드시트와 새로 연동하였습니다.");
            break;
          } catch (e) {
            Logger.log("드라이브에서 발견한 설문지를 여는 데 실패했습니다: " + e.toString());
          }
        }
      }
    } catch (err) {
      Logger.log("구글 드라이브 폴더 검색 중 오류 발생: " + err.toString());
    }
  }
  
  // 3. 기존 설문지가 완전히 없거나 로드에 실패한 경우 -> 신규 설문지 생성
  if (!form) {
    Logger.log("기존 설문지를 찾지 못해 새 설문지를 생성합니다.");
    form = FormApp.create("2026학년도 입학생 3개년 교육과정 편성표(1학년) 의견 수렴");
    form.setDestination(FormApp.DestinationType.SPREADSHEET, ssActive.getId());
    
    // 지정하신 구글 드라이브 폴더로 설문지 파일 이동
    try {
      var file = DriveApp.getFileById(form.getId());
      var folder = DriveApp.getFolderById(targetFolderId);
      file.moveTo(folder);
      Logger.log("새 설문지를 지정된 드라이브 폴더로 이동했습니다.");
    } catch (err) {
      Logger.log("설문지 파일 이동 실패: " + err.toString());
    }
  }
  
  // 4. 설문지 내용 업데이트를 위해 제목 설정 및 기존 모든 질문 항목 삭제 (초기화)
  form.setTitle("2026학년도 입학생 3개년 교육과정 편성표(1학년) 의견 수렴");
  var items = form.getItems();
  for (var i = 0; i < items.length; i++) {
    form.deleteItem(items[i]);
  }
  Logger.log("설문지의 기존 문항을 모두 초기화하였습니다. 새로 덮어씁니다.");
  
  // 3. 구글 드라이브에 업로드된 각 편성표 이미지 파일 ID
  var imgId1 = "1ddB1pB9sQz-Z0_6mYc-h4CRUgz963N4R";
  var imgId2 = "1b8rYUgkYUAkjEDuCQL3p6ttDILapwJX6";
  var imgId3 = "1Zd28HhkOLM4T5CMY7wLHR7BrKRG0J3Wv";
  var imgId4 = "1yeLWpQkfmO8c9mT8flt79BeuOgjtao4K";
  
  // 4. 설문지 설명글 설정
  var description = 
    "본 설문은 2026학년도 입학생 3개년 교육과정 편성표(1학년) 개정 및 편성에 대한 선생님들의 의견을 수렴하기 위한 것입니다.\n\n" +
    "제시된 1안부터 4안까지의 편성표 이미지를 차례대로 검토해 주시고, 각 안에 대한 선택 여부 및 의견을 기재해 주시기 바랍니다.\n\n" +
    "선생님들의 소중한 의견을 모아 교육과정부에 전달하도록 하겠습니다. 적극적인 참여 감사드립니다.";
    
  form.setDescription(description);
  
  // 5. 질문 1: 성명 선택 (객관식 라디오 버튼 / 필수)
  var nameItem = form.addMultipleChoiceItem();
  nameItem.setTitle("성명을 선택해 주세요.").setRequired(true);
  nameItem.setChoiceValues([
    "김태영", "임언숙", "조진희", "강지영", "황요한", "김승우", "강필성", "이병의"
  ]);
  
  // ==========================================
  // [1안 섹션]
  // ==========================================
  form.addPageBreakItem().setTitle("1안 검토 및 선택");
  
  // 1안 이미지 임베드
  try {
    var img1 = DriveApp.getFileById(imgId1);
    form.addImageItem()
        .setImage(img1)
        .setTitle("[1안] 편성표 이미지")
        .setHelpText("1안 요약 : 이전과 동일함. 다만, 선택군C의 '언어생활탐구', 선택군E의 '매체의사소통' 과목은 제외. (학생들의 과목 분산으로 인한 폐강을 막기 위함)");
  } catch (e) {
    form.addSectionHeaderItem().setTitle("[1안 이미지 로드 실패] 이미지 파일 ID를 확인해 주세요.");
  }
  
  // 1안 선택 여부 질문
  var choice1 = form.addMultipleChoiceItem();
  choice1.setTitle("1안을 선택하시겠습니까?").setRequired(true);
  choice1.setChoiceValues(["선택함", "선택하지 않음"]);
  
  // 1안 건의사항 질문
  var opinion1 = form.addParagraphTextItem();
  opinion1.setTitle("1안에 대한 의견 및 건의사항을 적어주세요.");
  
  // ==========================================
  // [2안 섹션]
  // ==========================================
  form.addPageBreakItem().setTitle("2안 검토 및 선택");
  
  // 2안 이미지 임베드
  try {
    var img2 = DriveApp.getFileById(imgId2);
    form.addImageItem()
        .setImage(img2)
        .setTitle("[2안] 편성표 이미지")
        .setHelpText("2안 요약 : 이전의 선택군 C, D를 묶은 뒤 3학점씩 4과목을 선택하도록 하는 안.");
  } catch (e) {
    form.addSectionHeaderItem().setTitle("[2안 이미지 로드 실패] 이미지 파일 ID를 확인해 주세요.");
  }
  
  // 2안 선택 여부 질문
  var choice2 = form.addMultipleChoiceItem();
  choice2.setTitle("2안을 선택하시겠습니까?").setRequired(true);
  choice2.setChoiceValues(["선택함", "선택하지 않음"]);
  
  // 2안 건의사항 질문
  var opinion2 = form.addParagraphTextItem();
  opinion2.setTitle("2안에 대한 의견 및 건의사항을 적어주세요.");
  
  // ==========================================
  // [3안 섹션]
  // ==========================================
  form.addPageBreakItem().setTitle("3안 검토 및 선택");
  
  // 3안 이미지 임베드
  try {
    var img3 = DriveApp.getFileById(imgId3);
    form.addImageItem()
        .setImage(img3)
        .setTitle("[3안] 편성표 이미지")
        .setHelpText("3안 요약 : 이전의 선택군 C, D 뿐만 아니라 이전의 선택군 E, F도 묶어서 각각 3학점씩 4과목을 선택하도록 하는 안.");
  } catch (e) {
    form.addSectionHeaderItem().setTitle("[3안 이미지 로드 실패] 이미지 파일 ID를 확인해 주세요.");
  }
  
  // 3안 선택 여부 질문
  var choice3 = form.addMultipleChoiceItem();
  choice3.setTitle("3안을 선택하시겠습니까?").setRequired(true);
  choice3.setChoiceValues(["선택함", "선택하지 않음"]);
  
  // 3안 건의사항 질문
  var opinion3 = form.addParagraphTextItem();
  opinion3.setTitle("3안에 대한 의견 및 건의사항을 적어주세요.");
  
  // ==========================================
  // [4안 섹션]
  // ==========================================
  form.addPageBreakItem().setTitle("4안 검토 및 선택");
  
  // 4안 이미지 임베드
  try {
    var img4 = DriveApp.getFileById(imgId4);
    form.addImageItem()
        .setImage(img4)
        .setTitle("[4안] 편성표 이미지")
        .setHelpText("4안 요약 : 3학년 1학기 학교지정과목 중 국어, 영어, 수학의 학점을 1학점씩 줄여 3학점을 확보한 뒤, 이전의 선택군 E, F에서 3학점씩 5과목을 선택하도록 하는 안.");
  } catch (e) {
    form.addSectionHeaderItem().setTitle("[4안 이미지 로드 실패] 이미지 파일 ID를 확인해 주세요.");
  }
  
  // 4안 선택 여부 질문
  var choice4 = form.addMultipleChoiceItem();
  choice4.setTitle("4안을 선택하시겠습니까?").setRequired(true);
  choice4.setChoiceValues(["선택함", "선택하지 않음"]);
  
  // 4안 건의사항 질문
  var opinion4 = form.addParagraphTextItem();
  opinion4.setTitle("4안에 대한 의견 및 건의사항을 적어주세요.");
  
  Logger.log("설문지 편집 링크: " + form.getEditUrl());
  Logger.log("설문지 배포 링크 (교사 공유용): " + form.getPublishedUrl());
  
  // 구글 시트 내에 모달창으로 완료 안내 및 링크 표시
  var htmlOutput = HtmlService.createHtmlOutput(
    "<div style='font-family: sans-serif; padding: 15px; line-height: 1.6; font-size: 14px;'>" +
    "<h3 style='color: #1e3a8a; border-bottom: 2px solid #3b82f6; padding-bottom: 8px;'>[완료] 교육과정 의견 수렴 설문지 업데이트 완료!</h3>" +
    "<p style='margin: 12px 0;'>기존에 연동되어 있던 구글 설문지에 신규 교육과정 설문 내용을 <b>성공적으로 덮어썼습니다(업데이트 완료)</b>.</p>" +
    "<div style='background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 8px; margin: 12px 0;'>" +
    "  <p style='margin-bottom: 8px;'><b>1. 설문지 편집 & 관리 주소 (선생님용):</b><br>" +
    "  <a href='" + form.getEditUrl() + "' target='_blank' style='color:#2563eb; font-weight:bold; word-break:break-all;'>" + form.getEditUrl() + "</a></p>" +
    "  <p style='margin: 0;'><b>2. 교사용 배포 주소 (선생님들께 보내는 링크):</b><br>" +
    "  <a href='" + form.getPublishedUrl() + "' target='_blank' style='color:#15803d; font-weight:bold; word-break:break-all;'>" + form.getPublishedUrl() + "</a></p>" +
    "</div>" +
    "<p style='color: #475569; font-size: 13px;'>* 선생님들이 제출하시는 모든 새 답변은 본 스프레드시트의 <b>새로운 탭(설문지 응답 1)</b>에 계속 누적 기록됩니다.</p>" +
    "</div>"
  ).setWidth(600).setHeight(380);
  SpreadsheetApp.getUi().showModalDialog(htmlOutput, "교육과정 의견 수렴 설문지 연동 완료");
}
