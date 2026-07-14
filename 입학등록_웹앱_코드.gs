/**
 * 2027학년도 진해고등학교 신입생 입학등록 확인서 온라인 제출 시스템 - 백엔드
 * 
 * 제작: Antigravity (Google DeepMind Team Pair Programming)
 * 목적: 학생 및 보호자가 온라인 서명 패드를 통해 입학등록 확인서를 안전하고 원격으로 제출하고,
 *       실시간 합격자 DB 매칭 검증 및 행정 서류용 완성형 PDF를 자동 발급 및 저장합니다.
 */

// 1. 웹앱 진입점 (HTTP GET)
function doGet() {
  return HtmlService.createTemplateFromFile('입학등록_웹앱_화면')
      .evaluate()
      .setTitle('2027학년도 진해고등학교 입학등록 확인서 제출')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// 2. 구글 드라이브 폴더 가져오기 또는 생성 (기본 설정 자동화)
function getOrCreateFolder(folderName) {
  var folders = DriveApp.getFoldersByName(folderName);
  if (folders.hasNext()) {
    return folders.next();
  } else {
    return DriveApp.createFolder(folderName);
  }
}

// 3. 합격자 마스터 시트 가져오기 또는 생성 (테스트 환경 자동 빌드)
function getOrCreateMasterSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("합격자_마스터");
  if (!sheet) {
    sheet = ss.insertSheet("합격자_마스터");
    var headers = ["접수번호", "학생 성명", "출신중학교", "생년월일", "등록상태"];
    sheet.appendRow(headers);
    // 가상의 테스트 데이터 자동 생성
    sheet.appendRow(["2027-0001", "홍길동", "진해남중학교", "090101", "미등록"]);
    sheet.appendRow(["2027-0002", "성춘향", "석동중학교", "090202", "미등록"]);
    sheet.appendRow(["2027-0003", "이몽룡", "진해중학교", "090303", "미등록"]);
    
    sheet.getRange(1, 1, 1, headers.length)
         .setFontWeight("bold")
         .setBackground("#f1f5f9")
         .setHorizontalAlignment("center");
    sheet.setFrozenRows(1);
    sheet.autoResizeColumns(1, headers.length);
  }
  return sheet;
}

// 4. 입학등록 응답 시트 가져오기 또는 생성
function getOrCreateResponseSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("등록_확인서_응답");
  if (!sheet) {
    sheet = ss.insertSheet("등록_확인서_응답");
    var headers = [
      "제출일시", 
      "접수번호",
      "학생 성명", 
      "출신중학교",
      "생년월일",
      "보호자 성명", 
      "보호자 연락처", 
      "학생 서명 URL",
      "보호자 서명 URL", 
      "등록확인서 PDF URL"
    ];
    sheet.appendRow(headers);
    
    sheet.getRange(1, 1, 1, headers.length)
         .setFontWeight("bold")
         .setBackground("#e0f2fe")
         .setHorizontalAlignment("center");
    sheet.setFrozenRows(1);
    sheet.autoResizeColumns(1, headers.length);
  }
  return sheet;
}

// 5. PDF 생성용 구글 문서 템플릿 가져오기 또는 기본 템플릿 생성
function getOrCreateTemplateDoc() {
  var files = DriveApp.getFilesByName("2027학년도_입학등록확인서_템플릿");
  if (files.hasNext()) {
    return DocumentApp.openById(files.next().getId());
  }
  
  // 템플릿 문서가 드라이브에 없을 경우 자동으로 세련된 양식 생성
  var doc = DocumentApp.create("2027학년도_입학등록확인서_템플릿");
  var body = doc.getBody();
  
  // 마진 설정 (인쇄용 표준 여백)
  body.setMarginTop(50);
  body.setMarginBottom(50);
  body.setMarginLeft(50);
  body.setMarginRight(50);
  
  // 전체 외곽 테두리를 위한 1x1 테이블 생성
  var outerTable = body.appendTable([[""]]);
  outerTable.setBorderWidth(1.5);
  outerTable.setBorderColor("#1c4587"); // Dark Blue border
  
  var cell = outerTable.getCell(0, 0);
  cell.setPaddingTop(40);
  cell.setPaddingBottom(40);
  cell.setPaddingLeft(45);
  cell.setPaddingRight(45);
  
  // 제목 스타일링
  var title = cell.appendParagraph("2027학년도 진해고등학교 입학등록확인서");
  title.setFontSize(22);
  title.setBold(true);
  title.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
  title.setFontColor("#1c4587");
  
  // 제목 밑의 가로선 역할 (thin borderless table)
  var hrTable = cell.appendTable([[""]]);
  hrTable.setBorderWidth(0);
  hrTable.setColumnWidth(0, 420);
  hrTable.getRow(0).getCell(0).setBackgroundColor("#1c4587").setMinimumHeight(2);
  
  cell.appendParagraph("\n\n\n");
  
  // 학생 정보 입력 영역 (우측 정렬용 2열 테이블)
  var infoCells = [
    ["", "접 수 번 호 : {{접수번호}}"],
    ["", "성       명 : {{학생성명}}"],
    ["", "출 신 중 학 교 : {{출신중학교}}"],
    ["", "생  년  월  일 : {{생년월일}}"]
  ];
  var infoTable = cell.appendTable(infoCells);
  infoTable.setBorderWidth(0);
  infoTable.setColumnWidth(0, 180); // 왼쪽 공백
  infoTable.setColumnWidth(1, 260); // 오른쪽 정보
  
  for (var i = 0; i < infoTable.getNumRows(); i++) {
    var rCell = infoTable.getRow(i).getCell(1);
    var p = rCell.getChild(0).asParagraph();
    p.setFontSize(14);
    p.setLineSpacing(1.5);
  }
  
  cell.appendParagraph("\n\n\n\n");
  
  // 안내 서약 문구
  var noticeText = cell.appendParagraph(
    "본인은 2027학년도 비평준화지역 일반고 입학전형에서 진해고등학교에 입학을 희망합니다."
  );
  noticeText.setFontSize(13);
  noticeText.setBold(true);
  noticeText.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
  
  cell.appendParagraph("\n\n\n\n");
  
  // 날짜
  var datePara = cell.appendParagraph("2027년   1월   4일");
  datePara.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
  datePara.setFontSize(13);
  
  cell.appendParagraph("\n\n\n\n");
  
  // 서명 영역 (우측 정렬용 2열 테이블)
  var sigCells = [
    ["", "학   생 : {{학생성명}}   {{학생서명}}   (서명 또는 인)"],
    ["", "보 호 자 : {{보호자성명}}   {{보호자서명}}   (서명 또는 인)"]
  ];
  var sigTable = cell.appendTable(sigCells);
  sigTable.setBorderWidth(0);
  sigTable.setColumnWidth(0, 180);
  sigTable.setColumnWidth(1, 260);
  
  for (var i = 0; i < sigTable.getNumRows(); i++) {
    var rCell = sigTable.getRow(i).getCell(1);
    var p = rCell.getChild(0).asParagraph();
    p.setFontSize(13);
    p.setLineSpacing(2.0);
  }
  
  cell.appendParagraph("\n\n\n\n\n");
  
  // 수신처
  var schoolPara = cell.appendParagraph("진해고등학교장 귀하");
  schoolPara.setFontSize(20);
  schoolPara.setBold(true);
  schoolPara.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
  
  doc.saveAndClose();
  return doc;
}

// 6. 학부모 정보 입력 및 서명을 기반으로 정식 PDF 서류 생성
function generateConfirmationPdf(studentName, studentId, schoolName, birthDate, parentName, parentPhone, studentSigBlob, parentSigBlob) {
  var templateDoc = getOrCreateTemplateDoc();
  var pdfFolder = getOrCreateFolder("2027학년도_입학등록확인서_PDF");
  
  // 템플릿 복제본 생성
  var tempDocFile = DriveApp.getFileById(templateDoc.getId()).makeCopy(
    studentId + "_" + studentName + "_입학등록확인서_임시", 
    pdfFolder
  );
  var doc = DocumentApp.openById(tempDocFile.getId());
  var body = doc.getBody();
  
  // 텍스트 치환
  body.replaceText("{{학생성명}}", studentName);
  body.replaceText("{{접수번호}}", studentId);
  body.replaceText("{{출신중학교}}", schoolName);
  body.replaceText("{{생년월일}}", birthDate);
  body.replaceText("{{보호자성명}}", parentName);
  
  // 학생 서명 이미지 삽입
  insertSignatureImage(body, "{{학생서명}}", studentSigBlob);
  // 보호자 서명 이미지 삽입
  insertSignatureImage(body, "{{보호자서명}}", parentSigBlob);
  
  doc.saveAndClose();
  
  // PDF 생성 및 공유 권한 부여
  var pdfBlob = tempDocFile.getAs(MimeType.PDF);
  var pdfFile = pdfFolder.createFile(pdfBlob);
  pdfFile.setName(studentId + "_" + studentName + "_입학등록확인서.pdf");
  pdfFile.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  
  // 템플릿 임시 복제 문서 삭제 (드라이브 청소)
  DriveApp.getFileById(tempDocFile.getId()).setTrashed(true);
  
  return pdfFile.getUrl();
}

function insertSignatureImage(body, placeholder, blob) {
  var searchResult = body.findText(placeholder);
  if (searchResult) {
    var element = searchResult.getElement();
    var text = element.asText();
    var parent = element.getParent();
    
    // 서명 블롭 이미지 추가 및 픽셀 스케일링
    var image = parent.asParagraph().appendInlineImage(blob);
    image.setWidth(80);
    image.setHeight(40);
    
    // 플레이스홀더 텍스트 삭제
    text.setText(text.getText().replace(placeholder, ""));
  }
}

// 7. 실시간 합격자 신원 검증 (프론트엔드 연동 API)
function checkCandidate(studentName, examineeNumber) {
  try {
    var masterSheet = getOrCreateMasterSheet();
    var data = masterSheet.getDataRange().getValues();
    
    var isMatched = false;
    var matchedRowIndex = -1;
    var registrationStatus = "";
    var schoolName = "";
    var birthDate = "";
    
    // 2번째 줄(인덱스 1)부터 탐색
    for (var i = 1; i < data.length; i++) {
      var row = data[i];
      var rowId = String(row[0]).trim();
      var rowName = String(row[1]).trim();
      
      if (rowId === String(examineeNumber).trim() && rowName === String(studentName).trim()) {
        isMatched = true;
        matchedRowIndex = i + 1; // 1-based row index
        schoolName = String(row[2]).trim();
        birthDate = String(row[3]).trim();
        registrationStatus = String(row[4]).trim();
        break;
      }
    }
    
    if (!isMatched) {
      return { 
        valid: false, 
        error: "입력하신 접수번호와 학생 성명이 합격자 명단과 일치하지 않습니다. 다시 확인해주세요." 
      };
    }
    
    // 이미 등록 완료했는지 체크
    var responseSheet = getOrCreateResponseSheet();
    var responseData = responseSheet.getDataRange().getValues();
    var alreadySubmitted = false;
    
    for (var j = 1; j < responseData.length; j++) {
      var repRow = responseData[j];
      var repId = String(repRow[1]).trim(); // 접수번호 열 (Index 1)
      
      if (repId === String(examineeNumber).trim()) {
        alreadySubmitted = true;
        break;
      }
    }
    
    if (alreadySubmitted || registrationStatus === "등록완료") {
      return { 
        valid: true, 
        alreadySubmitted: true, 
        message: "이미 해당 학생의 입학등록 확인서가 접수되었습니다." 
      };
    }
    
    return { 
      valid: true, 
      alreadySubmitted: false,
      schoolName: schoolName,
      birthDate: birthDate
    };
    
  } catch (error) {
    return { valid: false, error: "서버 검증 중 에러가 발생했습니다: " + error.toString() };
  }
}

// 8. 서명 및 인적사항 폼 제출 데이터 일괄 처리
function submitAdmissionConfirmation(formData) {
  try {
    // 백엔드 재검증 (보안 무결성 보장)
    var checkResult = checkCandidate(formData.studentName, formData.studentId);
    if (!checkResult.valid) {
      return { success: false, error: checkResult.error };
    }
    if (checkResult.alreadySubmitted) {
      return { success: false, error: "이미 제출 완료된 접수번호입니다." };
    }
    
    // 서명 이미지 및 PDF 저장 드라이브 설정
    var imgFolder = getOrCreateFolder("2027학년도_입학등록확인서_서명");
    
    var contentType = "image/png";
    
    // 1) 학생 서명 디코딩 및 저장
    var studentBase64 = formData.studentSignature;
    var studentDecoded = Utilities.base64Decode(studentBase64.split(",")[1]);
    var studentFileName = formData.studentId + "_" + formData.studentName + "_학생서명.png";
    var studentBlob = Utilities.newBlob(studentDecoded, contentType, studentFileName);
    var studentSigFile = imgFolder.createFile(studentBlob);
    studentSigFile.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    var studentSigUrl = studentSigFile.getUrl();
    
    // 2) 보호자 서명 디코딩 및 저장
    var parentBase64 = formData.parentSignature;
    var parentDecoded = Utilities.base64Decode(parentBase64.split(",")[1]);
    var parentFileName = formData.studentId + "_" + formData.studentName + "_보호자서명.png";
    var parentBlob = Utilities.newBlob(parentDecoded, contentType, parentFileName);
    var parentSigFile = imgFolder.createFile(parentBlob);
    parentSigFile.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    var parentSigUrl = parentSigFile.getUrl();
    
    // 3) 템플릿 기반 입학등록 확인서 PDF 파일 생성
    var pdfUrl = "";
    try {
      pdfUrl = generateConfirmationPdf(
        formData.studentName, 
        formData.studentId, 
        checkResult.schoolName,
        checkResult.birthDate,
        formData.parentName, 
        formData.parentPhone, 
        studentBlob,
        parentBlob
      );
    } catch (pdfErr) {
      console.error("PDF 생성 오류: " + pdfErr.toString());
    }
    
    // 시트에 데이터 누적 기록
    var responseSheet = getOrCreateResponseSheet();
    responseSheet.appendRow([
      new Date(),              // 제출일시
      formData.studentId,      // 접수번호
      formData.studentName,    // 학생 성명
      checkResult.schoolName,  // 출신중학교
      checkResult.birthDate,   // 생년월일
      formData.parentName,     // 학부모 성명
      formData.parentPhone,    // 학부모 연락처
      studentSigUrl,           // 학생 서명 링크
      parentSigUrl,            // 보호자 서명 링크
      pdfUrl                   // 등록확인서 PDF 링크
    ]);
    
    // 마스터 시트 상태 변경 (등록상태 -> 등록완료)
    var masterSheet = getOrCreateMasterSheet();
    var masterData = masterSheet.getDataRange().getValues();
    for (var k = 1; k < masterData.length; k++) {
      if (String(masterData[k][0]).trim() === String(formData.studentId).trim()) {
        masterSheet.getRange(k + 1, 5).setValue("등록완료"); // 등록상태는 5열 (Index 4)
        break;
      }
    }
    
    return { success: true, studentName: formData.studentName };
    
  } catch (error) {
    return { success: false, error: error.toString() };
  }
}
