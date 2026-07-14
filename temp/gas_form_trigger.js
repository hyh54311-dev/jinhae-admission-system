/**
 * ?숈깮 寃곗꽍 ?뺤씤???곕룞 ?ㅽ겕由쏀듃 (Google Apps Script)
 * 
 * [?ㅼ튂 諛⑸쾿]
 * 1. ?숈깮?ㅼ뿉寃?諛쏆쓣 援ш? ??援ш? ?ㅻЦ吏)??留뚮벊?덈떎.
 * 2. ?쇱뿉??[?묐떟] -> [?ㅽ봽?덈뱶?쒗듃???곌껐]???뚮윭 ?쒗듃瑜?留뚮벊?덈떎.
 * 3. ?쒗듃??[?뺤옣 ?꾨줈洹몃옩] -> [Apps Script]????肄붾뱶瑜?遺숈뿬?ｌ뒿?덈떎.
 * 4. ?몃━嫄??쒓퀎 ?꾩씠肄? ?ㅼ젙?먯꽌 "?묒떇 ?쒖텧 ?? ???⑥닔媛 ?ㅽ뻾?섎룄濡??깅줉?⑸땲??
 */

// ?좎깮?섏쓽 ?덈룄??PC(援ш? ?쒕씪?대툕 ?곗뒪?ы넲)? ?숆린?붾맆 ?대뜑 ID瑜??낅젰?섏꽭??
// (?? G?쒕씪?대툕 ??'寃곗꽍?뺤씤???湲곗뿴' ?대뜑??ID)
const QUEUE_FOLDER_ID = "?ш린???대뜑_?꾩씠?붾?_?ｌ쑝?몄슂"; 

function onFormSubmit(e) {
  try {
    const responses = e.namedValues;
    const timestamp = e.values[0]; 
    
    // ????ぉ ?대쫫??留욎떠 ?곗씠?곕? 異붿텧?⑸땲?? 
    // (?ㅻЦ吏??吏덈Ц ?대쫫怨??꾨옒 ?ㅼ썙?쒓? ?뺥솗???쇱튂?댁빞 ?⑸땲??)
    const studentName = responses["?대쫫"] ? responses["?대쫫"][0] : "?대쫫?놁쓬";
    const stdClass = responses["?숇뀈諛?] ? responses["?숇뀈諛?][0] : "?숇컲誘몄긽";
    const stdNumber = responses["踰덊샇"] ? responses["踰덊샇"][0] : "0踰?;
    const absenceDate = responses["寃곗꽍 ?쇱옄"] ? responses["寃곗꽍 ?쇱옄"][0] : "?쇱옄誘몄긽";
    const absenceType = responses["寃곗꽍 醫낅쪟"] ? responses["寃곗꽍 醫낅쪟"][0] : "湲고?寃곗꽍";
    const absenceReason = responses["寃곗꽍 ?ъ쑀"] ? responses["寃곗꽍 ?ъ쑀"][0] : "?ъ쑀 ?놁쓬";
    
    const dataObj = {
      "timestamp": timestamp,
      "name": studentName,
      "class": stdClass,
      "number": stdNumber,
      "date": absenceDate,
      "type": absenceType,
      "reason": absenceReason
    };
    
    const jsonString = JSON.stringify(dataObj, null, 2);
    
    // ?뚯씪紐??덉떆: 寃곗꽍?좎껌_?띻만??202604121530.json
    const safeTime = timestamp.replace(/[-:\s/]/g, "").substring(0, 14);
    const fileName = `寃곗꽍?좎껌_${studentName}_${safeTime}.json`;
    
    const folder = DriveApp.getFolderById(QUEUE_FOLDER_ID);
    folder.createFile(fileName, jsonString, MimeType.PLAIN_TEXT);
    
    console.log("??寃곗꽍 ?좎껌??JSON ?ㅽ봽 ?꾨즺: " + fileName);
    
  } catch (error) {
    console.error("?ㅻ쪟 諛쒖깮: " + error.toString());
  }
}
