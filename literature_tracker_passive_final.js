/**
 * ?럳 2026?숇뀈??2?숇뀈 臾명븰 吏꾨룄??'?댁쨷 ?덉씠?? ?먮룞 ?숆린???쒖뒪?? * ?쒖옉: AI 援먯쑁 鍮꾩꽌 (Antigravity)
 * 
 * [?쒖뒪???뱀쭠]
 * 1. ?ㅼ떆媛??숆린??(onEdit): ? ?섏젙 利됱떆 ?꾩넚 ?쒕룄
 * 2. 諛곌꼍 ?먮룞??(Trigger): 10遺꾨쭏???꾨씫???곗씠?곕? 李얠븘 ?먮룞?쇰줈 蹂댁젙?꾩넚 (?쒕툝由??섍꼍 理쒖쟻??
 * 3. ?좎쭨 ?먮룞 蹂댁젙: ?좎쭨 ?놁씠 ?꾩넚?대룄 ?먮룞?쇰줈 ?ㅻ뒛 ?좎쭨瑜?梨꾩썙以? */

// --- [?꾩뿭 ?ㅼ젙] ---
const MAIN_SHEET_NAME = "2?숇뀈 ?꾩껜 諛?;
const CLASS_LIST = ["1諛?, "2諛?, "3諛?, "4諛?, "5諛?, "6諛?, "7諛?, "8諛?, "9諛?, "10諛?];

/**
 * [onOpen] ?곷떒 硫붾돱 ?앹꽦
 */
function onOpen() {
  SpreadsheetApp.getUi().createMenu('?뱷 吏꾨룄???꾧뎄')
    .addItem('?? 2?숇뀈???쒗듃 ?앹꽦 諛?珥덇린??, 'setupSystem')
    .addItem('?봽 吏湲?利됱떆 ?숆린??(?섎룞)', 'manualSync')
    .addSeparator()
    .addItem('??[?쒕툝由우슜] 10遺꾨쭏???먮룞 ?숆린??耳쒓린', 'setupTimeTrigger')
    .addSeparator()
    .addItem('?좑툘 ?꾩껜 ?ㅼ떆 ?숆린??(媛뺤젣)', 'forceSyncAll')
    .addItem('?뮕 ?꾩?留?, 'showHelp')
    .addToUi();
}

/**
 * [setupSystem] 1~10諛??쒗듃 ?앹꽦 諛??쒕∼?ㅼ슫 ?ㅼ젙
 */
function setupSystem() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let createdCount = 0;

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
  
  const mainSheet = ss.getSheetByName(MAIN_SHEET_NAME);
  if (mainSheet) {
    mainSheet.getRange("E1").setValue("?꾩넚 ?곹깭").setBackground("#f3f3f3").setFontWeight("bold").setHorizontalAlignment("center");
    mainSheet.setColumnWidth(5, 80);
    const classRule = SpreadsheetApp.newDataValidation().requireValueInList(CLASS_LIST).build();
    mainSheet.getRange("A2:A100").setDataValidation(classRule);
    const lastRow = mainSheet.getMaxRows();
    mainSheet.getRange(2, 5, lastRow - 1, 1).setHorizontalAlignment("center");
  }

  const ui = SpreadsheetApp.getUi();
  ui.alert("???명똿 ?꾨즺! " + createdCount + "媛쒖쓽 ?쒗듃媛 ?앹꽦?섏뿀?쇰ŉ ?쒕∼?ㅼ슫???ㅼ젙?섏뿀?듬땲??");
}

/**
 * [onEdit] ?ㅼ떆媛??몄쭛 ?몃━嫄? */
function onEdit(e) {
  if (!e || !e.range) return;
  const ss = e.source;
  const sheet = e.range.getSheet();
  if (sheet.getName().trim() !== MAIN_SHEET_NAME) return;
  const row = e.range.rowStart;
  const col = e.range.columnStart;
  if (row <= 1) return;

  if (col === 1 || col === 3) {
    const classValue = sheet.getRange(row, 1).getValue();
    const dateCell = sheet.getRange(row, 2);
    if (classValue !== "" && dateCell.getValue() === "") {
      dateCell.setValue(new Date()).setNumberFormat("MM/dd (ddd)");
    }
  }
  syncAllUnsentRecords(ss);
}

/**
 * [manualSync] ?섎룞 ?숆린?? */
function manualSync() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  syncAllUnsentRecords(ss);
  ss.toast("?숆린?붽? ?꾨즺?섏뿀?듬땲??", "2?숇뀈 ?먮룞 湲곕줉 ?꾨즺");
}

/**
 * [setupTimeTrigger] 10遺?二쇨린 ?몃━嫄??ㅼ젙
 */
function setupTimeTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(t => {
    if (t.getHandlerFunction() === 'syncAllUnsentRecordsForTrigger') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('syncAllUnsentRecordsForTrigger').timeBased().everyMinutes(10).create();
  SpreadsheetApp.getUi().alert("?? [2?숇뀈 ?꾩쟾 ?먮룞???쒖꽦??\n?댁젣 10遺꾨쭏???쒖뒪?쒖씠 誘몄쟾???곗씠?곕? 李얠븘 ?먮룞?쇰줈 蹂댁젙?꾩넚?⑸땲??");
}

function syncAllUnsentRecordsForTrigger() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  syncAllUnsentRecords(ss);
}

/**
 * [syncAllUnsentRecords] ?숆린???붿쭊
 */
function syncAllUnsentRecords(ss) {
  const mainSheet = ss.getSheetByName(MAIN_SHEET_NAME);
  if (!mainSheet) return;

  const dataRange = mainSheet.getDataRange();
  const data = dataRange.getValues();
  let syncCount = 0;

  for (let i = 1; i < data.length; i++) {
    const className = data[i][0].toString().trim();
    let dateVal = data[i][1];
    const progressVal = data[i][2];
    const summaryVal = data[i][3];
    const statusVal = data[i][4];

    if (className && progressVal && statusVal !== "??) {
      if (!dateVal || dateVal === "") {
        dateVal = new Date();
        mainSheet.getRange(i + 1, 2).setValue(dateVal).setNumberFormat("MM/dd (ddd)");
      }

      let targetName = className;
      if (!targetName.includes("諛?) && !isNaN(targetName)) targetName += "諛?;
      
      const targetSheet = ss.getSheetByName(targetName);
      if (targetSheet) {
        targetSheet.insertRowAfter(1);
        targetSheet.getRange(2, 1, 1, 3).setValues([[dateVal, progressVal, summaryVal]]);
        targetSheet.getRange("A2").setNumberFormat("MM/dd (ddd)");
        targetSheet.getRange(2, 2).setWrap(true);
        targetSheet.getRange(2, 3).setWrap(true);
        
        mainSheet.getRange(i + 1, 5).setValue("??).setHorizontalAlignment("center");
        syncCount++;
      }
    }
  }
}

function forceSyncAll() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  const response = ui.alert('媛뺤젣 ?щ룞湲고솕', '?대? ???쒖떆????ぉ??紐⑤몢 ?ㅼ떆 ?꾩넚?좉퉴??', ui.ButtonSet.YES_NO);
  if (response !== ui.Button.YES) return;

  const mainSheet = ss.getSheetByName(MAIN_SHEET_NAME);
  const lastRow = mainSheet.getLastRow();
  if (lastRow > 1) mainSheet.getRange(2, 5, lastRow - 1, 1).clearContent();
  syncAllUnsentRecords(ss);
}

function showHelp() {
  const msg = "?뱷 2?숇뀈 臾명븰 吏꾨룄???ъ슜 媛?대뱶\n\n" +
              "1. ?숆툒怨?吏꾨룄 ?댁슜???낅젰?섏꽭??\n" +
              "2. ?좎쭨瑜?鍮쇰㉨?대룄 ?숆린?????먮룞?쇰줈 ?ㅻ뒛 ?좎쭨媛 ?낅젰?⑸땲??\n" +
              "3. ?쒕툝由??ъ슜?먮뒗 [10遺꾨쭏???먮룞 ?숆린??耳쒓린]瑜?異붿쿇?⑸땲??";
  SpreadsheetApp.getUi().alert(msg);
}
