/**
 * 吏꾪빐怨좊벑?숆탳 ?듯솕 ?붿빟 ?쒗듃 愿由??좏떥由ы떚
 * 1. 以묐났 ?쒓굅: ?숈씪 ?좎쭨/???湲곕줉 以?媛???댁슜??湲?寃껊쭔 ?④?
 * 2. 媛뺤젣 ?뺣젹: ?꾩껜 ?곗씠?곕? ?좎쭨 ?대┝李⑥닚(理쒖떊???쇰줈 ?뺣젹
 */

function runMaintenance() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  
  if (!sheet.getName().includes("??)) {
    const ui = SpreadsheetApp.getUi();
    const response = ui.alert("?뚮┝", "?듯솕 ?붿빟??湲곕줉???붾퀎 ?쒗듃(?? 2026??04???먯꽌 ?ㅽ뻾??二쇱꽭?? ?꾩옱 ?쒗듃?먯꽌 吏꾪뻾?좉퉴??", ui.ButtonSet.YES_NO);
    if (response == ui.Button.NO) return;
  }

  removeDuplicatesAndKeepLongest(sheet);
  forceSortDescending(sheet);
  
  SpreadsheetApp.getActiveSpreadsheet().toast("???쒗듃 ?뺣━ 諛??뺣젹???꾨즺?섏뿀?듬땲??");
}

/**
 * 以묐났 ?곗씠?곕? 李얠븘 媛??湲??붿빟蹂몃쭔 ?④린怨???젣?섎뒗 ?⑥닔
 */
function removeDuplicatesAndKeepLongest(sheet) {
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;

  const range = sheet.getRange(2, 1, lastRow - 1, 3);
  const data = range.getValues();
  
  // ?? "?좎쭨|?대쫫", 媛? { rowIdx: n, length: m }
  const uniqueMap = {};
  const rowsToDelete = [];

  for (let i = 0; i < data.length; i++) {
    const rawDate = data[i][0];
    const identity = String(data[i][1]).trim();
    const summary = String(data[i][2]).trim();
    
    // ?좎쭨 ?쒖???(鍮꾧탳??
    let dateStr = "";
    if (rawDate instanceof Date) {
      dateStr = Utilities.formatDate(rawDate, Session.getScriptTimeZone(), "yyyy/MM/dd HH:mm");
    } else {
      dateStr = String(rawDate).trim();
    }

    const key = `${dateStr}|${identity}`;

    if (uniqueMap[key]) {
      // ?대? 議댁옱?섎뒗 寃쎌슦 湲몄씠瑜?鍮꾧탳
      if (summary.length > uniqueMap[key].length) {
        // ?꾩옱 寃껋씠 ??湲몃㈃ ?댁쟾 寃껋쓣 ??젣 紐⑸줉??異붽?
        rowsToDelete.push(uniqueMap[key].rowIdx);
        // 留??낅뜲?댄듃
        uniqueMap[key] = { rowIdx: i + 2, length: summary.length };
      } else {
        // ?댁쟾 寃껋씠 ??湲멸굅??媛숈쑝硫??꾩옱 寃껋쓣 ??젣 紐⑸줉??異붽?
        rowsToDelete.push(i + 2);
      }
    } else {
      uniqueMap[key] = { rowIdx: i + 2, length: summary.length };
    }
  }

  // ??踰덊샇媛 ??寃껊?????젣?댁빞 ?몃뜳?ㅺ? 瑗ъ씠吏 ?딆쓬
  rowsToDelete.sort((a, b) => b - a);
  
  if (rowsToDelete.length > 0) {
    rowsToDelete.forEach(row => sheet.deleteRow(row));
    console.log(`[以묐났 ?쒓굅] 珥?${rowsToDelete.length}媛쒖쓽 以묐났 ?됱쓣 ??젣?덉뒿?덈떎.`);
  }
}

/**
 * ?쒗듃 ?꾩껜瑜??좎쭨 ?대┝李⑥닚?쇰줈 ?뺣젹?섎뒗 ?⑥닔
 */
function forceSortDescending(sheet) {
  const lastRow = sheet.getLastRow();
  if (lastRow > 1) {
    sheet.getRange(2, 1, lastRow - 1, 3).sort({column: 1, ascending: false});
    console.log(`[?뺣젹 ?꾨즺] ${sheet.getName()} ?쒗듃 ?대┝李⑥닚 ?뺣젹 ?꾨즺`);
  }
}
