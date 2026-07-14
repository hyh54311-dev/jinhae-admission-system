/**
 * ?뱷 2026?숇뀈??2?숇뀈 臾명븰 吏꾨룄???먮룞???쒖뒪??(理쒖쥌 ?듯빀 踰꾩쟾)
 * ?쒖옉: AI 援먯쑁 鍮꾩꽌 (Antigravity)
 * 
 * [二쇱슂 湲곕뒫]
 * 1. ?숆툒紐?A?? ?좏깮 ??'理쒖쥌 ?섏뾽??B??'???ㅻ뒛 ?좎쭨 ?먮룞 ?낅젰
 * 2. 吏꾨룄?댁슜(C?? ?낅젰 ???대떦 ?숆툒 ?쒗듃濡??곗씠???ㅼ떆媛??꾩넚
 * 3. ?숆툒 ?쒗듃(1~10諛?媛 ?놁쑝硫??먮룞?쇰줈 ?앹꽦 ?쒖븞
 * 4. ?곗씠???꾩넚 ???쒖떇(以꾨컮轅? ???덈퉬) ?먮룞 理쒖쟻?? */

// ?꾩뿭 ?ㅼ젙
const MAIN_SHEET_NAME = "2?숇뀈 ?꾩껜 諛?;
const CLASS_LIST = ["1諛?, "2諛?, "3諛?, "4諛?, "5諛?, "6諛?, "7諛?, "8諛?, "9諛?, "10諛?];

/**
 * [onOpen] ?곷떒 硫붾돱瑜??앹꽦?⑸땲??
 */
function onOpen() {
  SpreadsheetApp.getUi().createMenu('?뱷 吏꾨룄???꾧뎄')
    .addItem('?? 1~10諛??쒗듃 ??踰덉뿉 留뚮뱾湲?, 'autoCreateSheets')
    .addSeparator()
    .addItem('?뮕 ?ъ슜 諛⑸쾿 ?덈궡', 'showHelp')
    .addToUi();
}

/**
 * [autoCreateSheets] 1~10諛??쒗듃媛 ?놁쑝硫?'6諛? ?쒗듃瑜?蹂듭궗?섍굅???덈줈 留뚮벊?덈떎.
 */
function autoCreateSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const templateSheet = ss.getSheetByName("6諛?);
  let createdCount = 0;

  CLASS_LIST.forEach(name => {
    if (!ss.getSheetByName(name)) {
      if (templateSheet) {
        templateSheet.copyTo(ss).setName(name).showSheet();
      } else {
        const newSheet = ss.insertSheet(name);
        newSheet.appendRow(["?좎쭨", "吏꾨룄 ?꾪솕", "鍮꾧퀬/?붿빟"]);
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
 * [onEdit] ? ?섏젙 ???먮룞?쇰줈 ?묐룞?섎뒗 ?듭떖 ?붿쭊
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
    // 1. A???숆툒紐? ?낅젰 ??B???좎쭨) ?명똿
    if (col === 1 && value != "") {
      const dateCell = sheet.getRange(row, 2);
      dateCell.setValue(new Date()).setNumberFormat("MM/dd (ddd)");
      return; // ?좎쭨留??명똿?섍퀬 醫낅즺
    }

    // 2. C??吏꾨룄?꾪솴) ?낅젰 ???대떦 諛??쒗듃濡??대룞
    if (col === 3 && value != "") {
      const className = sheet.getRange(row, 1).getValue();
      if (!className) {
        SpreadsheetApp.getActive().toast("?좑툘 ?숆툒紐낆쓣 癒쇱? ?좏깮?댁＜?몄슂!", "?ㅻ쪟", 3);
        return;
      }

      let targetSheet = e.source.getSheetByName(className);
      
      // ?쒗듃媛 ?놁쑝硫??앹꽦 ?щ? ?뺤씤
      if (!targetSheet) {
        const ui = SpreadsheetApp.getUi();
        const response = ui.alert('?뚮┝', className + ' ?쒗듃媛 ?놁뒿?덈떎. 吏湲?留뚮뱶?쒓쿋?듬땲源?', ui.ButtonSet.YES_NO);
        if (response == ui.Button.YES) {
          autoCreateSheets();
          targetSheet = e.source.getSheetByName(className);
        } else {
          return;
        }
      }

      // ?곗씠???꾩넚 (2?됱뿉 ?쎌엯)
      const dateVal = sheet.getRange(row, 2).getValue();
      const summaryVal = sheet.getRange(row, 4).getValue(); // D??      
      targetSheet.insertRowAfter(1);
      const targetRange = targetSheet.getRange(2, 1, 1, 3);
      targetRange.setValues([[dateVal, value, summaryVal]]);
      
      // ?꾨━誘몄뾼 ?쒖떇 ?뺣━
      targetSheet.getRange("A2").setNumberFormat("MM/dd (ddd)");
      targetSheet.getRange(2, 2).setWrap(true); // ?먮룞 以꾨컮轅?      targetSheet.getRange(2, 3).setWrap(true);
      targetSheet.autoResizeColumns(1, 3);
      
      // ?꾨즺 ?뚮┝
      SpreadsheetApp.getActive().toast("??" + className + " 湲곕줉 ?꾨즺!", "?곗씠???꾩넚 ?깃났", 2);
    }
  } catch (err) {
    console.error(err);
  }
}

/**
 * [showHelp] ?ъ슜 諛⑸쾿 ?덈궡 ?앹뾽
 */
function showHelp() {
  const msg = "?뱷 ?ъ슜 諛⑸쾿\n\n" +
              "1. '?숆툒紐????좏깮?섎㈃ ?ㅻ뒛 ?좎쭨媛 ?먮룞?쇰줈 ?밸땲??\n" +
              "2. '吏꾨룄 ?꾪솴'???낅젰?섎㈃ ?대떦 諛??쒗듃濡??댁슜??蹂듭궗?⑸땲??\n" +
              "3. '鍮꾧퀬/?붿빟'???곸쑝硫??④퍡 蹂듭궗?⑸땲??\n" +
              "* 理쒖큹 1?? ??硫붾돱?먯꽌 '?쒗듃 ??踰덉뿉 留뚮뱾湲?瑜??뚮윭 沅뚰븳???뱀씤?댁＜?몄슂!";
  SpreadsheetApp.getUi().alert(msg);
}
