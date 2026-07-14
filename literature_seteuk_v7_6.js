/**
 * ?럳 2?숇뀈 臾명븰 ?명듅 珥덉젙諛 ?앹꽦湲?(V8.0 ?곸슜??踰꾩쟾)
 * ?쒖옉: AI 援먯쑁 鍮꾩꽌 (Antigravity)
 * 
 * [V8.0 二쇱슂 ?뱀쭠]
 * 1. 309紐??洹쒕え ?몄썝 理쒖쟻??(?곗씠??罹먯떛 湲곗닠 ?곸슜)
 * 2. 臾닿????ㅽ뻾: ?대┃ 利됱떆 ?꾩껜 珥덇린??諛??앹꽦 ?쒖옉
 * 3. ?ㅻ쪟 ?쒓컖?? [?뺤씤?꾩슂] ?щ????낆? ?뚮???#cfe2f3)?쇰줈 媛뺤“
 * 4. ?먮룞???좎?: 釉뚮씪?곗?瑜??レ븘??30珥덈쭏???먮룞?쇰줈 源⑥뼱???묒뾽 ?섑뻾
 * 5. 理쒖쥌 由ы룷?? ?묒뾽 ?꾨즺 ???깆쟻?쒖? ?ㅻ쪟 ?듦퀎瑜??붾젅洹몃옩?쇰줈 ?꾩넚
 */

const CONFIG = {
  MODEL_NAME: "gemini-3.1-flash-lite", 
  API_KEY: "", // 蹂댁븞 二쇱쓽: 怨듦컻 ??μ냼 ?낅줈??湲덉?
  RESPONSE_SHEET_URL: "https://docs.google.com/spreadsheets/d/1UAO-OHKMDtc8J50pNYcB4SGthiLEJtvVFoOZihjwGWw/edit",
  TARGET_SHEET_URL: "https://docs.google.com/spreadsheets/d/1JCrVEDhivEJyI4KZD1dt5SRcBECjsHOx0kuD35Usqp4/edit",
  BATCH_SIZE: 5,        
  DELAY_TIME: 30 * 1000, 
  TELEGRAM_TOKEN: "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY",
  TELEGRAM_CHAT_ID: "8518409134",
  STOP_AFTER: 309,      
  ERROR_COLOR: "#cfe2f3" 
};

/**
 * ?곷떒 硫붾돱 ?앹꽦
 */
function onOpen() {
  SpreadsheetApp.getUi().createMenu('???명듅 V8.0 ?곸슜')
    .addItem('?? [?꾩껜 ?곗씠????젣 ??泥섏쓬遺???쒖옉]', 'resetAndStartFresh')
    .addSeparator()
    .addItem('?띰툘 [以묐떒???묒뾽 ?댁뼱???섍린]', 'updateSeteukDirectly')
    .addItem('?썞 紐⑤뱺 ?먮룞???묒뾽 以묒?', 'clearAllTriggers')
    .addToUi();
}

/**
 * [珥덇린?? 紐⑤뱺 ?댁슜??吏?곌퀬 利됱떆 1踰덈????ㅽ뻾?⑸땲?? (?뺤씤 ?앹뾽 ?놁쓬)
 */
function resetAndStartFresh() {
  const targetSS = SpreadsheetApp.openByUrl(CONFIG.TARGET_SHEET_URL);
  const sheets = targetSS.getSheets();
  
  // 紐⑤뱺 ?쒗듃 ?댁슜 珥덇린??(C:D??
  sheets.forEach(sheet => {
    const lastRow = sheet.getLastRow();
    if (lastRow > 1) {
      sheet.getRange(2, 3, lastRow - 1, 2).clearContent();
      sheet.getRange(2, 3, lastRow - 1, 1).setBackground(null); // 諛곌꼍??珥덇린??    }
  });

  clearAllTriggers();
  
  // 吏꾪뻾 ?곹깭 珥덇린??  const props = PropertiesService.getScriptProperties();
  props.setProperty('PROCESSED_TOTAL', '0');
  props.setProperty('ERROR_COUNT', '0');
  props.setProperty('LAST_INDEX', '0'); // ?묐떟吏 ?쎄린 ?쒖옉??
  updateSeteukDirectly(); // 利됱떆 泥??ㅽ뻾
}

/**
 * 硫붿씤 ?붿쭊: 309紐낆쓣 ?⑥쑉?곸쑝濡?李얠븘 ?앹꽦
 */
function updateSeteukDirectly() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const responseSheet = SpreadsheetApp.openByUrl(CONFIG.RESPONSE_SHEET_URL).getSheets()[0];
  const responses = responseSheet.getDataRange().getValues();
  const targetSS = SpreadsheetApp.openByUrl(CONFIG.TARGET_SHEET_URL);
  
  const props = PropertiesService.getScriptProperties();
  let totalProcessed = parseInt(props.getProperty('PROCESSED_TOTAL') || '0', 10);
  let errorCount = parseInt(props.getProperty('ERROR_COUNT') || '0', 10);
  let lastIndex = parseInt(props.getProperty('LAST_INDEX') || '0', 10);

  // 309紐??쒗븳 泥댄겕
  if (totalProcessed >= CONFIG.STOP_AFTER) {
    finalizeWork(totalProcessed, errorCount);
    return;
  }

  let currentBatchProcessed = 0;
  let sheetCache = {}; // ?쒗듃 ?곗씠???꾩떆 蹂닿? (?띾룄 理쒖쟻??

  try {
    for (let i = lastIndex + 1; i < responses.length; i++) {
      if (currentBatchProcessed >= CONFIG.BATCH_SIZE) {
        props.setProperty('LAST_INDEX', (i - 1).toString());
        break;
      }

      const rowData = responses[i];
      const hakbunRaw = String(rowData[1] || "").replace(/[^0-9]/g, '');
      if (hakbunRaw.length < 5) continue;

      const classNum = parseInt(hakbunRaw.substring(1, 3), 10);
      const studentNum = parseInt(hakbunRaw.substring(3, 5), 10);
      const tabName = classNum + "諛?;

      // ?쒗듃 ?곗씠??罹먯떛 (留ㅻ쾲 getValues?섏? ?딆쓬)
      if (!sheetCache[tabName]) {
        const targetSheet = targetSS.getSheetByName(tabName);
        if (targetSheet) {
          sheetCache[tabName] = {
            obj: targetSheet,
            data: targetSheet.getDataRange().getValues()
          };
        }
      }

      const cache = sheetCache[tabName];
      if (!cache) continue;

      const rowIdxInSheet = cache.data.findIndex(r => String(r[0]) === String(studentNum));

      if (rowIdxInSheet !== -1) {
        const existingVal = String(cache.data[rowIdxInSheet][2] || "").trim(); 
        
        // C?댁씠 鍮꾩뼱?덈뒗 寃쎌슦?먮쭔 ?앹꽦 (?먮뒗 ?댁쟾????젣??寃쎌슦)
        if (!existingVal || existingVal === "" || existingVal === "誘몄젣異?) {
            ss.toast(`${tabName} ${studentNum}踰??앹꽦 以?.. (${totalProcessed + 1}/${CONFIG.STOP_AFTER})`, "?쨼 AI ?묐룞");
            
            const isTypeB = rowData[3] && String(rowData[3]).includes("B??);
            const seteuk = callGeminiWithRetry(rowData, isTypeB);
            
            const targetCell = cache.obj.getRange(rowIdxInSheet + 1, 3);
            targetCell.setValue(seteuk);
            cache.obj.getRange(rowIdxInSheet + 1, 4).setValue(calculateByte(seteuk));
            
            // ?ㅻ쪟 ?щ? 媛뺤“ (?낆? ?뚮???
            if (seteuk.includes("[?뺤씤?꾩슂]")) {
              targetCell.setBackground(CONFIG.ERROR_COLOR);
              errorCount++;
            }

            totalProcessed++;
            currentBatchProcessed++;
            props.setProperty('PROCESSED_TOTAL', totalProcessed.toString());
            props.setProperty('ERROR_COUNT', errorCount.toString());
        }
      }
      
      // 留덉?留??몃뜳??媛깆떊
      if (i === responses.length - 1) {
        props.setProperty('LAST_INDEX', i.toString());
      }
    }
  } catch (e) {
    console.error("?ㅻ쪟 諛쒖깮: " + e.toString());
  }

  SpreadsheetApp.flush(); // 媛뺤젣 諛섏쁺

  // ?ㅼ쓬 ?덉빟 ?먮뒗 醫낅즺 泥섎━
  if (currentBatchProcessed > 0 && totalProcessed < CONFIG.STOP_AFTER) {
    setupNextTrigger();
  } else {
    finalizeWork(totalProcessed, errorCount);
  }
}

/**
 * 紐⑤뱺 ?묒뾽 ?꾨즺 泥섎━ 諛??붾젅洹몃옩 怨듭?
 */
function finalizeWork(total, errors) {
  clearAllTriggers();
  const summary = `?럳 [臾명븰 ?명듅 ?앹꽦 ?꾨즺 蹂닿퀬]\n\n?꾩껜 泥섎━ ?몄썝: ${total}紐?n?뺤씤 ?꾩슂(?ㅻ쪟): ${errors}嫄?n\n紐⑤뱺 ?숈깮???묒뾽???앸궗?듬땲?? ?쒗듃???뚮???????뺤씤??二쇱꽭??`;
  sendTelegramNotification(summary);
  SpreadsheetApp.getActiveSpreadsheet().toast("309紐?理쒖쥌 ?묒뾽??紐⑤몢 ?꾨즺?섏뿀?듬땲??", "??理쒖쥌 ?꾨즺");
}

/**
 * AI ?몄텧 諛?怨좊룄?붾맂 ?꾨＼?꾪듃 (V8)
 */
/**
 * V10 ?뺣? 蹂댁젙: 遺꾨웾怨??꾧껐?깆쓣 寃利앺븯??遺議깊븷 寃쎌슦 理쒕? 3???먮룞 ?ъ떆?꾪빀?덈떎.
 */
/**
 * V12 ?뺣? 蹂댁젙: 遺꾨웾怨??ъ떎?깆쓣 寃?섑븯??220~330諛붿씠???ъ씠濡??앹꽦?⑸땲??
 */
function callGeminiWithRetry(rowData, isB) {
  const prompt = createPromptV8(rowData, isB);
  let finalResult = "";
  
  for (let attempt = 0; attempt < 3; attempt++) {
    let res = callGemini(prompt);
    if (!res || res.startsWith("?먮윭")) continue;
    
    res = cleanResponse(res);
    const bCount = calculateByte(res);
    const endsCorrectly = res.endsWith('.') || res.endsWith('??) || res.endsWith('??);

    // V12 ?寃? 220~350諛붿씠??(?덈Т 湲몄뼱???ъ떆??
    if (bCount >= 220 && bCount <= 350 && endsCorrectly) {
      return res;
    }
    
    finalResult = res;
    console.warn(`[?쒕룄 ${attempt+1}] 遺꾨웾 遺?곸젅(${bCount}B). ?ㅼ떆 ?앹꽦?⑸땲??`);
    Utilities.sleep(1500); 
  }
  
  return (finalResult && finalResult.length > 20) ? "[湲몄씠二쇱쓽] " + finalResult : "[?뺤씤?꾩슂] ?앹꽦 ?ㅽ뙣";
}

function cleanResponse(text) {
  return text ? text.replace(/\*\*.*?\*\*/g, "").replace(/Initial thought.*?\n/gi, "").replace(/```.*?```/gs, "").replace(/\\n/g, " ").trim() : "";
}

/**
 * V10 ?꾨＼?꾪듃: 湲곗닠???⑹뼱瑜?諛곗젣?섍퀬 6媛?臾몄옣??援ъ껜?곸씤 援ъ“瑜?紐낆떆?⑸땲??
 */
/**
 * V12 ?꾨＼?꾪듃: ?숈깮 ?듬? 湲곕컲 ?ъ떎???쒖닠 (250~300Byte ?寃?
 */
function createPromptV8(r, isB) {
  const d = r.map(v => (v === undefined || v === null || v === "" || v === " ") ? "?곗씠?곗뾾?? : v);
  const dataStr = isB ? `怨듦컙(${d[10]}), 遺?꾨윭?(${d[11]}), ?ㅼ쭚(${d[12]})` : `?μ냼(${d[4]}), ?뚮━(${d[5]}), ?섎Т(${d[6]}), ?댁쭞(${d[7]}), 湲곕텇(${d[8]}), ?ㅼ쭚(${d[9]})`;
  
  return `怨좉탳 援?뼱 援먯궗濡쒖꽌 ?숈깮?????쒕룞 ?듬???諛뷀깢?쇰줈 ?앺솢湲곕줉遺 ?명듅???묒꽦?섏꽭??

[?꾩닔 洹쒖튃 - ?꾨컲 ???ъ옉??
1. **?ъ떎 湲곕컲**: ?낅젰 ?곗씠?곗뿉 湲곗닠???숈깮???앷컖怨?媛먯젙留??ъ슜?섏뿬 ?대갚?섍쾶 ?묒꽦?섏꽭?? ?덈? ?댁슜??吏?대궡??誘명솕?섍굅??袁몃?吏 留덉꽭??
2. **遺꾨웾**: 怨듬갚 ?ы븿 ?쒓? 80~100???댁쇅 (**250~300諛붿씠???꾩닔**)濡?吏㏐퀬 紐낅즺?섍쾶 ?묒꽦?섏꽭??
3. **?뺤떇**: 諛섎뱶??{"seteuk": "?댁슜..."} ?뺥깭??JSON?쇰줈留??묐떟?섏꽭??
4. **?쒖옉/??*: "?ㅻ룞二쇱쓽 '?쎄쾶 ?뚯뼱吏???瑜??듯빐 "濡??쒖옉?섍퀬 紐낆궗???대?(~?? ~??濡??앸궪 寃?

?낅젰 ?곗씠?? ${dataStr}
異쒕젰:`;
}

function calculateByte(s) {
  return s ? s.split('').reduce((b, char) => b + (char.charCodeAt(0) > 128 ? 3 : 1), 0) : 0;
}

function callGemini(prompt) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.MODEL_NAME}:generateContent?key=${CONFIG.API_KEY}`;
  const safetySettings = [{ "category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE" }, { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE" }, { "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE" }, { "category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE" }];
  
  const payload = { 
    "contents": [{ "parts": [{ "text": prompt }] }], 
    "generationConfig": { 
      "temperature": 0.5, // 李쎌쓽???듭젣 (?ъ떎 湲곕컲 ?쒖닠 ?좊룄)
      "maxOutputTokens": 500,
      "response_mime_type": "application/json" 
    },
    "safetySettings": safetySettings 
  };
  
  try {
    const res = UrlFetchApp.fetch(url, { "method": "post", "contentType": "application/json", "payload": JSON.stringify(payload), "muteHttpExceptions": true });
    const json = JSON.parse(res.getContentText());
    
    if (json.candidates && json.candidates[0].content) {
      const respText = json.candidates[0].content.parts[0].text;
      const parsed = JSON.parse(respText);
      return parsed.seteuk || "?먮윭: JSON ?꾨뱶 ?꾨씫";
    }
    return "?먮윭: ?묐떟 援ъ“ ?댁긽";
  } catch(e) { return "?먮윭: " + e.toString(); }
}

function setupNextTrigger() {
  clearAllTriggers();
  Utilities.sleep(1000);
  try {
    ScriptApp.newTrigger('updateSeteukDirectly').timeBased().after(CONFIG.DELAY_TIME).create();
  } catch (e) {
    Utilities.sleep(3000);
    ScriptApp.newTrigger('updateSeteukDirectly').timeBased().after(CONFIG.DELAY_TIME).create();
  }
}

function sendTelegramNotification(message) {
  const url = `https://api.telegram.org/bot${CONFIG.TELEGRAM_TOKEN}/sendMessage`;
  try {
    UrlFetchApp.fetch(url, { "method": "post", "contentType": "application/json", "payload": JSON.stringify({ "chat_id": CONFIG.TELEGRAM_CHAT_ID, "text": message }) });
  } catch (e) {}
}

function clearAllTriggers() {
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction() === 'updateSeteukDirectly') ScriptApp.deleteTrigger(t);
  });
}

