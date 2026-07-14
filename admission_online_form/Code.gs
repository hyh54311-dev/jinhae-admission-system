/**
 * 2027학년도 진해고등학교 신입생 입학등록확인서 자동 생성 시스템 (Backend)
 * 
 * 이 스크립트는 구글 문서(Docs) 템플릿에 학부모가 입력한 정보와 서명 이미지를 삽입하고,
 * 이를 PDF 파일로 변환하여 구글 드라이브 지정 폴더에 자동 저장하는 역할을 합니다.
 */

// [필수 설정] 아래 ID 값들을 본인의 구글 드라이브 ID에 맞게 수정해야 합니다.
var TEMPLATE_DOC_ID = "본인의_구글_문서_템플릿_ID_입력"; 
var SAVE_FOLDER_ID = "PDF를_저장할_구글_드라이브_폴더_ID_입력";

/**
 * 웹앱 접속 시 HTML 화면(Index.html)을 보여줍니다.
 */
function doGet(e) {
  return HtmlService.createTemplateFromFile("Index")
      .evaluate()
      .setTitle("2027학년도 진해고등학교 입학등록확인서 제출")
      .addMetaTag("viewport", "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no");
}

/**
 * 클라이언트(HTML 웹앱)에서 폼 데이터와 서명을 받아와 처리합니다.
 */
function submitForm(data) {
  try {
    // 1. 구글 문서 템플릿 파일 열기
    var templateFile = DriveApp.getFileById(TEMPLATE_DOC_ID);
    var targetFolder = DriveApp.getFolderById(SAVE_FOLDER_ID);
    
    // 2. 템플릿을 복사하여 임시 문서 생성
    var fileName = data.studentName + "_입학등록확인서_임시";
    var copiedFile = templateFile.makeCopy(fileName, targetFolder);
    var doc = DocumentApp.openById(copiedFile.getId());
    var body = doc.getBody();
    
    // 3. 오늘 날짜 구하기
    var today = new Date();
    var year = today.getFullYear().toString();
    var month = (today.getMonth() + 1).toString();
    var date = today.getDate().toString();
    
    // 4. 텍스트 치환 작업
    body.replaceText("\\{\\{학생이름\\}\\}", data.studentName);
    body.replaceText("\\{\\{생년월일\\}\\}", data.studentBirth);
    body.replaceText("\\{\\{학부모이름\\}\\}", data.parentName);
    body.replaceText("\\{\\{관계\\}\\}", data.parentRelation);
    body.replaceText("\\{\\{연락처\\}\\}", data.parentPhone);
    body.replaceText("\\{\\{년\\}\\}", year);
    body.replaceText("\\{\\{월\\}\\}", month);
    body.replaceText("\\{\\{일\\}\\}", date);
    
    // 5. 서명 이미지 삽입 작업
    if (data.signature) {
      // Base64 이미지 데이터 디코딩
      var base64Data = data.signature.split(',')[1];
      var blob = Utilities.newBlob(Utilities.base64Decode(base64Data), 'image/png', 'signature.png');
      
      // {{서명}} 표시가 있는 단락 찾기
      var rangeElement = body.findText("\\{\\{서명\\}\\}");
      if (rangeElement) {
        var element = rangeElement.getElement();
        var text = element.asText();
        var textStr = text.getText();
        var start = textStr.indexOf("{{서명}}");
        
        // {{서명}} 텍스트 삭제
        text.deleteText(start, start + 5); // "{{서명}}"은 6글자이므로 start ~ start+5 범위 삭제
        
        // 서명 이미지 삽입
        var parent = element.getParent();
        var index = parent.getChildIndex(element);
        var image = parent.asParagraph().insertInlineImage(index, blob);
        
        // 서명 크기 조정 (가로 80px, 세로 40px 정도로 조절 - 상황에 맞게 조절 가능)
        image.setWidth(80);
        image.setHeight(40);
      }
    }
    
    // 6. 변경사항 저장하고 닫기
    doc.saveAndClose();
    
    // 7. 임시 구글 문서를 PDF 파일로 변환하여 저장
    var pdfBlob = copiedFile.getAs(MimeType.PDF);
    var pdfFile = targetFolder.createFile(pdfBlob);
    pdfFile.setName(data.studentName + "_입학등록확인서.pdf");
    
    // 8. 임시로 만든 구글 문서 파일은 삭제(휴지통으로 이동)
    copiedFile.setTrashed(true);
    
    return {
      success: true,
      message: "제출이 완료되었습니다. 감사합니다."
    };
    
  } catch (e) {
    return {
      success: false,
      message: "오류가 발생했습니다: " + e.toString()
    };
  }
}
