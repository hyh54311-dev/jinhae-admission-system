/**
 * 2026?숇뀈??2?숇뀈 臾명븰 吏꾨룄??(媛쒖꽑 諛?理쒖쟻??踰꾩쟾)
 * - ?숆툒紐??좏깮 ???좎쭨 ?먮룞 ?낅젰
 * - 吏꾨룄 ?꾪솴 ?낅젰 ??媛쒕퀎 諛??쒗듃濡??곗씠???먮룞 遺꾨같
 * - 硫붾돱 異붽?濡?愿由??몄쓽??利앸?
 */

// Gemini ?곕룞 蹂??(?좏깮 ?ы빆)
const GEMINI_API_KEY = ""; // ?꾩슂 ???낅젰
const MODEL_NAME = "models/gemini-3.1-flash-lite"; 

/**
 * [異붽?] 硫붾돱 ?앹꽦 ?⑥닔
 * ?ㅽ봽?덈뱶?쒗듃媛 ?대┫ ???먮룞?쇰줈 ?묐룞?섏뿬 ?곷떒 硫붾돱瑜?留뚮벊?덈떎.
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('?뱷 吏꾨룄???꾧뎄')
    .addItem('1. 珥덇린 ?명똿 (?쒗듃 ?앹꽦/?쒕∼?ㅼ슫)', 'setupSystem')
    .addSeparator()
    .addItem('吏??臾몄쓽 (?⑹슂??', 'showContact')
    .addToUi();
}

/**
 * ?꾩?留?硫붿떆吏
 */
function showContact() {
  SpreadsheetApp.getUi().alert("吏꾨룄???먮룞???쒖뒪??v1.0\n?섏젙???꾩슂?섎㈃ ?⑹슂???좎깮?섍퍡 臾몄쓽?섏꽭??");
}

/**
 * [湲곕줉??珥덇린 ?명똿] 
 * 1~5諛??쒗듃瑜?留뚮뱾怨??쒕∼?ㅼ슫???명똿?⑸땲??
 */
function setupSystem() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. "6諛? ?쒗듃瑜??쒗뵆由우쑝濡?1~5諛??먮룞 ?앹꽦
  const templateSheet = ss.getSheetByName("6諛?);
  if (!templateSheet) {
    SpreadsheetApp.getUi().alert("?ㅻ쪟: '6諛? ?쒗듃媛 ?놁뒿?덈떎. 癒쇱? 6諛??쒗듃瑜?留뚮뱾??二쇱꽭??");
    return;
  }

  const targetClasses = ["1諛?, "2諛?, "3諛?, "4諛?, "5諛?];
  targetClasses.forEach(className => {
    if (!ss.getSheetByName(className)) {
      templateSheet.copyTo(ss).setName(className).showSheet();
    }
  });

  // 2. "2?숇뀈 ?꾩껜 諛? ?쒗듃 ?쒕∼?ㅼ슫 ?ㅼ젙
  const mainSheet = ss.getSheetByName("2?숇뀈 ?꾩껜 諛?) || ss.insertSheet("2?숇뀈 ?꾩껜 諛?);
  const classList = ["1諛?, "2諛?, "3諛?, "4諛?, "5諛?, "6諛?, "7諛?, "8諛?, "9諛?, "10諛?];
  
  const rule = SpreadsheetApp.newDataValidation()
                  .requireValueInList(classList)
                  .setAllowInvalid(false)
                  .build();
                  
  // A2遺??A100源뚯? ?쒕∼?ㅼ슫 ?곸슜 (?꾩슂??踰붿쐞 議곗젅)
  mainSheet.getRange("A2:A100").setDataValidation(rule);
  
  // ?쒕ぉ ???ㅼ젙 (?놁쓣 寃쎌슦 ?鍮?
  if (mainSheet.getRange("A1").getValue() === "") {
    mainSheet.getRange("A1:D1").setValues([["?숆툒紐?, "理쒖쥌 ?섏뾽??, "吏꾨룄 ?꾪솴", "鍮꾧퀬/?붿빟"]]);
    mainSheet.getRange("A1:D1").setBackground("#f3f3f3").setFontWeight("bold");
  }

  SpreadsheetApp.getUi().alert("珥덇린 ?명똿???꾨즺?섏뿀?듬땲?? ?댁젣 媛?諛섏쓣 ?좏깮?섍퀬 吏꾨룄瑜??낅젰?대낫?몄슂!");
}

/**
 * [?먮룞 ?ㅽ뻾 ?⑥닔] 
 * ?쒗듃 ?댁슜???섏젙???뚮쭏???먮룞?쇰줈 ?묐룞?⑸땲??
 */
function onEdit(e) {
  if (!e || !e.range) return;
  
  const range = e.range;
  const sheet = range.getSheet();
  const sheetName = sheet.getName();
  
  // "2?숇뀈 ?꾩껜 諛? ?쒗듃?먯꽌 ?쇱뼱??蹂寃쎌궗??쭔 媛먯?
  if (sheetName !== "2?숇뀈 ?꾩껜 諛?) return;
  
  const row = range.getRow();
  const col = range.getColumn();
  const value = range.getValue(); // e.value ???range.getValue()濡????뺥솗?섍쾶 媛?몄샂
  
  // ?쒕ぉ ??臾댁떆
  if (row === 1) return;

  try {
    // 1. A???숆툒紐? 蹂寃?-> B?댁뿉 ?좎쭨 ?먮룞 ?낅젰
    if (col === 1 && value != "") {
      const today = new Date();
      const dateCell = sheet.getRange(row, 2);
      dateCell.setValue(today);
      dateCell.setNumberFormat("MM/dd (ddd)"); 
    }
    
    // 2. C??吏꾨룄 ?꾪솴) ?낅젰 -> ?대떦 諛???쑝濡??곗씠??蹂듭궗
    if (col === 3 && value != "") {
      const className = sheet.getRange(row, 1).getValue();
      const dateVal = sheet.getRange(row, 2).getValue();
      const summaryVal = sheet.getRange(row, 4).getValue(); // D???붿빟
      
      if (!className) {
        SpreadsheetApp.getActiveSpreadsheet().toast("?숆툒紐낆씠 ?좏깮?섏? ?딆븯?듬땲??", "?좑툘 二쇱쓽", 3);
        return;
      }
      
      const targetSheet = sheet.getParent().getSheetByName(className);
      if (targetSheet) {
        // 湲곗〈 ?곗씠?곕? 2?됱뿉 ?쎌엯 (?덈줈???뺣낫媛 ?꾨줈 ?ㅻ룄濡?
        targetSheet.insertRowAfter(1);
        targetSheet.getRange(2, 1, 1, 3).setValues([[dateVal, value, summaryVal]]);
        
        // ?쒖떇 ?뺣━
        targetSheet.getRange("A2").setNumberFormat("MM/dd (ddd)");
        targetSheet.getRange(2, 2).setWrap(true);
        targetSheet.getRange(2, 3).setWrap(true);
        targetSheet.autoResizeColumns(1, 3);
        
        // ?쇰뱶諛?(?좎뒪??硫붿떆吏)
        SpreadsheetApp.getActiveSpreadsheet().toast(`${className} ?쒗듃??吏꾨룄媛 湲곕줉?섏뿀?듬땲??`, "??湲곕줉 ?꾨즺", 2);
      }
    }
  } catch (err) {
    console.error("?ㅻ쪟 諛쒖깮: " + err.message);
  }
}
