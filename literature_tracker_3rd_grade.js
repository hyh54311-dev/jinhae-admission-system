/**
 * ?럳 2026?숇뀈??3?숇뀈 臾명븰 吏꾨룄??'?댁쨷 ?덉씠?? ?먮룞 ?숆린???쒖뒪?? * ?쒖옉: AI 援먯쑁 鍮꾩꽌 (Antigravity)
 * 
 * [?쒖뒪???뱀쭠]
 * 1. ?ㅼ떆媛??숆린??(onEdit): ? ?섏젙 利됱떆 ?꾩넚 ?쒕룄
 * 2. 諛곌꼍 ?먮룞??(Trigger): 10遺꾨쭏???꾨씫???곗씠?곕? 李얠븘 ?먮룞?쇰줈 蹂댁젙?꾩넚 (?쒕툝由??섍꼍 理쒖쟻??
 * 3. 以묐났 諛⑹?: ?꾩넚 ?꾨즺????ぉ(??? ?ㅼ떆 蹂대궡吏 ?딆쓬
 */

// --- [?꾩뿭 ?ㅼ젙] ---
const MAIN_SHEET_NAME = "3?숇뀈 ?꾩껜 諛?;
const CLASS_LIST = ["1諛?, "2諛?, "3諛?, "4諛?, "5諛?, "6諛?, "7諛?, "8諛?, "9諛?, "10諛?];

/**
 * [onOpen] ?곷떒 硫붾돱瑜??앹꽦?⑸땲??
 */
function onOpen() {
  SpreadsheetApp.getUi().createMenu('?뱷 吏꾨룄???꾧뎄')
    .addItem('?? 1~10諛??쒗듃 ?앹꽦 諛?珥덇린??, 'setupSystem')
    .addItem('?봽 吏湲?利됱떆 ?숆린??(?섎룞)', 'manualSync')
    .addSeparator()
    .addItem('??[?쒕툝由우슜] 10遺꾨쭏???먮룞 ?숆린??耳쒓린', 'setupTimeTrigger')
    .addSeparator()
    .addItem('?좑툘 ?꾩껜 ?ㅼ떆 ?숆린??(媛뺤젣)', 'forceSyncAll')
    .addItem('?뮕 ?꾩?留?, 'showHelp')
    .addToUi();
}

/**
 * [setupSystem] 1~10諛??쒗듃 ?앹꽦 諛??곗씠???좏슚??寃???쒕∼?ㅼ슫) ?ㅼ젙
 */
function setupSystem() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let createdCount = 0;

  // 1. 1~10諛?媛쒕퀎 ?쒗듃 ?뺤씤 諛??앹꽦
  CLASS_LIST.forEach(name => {
    if (!ss.getSheetByName(name)) {
      const newSheet = ss.insertSheet(name);
      newSheet.appendRow(["?좎쭨", "吏꾨룄 ?꾪솴", "鍮꾧퀬/?붿빟"]);
      newSheet.getRange("A1:C1").setBackground("#444444").setFontColor("white").setFontWeight("bold").setHorizontalAlignment("center");
      newSheet.setColumnWidth(1, 120);
      newSheet.setColumnWidth(2, 350);
      newSheet.setColumnWidth(3, 300);
      createdCount++;
    }
  });
  
  // 2. 硫붿씤 ?쒗듃 ?ㅼ젙
  const mainSheet = ss.getSheetByName(MAIN_SHEET_NAME);
  if (mainSheet) {
    // E???꾩넚 ?곹깭) ?ㅻ뜑 ?ㅼ젙
    mainSheet.getRange("E1").setValue("?꾩넚 ?곹깭").setBackground("#f3f3f3").setFontWeight("bold").setHorizontalAlignment("center");
    mainSheet.setColumnWidth(5, 80);
    
    // A???숆툒 ?쒕∼?ㅼ슫 ?ㅼ젙 (?꾩껜 踰붿쐞)
    const classRule = SpreadsheetApp.newDataValidation().requireValueInList(CLASS_LIST).build();
    mainSheet.getRange("A2:A100").setDataValidation(classRule);
    
    // ?쒖떇 ?뺣━
    const lastRow = mainSheet.getMaxRows();
    mainSheet.getRange(2, 5, lastRow - 1, 1).setHorizontalAlignment("center");
  }

  const ui = SpreadsheetApp.getUi();
  ui.alert("???명똿 ?꾨즺! " + createdCount + "媛쒖쓽 ?쒗듃媛 ?앹꽦?섏뿀?쇰ŉ, 硫붿씤 ?쒗듃???쒕∼?ㅼ슫 紐⑸줉???ㅼ젙?섏뿀?듬땲??");
}

/**
 * [onEdit] ?ㅼ떆媛??몄쭛 ?몃━嫄?(媛뺥솕 踰꾩쟾)
 */
function onEdit(e) {
  if (!e || !e.range) return;
  
  const ss = e.source;
  const sheet = e.range.getSheet();
  const activeSheetName = sheet.getName().trim();
  
  if (activeSheetName !== MAIN_SHEET_NAME) return;

  const row = e.range.rowStart;
  const col = e.range.columnStart;
  if (row <= 1) return;

  // ?숆툒(A) ?뱀? 吏꾨룄(C) ?섏젙 ???좎쭨 ?먮룞 ?꾩꽦
  if (col === 1 || col === 3) {
    const classValue = sheet.getRange(row, 1).getValue();
    const dateCell = sheet.getRange(row, 2);
    const progressValue = sheet.getRange(row, 3).getValue();
    
    if ((classValue !== "" || progressValue !== "") && dateCell.getValue() === "") {
      dateCell.setValue(new Date()).setNumberFormat("MM/dd (ddd)");
    }
  }

  // 利됱떆 ?숆린???쒕룄
  syncAllUnsentRecords(ss);
}

/**
 * [manualSync] 硫붾돱瑜??듯븳 ?섎룞 ?숆린???ㅽ뻾
 */
function manualSync() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  syncAllUnsentRecords(ss);
  ss.toast("?숆린?붽? ?꾨즺?섏뿀?듬땲??", "?꾩쟾 ?먮룞 ?쒖뒪??);
}

/**
 * [setupTimeTrigger] ?쒓컙 湲곕컲 ?몃━嫄??ㅼ튂 (10遺?媛꾧꺽)
 */
function setupTimeTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  // 湲곗〈 ?몃━嫄???젣 (以묐났 諛⑹?)
  triggers.forEach(t => {
    if (t.getHandlerFunction() === 'syncAllUnsentRecordsForTrigger') {
      ScriptApp.deleteTrigger(t);
    }
  });
  
  // 10遺꾨쭏???ㅽ뻾?섎뒗 ?덈줈???몃━嫄??앹꽦
  ScriptApp.newTrigger('syncAllUnsentRecordsForTrigger')
    .timeBased()
    .everyMinutes(10)
    .create();
    
  SpreadsheetApp.getUi().alert("?? [?꾩쟾 ?먮룞???쒖꽦??\n?댁젣 10遺꾨쭏???쒖뒪?쒖씠 ?먮룞?쇰줈 誘몄쟾???곗씠?곕? 泥댄겕?⑸땲??\n?쒕툝由우뿉???낅젰留??섍퀬 ?깆쓣 ?レ쑝?붾룄 ?뚯븘??泥섎━?⑸땲??");
}

/**
 * [syncAllUnsentRecordsForTrigger] ?몃━嫄??꾩슜 ?ㅽ뻾 ?⑥닔
 */
function syncAllUnsentRecordsForTrigger() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  syncAllUnsentRecords(ss);
}

/**
 * [syncAllUnsentRecords] ?듭떖 ?숆린???붿쭊
 */
function syncAllUnsentRecords(ss) {
  const mainSheet = ss.getSheetByName(MAIN_SHEET_NAME);
  if (!mainSheet) return;

  const dataRange = mainSheet.getDataRange();
  const data = dataRange.getValues();
  let syncCount = 0;

  for (let i = 1; i < data.length; i++) {
    const className = data[i][0].toString().trim(); // A??    const dateVal = data[i][1];                     // B??    const progressVal = data[i][2];                 // C??    const summaryVal = data[i][3];                  // D??    const statusVal = data[i][4];                   // E??
    // ?숆툒怨?吏꾨룄媛 ?덇퀬 ?꾩쭅 ?꾩넚 ?꾨즺(???섏? ?딆? 寃쎌슦
    if (className && progressVal && statusVal !== "??) {
      let targetName = className;
      if (!targetName.includes("諛?) && !isNaN(targetName)) targetName += "諛?;
      
      const targetSheet = ss.getSheetByName(targetName);
      if (targetSheet) {
        // ?곗씠???쎌엯 (理쒖떊??
        targetSheet.insertRowAfter(1);
        targetSheet.getRange(2, 1, 1, 3).setValues([[dateVal, progressVal, summaryVal]]);
        
        // ?쒖떇 諛?留덈Т由?        targetSheet.getRange("A2").setNumberFormat("MM/dd (ddd)");
        targetSheet.getRange(2, 2).setWrap(true);
        targetSheet.getRange(2, 3).setWrap(true);
        
        mainSheet.getRange(i + 1, 5).setValue("??).setHorizontalAlignment("center");
        syncCount++;
      }
    }
  }

  if (syncCount > 0) {
    ss.toast("?? " + syncCount + "媛쒖쓽 湲곕줉??媛?諛???쑝濡??먮룞 ?곕룞?덉뒿?덈떎.", "?먮룞 湲곕줉 ?쒖뒪??);
  }
}

/**
 * [forceSyncAll] 紐⑤뱺 湲곕줉 臾댁“嫄??ъ쟾?? */
function forceSyncAll() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  const response = ui.alert('媛뺤젣 ?щ룞湲고솕', 
                            '?대? ???쒖떆??湲곕줉???ы븿?섏뿬 紐⑤뱺 ?곗씠?곕? ?ㅼ떆 ?꾩넚?섏떆寃좎뒿?덇퉴?\n?댁슜??以묐났?????덉뒿?덈떎.', 
                            ui.ButtonSet.YES_NO);
  
  if (response !== ui.Button.YES) return;

  const mainSheet = ss.getSheetByName(MAIN_SHEET_NAME);
  const lastRow = mainSheet.getLastRow();
  if (lastRow > 1) {
    mainSheet.getRange(2, 5, lastRow - 1, 1).clearContent();
  }
  
  syncAllUnsentRecords(ss);
}

/**
 * [showHelp] ?ъ슜 媛?대뱶
 */
function showHelp() {
  const msg = "?뱷 3?숇뀈 臾명븰 吏꾨룄???꾩쟾 ?먮룞??媛?대뱶\n\n" +
              "1. [?숆툒]???쒕∼?ㅼ슫?먯꽌 ?좏깮?섏꽭??\n" +
              "2. [吏꾨룄 ?꾪솴]???낅젰?섍퀬 ?뷀꽣瑜?移섎㈃ '理쒓렐 ?섏뾽 ?좎쭨'? '?? ?쒖떆媛 李⑤?濡??앷퉩?덈떎.\n" +
              "3. ?쒕툝由??ъ슜?먮뒗 ???섎떒??泥댄겕(V) 踰꾪듉???꾨Ⅴ硫????뺤떎?섍쾶 ?묐룞?⑸땲??\n" +
              "4. ?숆린?붽? 媛???먮━?ㅻ㈃ [??10遺꾨쭏???먮룞 ?숆린??耳쒓린] 硫붾돱瑜??쒖꽦?뷀빐 蹂댁꽭??";
  SpreadsheetApp.getUi().alert(msg);
}
