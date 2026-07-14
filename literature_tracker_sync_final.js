/**
 * ?뱷 2026?숇뀈??2?숇뀈 臾명븰 吏꾨룄???먮룞???쒖뒪??(理쒖쥌 ?듯빀 ?숆린??踰꾩쟾)
 * ?쒖옉: AI 援먯쑁 鍮꾩꽌 (Antigravity)
 */

// ?꾩뿭 ?ㅼ젙
const MAIN_SHEET_NAME = "2?숇뀈 ?꾩껜 諛?;
const CLASS_LIST = ["1諛?, "2諛?, "3諛?, "4諛?, "5諛?, "6諛?, "7諛?, "8諛?, "9諛?, "10諛?];

/**
 * [onOpen] ?곷떒 硫붾돱瑜??앹꽦?⑸땲??
 */
function onOpen() {
  SpreadsheetApp.getUi().createMenu('?뱷 吏꾨룄???꾧뎄')
    .addItem('?? 1~10諛??쒗듃 ?먮룞 ?앹꽦', 'setupSystem')
    .addItem('?봽 湲곗〈 湲곕줉 ?꾩껜 ?꾩넚?섍린(Sync)', 'syncExistingData')
    .addSeparator()
    .addItem('?뮕 ?ъ슜 諛⑸쾿 ?덈궡', 'showHelp')
    .addToUi();
}

/**
 * [setupSystem] 1~10諛??쒗듃媛 ?놁쑝硫??앹꽦?섍퀬 沅뚰븳???뱀씤諛쏆뒿?덈떎.
 */
function setupSystem() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const templateSheet = ss.getSheetByName("6諛?);
  let createdCount = 0;

  CLASS_LIST.forEach(name => {
    if (!ss.getSheetByName(name)) {
      if (templateSheet) {
        templateSheet.copyTo(ss).setName(name).showSheet();
      } else {
        const newSheet = ss.insertSheet(name);
        newSheet.appendRow(["?좎쭨", "吏꾨룄 ?꾪솴", "鍮꾧퀬/?붿빟"]);
        newSheet.getRange("A1:C1").setBackground("#444444").setFontColor("white").setFontWeight("bold");
      }
      createdCount++;
    }
  });

  if (createdCount > 0) {
    SpreadsheetApp.getUi().alert("??" + createdCount + "媛쒖쓽 ?숆툒 ?쒗듃媛 ?앹꽦?섏뿀?듬땲??");
  } else {
    SpreadsheetApp.getUi().alert("?뱄툘 紐⑤뱺 ?숆툒 ?쒗듃媛 ?대? 議댁옱?⑸땲??");
  }
}

/**
 * [syncExistingData] 硫붿씤 ?쒗듃???대? ?낅젰??紐⑤뱺 湲곕줉??諛섎퀎 ?쒗듃濡??쒓볼踰덉뿉 ?꾩넚?⑸땲??
 */
function syncExistingData() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.alert('湲곗냽 湲곕줉 ?꾩넚', 
                            '硫붿씤 ?쒗듃??紐⑤뱺 ?곗씠?곕? 媛?諛??쒗듃濡??꾩넚?섏떆寃좎뒿?덇퉴? \n\n' +
                            '二쇱쓽: ?대? ??꺼吏??곗씠?곌? ?덉쓣 寃쎌슦 以묐났?????덉뒿?덈떎.', 
                            ui.ButtonSet.YES_NO);
  
  if (response !== ui.Button.YES) return;

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const mainSheet = ss.getSheetByName(MAIN_SHEET_NAME);
  const data = mainSheet.getDataRange().getValues();
  let syncCount = 0;

  // ?쒕ぉ??0) ?쒖쇅?섍퀬 1?됰????앷퉴吏 ?ㅼ틪
  for (let i = 1; i < data.length; i++) {
    const className = data[i][0]; // A??    const dateVal = data[i][1];  // B??    const progressVal = data[i][2]; // C??    const summaryVal = data[i][3]; // D??
    if (className && progressVal) {
      const targetSheet = ss.getSheetByName(className);
      if (targetSheet) {
        targetSheet.insertRowAfter(1);
        targetSheet.getRange(2, 1, 1, 3).setValues([[dateVal, progressVal, summaryVal]]);
        
        // ?쒖떇 ?뺣━
        targetSheet.getRange("A2").setNumberFormat("MM/dd (ddd)");
        targetSheet.getRange(2, 2).setWrap(true);
        targetSheet.getRange(2, 3).setWrap(true);
        targetSheet.autoResizeColumns(1, 3);
        
        syncCount++;
      }
    }
  }

  ui.alert("??珥?" + syncCount + "媛쒖쓽 湲곕줉???꾩넚?섏뿀?듬땲??");
}

/**
 * [onEdit] ? ?섏젙 ???먮룞?쇰줈 ?묐룞?섎뒗 ?ㅼ떆媛??숆린???붿쭊
 */
function onEdit(e) {
  if (!e || !e.range) return;
  
  const range = e.range;
  const sheet = range.getSheet();
  if (sheet.getName() !== MAIN_SHEET_NAME || range.getRow() === 1) return;

  const row = range.getRow();
  const col = range.getColumn();
  const value = range.getValue();

  try {
    // 1. A???숆툒紐? ?낅젰 ??B???좎쭨) ?먮룞 ?명똿
    if (col === 1 && value != "") {
      const dateCell = sheet.getRange(row, 2);
      dateCell.setValue(new Date()).setNumberFormat("MM/dd (ddd)");
      return;
    }

    // 2. C??吏꾨룄?꾪솴) ?낅젰 ???대떦 諛??쒗듃濡??대룞
    if (col === 3 && value != "") {
      const className = sheet.getRange(row, 1).getValue();
      if (!className) return;

      let targetSheet = e.source.getSheetByName(className);
      if (!targetSheet) return; // ?쒗듃媛 ?놁쑝硫?以묐떒 (onEdit?먯꽌???먮룞?앹꽦 ?앹뾽 李⑤떒 - ?깅뒫 諛?沅뚰븳 ?댁뒋)

      const dateVal = sheet.getRange(row, 2).getValue();
      const summaryVal = sheet.getRange(row, 4).getValue(); // D??      
      targetSheet.insertRowAfter(1);
      targetSheet.getRange(2, 1, 1, 3).setValues([[dateVal, value, summaryVal]]);
      
      // ?쒖떇 ?뺣━
      targetSheet.getRange("A2").setNumberFormat("MM/dd (ddd)");
      targetSheet.getRange(2, 2).setWrap(true);
      targetSheet.getRange(2, 3).setWrap(true);
      targetSheet.autoResizeColumns(1, 3);
      
      SpreadsheetApp.getActive().toast("??" + className + " 湲곕줉 ?꾨즺!");
    }
  } catch (err) {
    console.error(err);
  }
}

/**
 * [showHelp] ?ъ슜 諛⑸쾿 ?덈궡 ?앹뾽
 */
function showHelp() {
  const msg = "?뱷 ?ъ슜 諛⑸쾿 ?덈궡\n\n" +
              "1. ?숆툒 ?좏깮: A?댁뿉??諛섏쓣 怨좊Ⅴ硫??좎쭨媛 ?먮룞 ?앹꽦?⑸땲??\n" +
              "2. 吏꾨룄 ?낅젰: C?댁뿉 ?낅젰?섎뒗 ?쒓컙 ?ㅼ떆媛꾩쑝濡?諛섎퀎 ??뿉 ?꾩쟻?⑸땲??\n\n" +
              "?봽 湲곗〈 湲곕줉 ?꾩넚: ?댁쟾???곸뼱???댁슜???쒓볼踰덉뿉 ??린?ㅻ㈃ 硫붾돱?먯꽌 '?봽 湲곗〈 湲곕줉 ?꾩껜 ?꾩넚?섍린'瑜??쒕쾲 ?뚮윭二쇱꽭??";
  SpreadsheetApp.getUi().alert(msg);
}
