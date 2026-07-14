/**
 * ?럳 2?숇뀈 臾명븰 ?명듅 珥덉젙諛 ?앹꽦湲?(V7.5 - 怨좎냽 ?꾩＜ 諛?1??吏묒쨷 泥섎━??
 * ?쒖옉: AI 援먯쑁 鍮꾩꽌 (Antigravity)
 * 
 * [?낅뜲?댄듃 ?댁슜]
 * 1. 諛곗튂 ?ъ씠利?1濡?議곗젙 (?덉젙??洹밸???
 * 2. ?ㅽ뻾 ?쒓컙 諛??좏겕 ?쒖빟 ?댁젣 (臾댄븳 猷⑦봽???몃━嫄??쒖뒪??
 * 3. ???諛⑹떇 理쒖쟻??(?대떦 ?됰쭔 利됱떆 ???
 */

const CONFIG = {
  MODEL_NAME: "gemini-2.5-flash", 
  API_KEY: "", // 蹂댁븞 二쇱쓽: 怨듦컻 ??μ냼 ?낅줈??湲덉?
  RESPONSE_SHEET_URL: "https://docs.google.com/spreadsheets/d/1UAO-OHKMDtc8J50pNYcB4SGthiLEJtvVFoOZihjwGWw/edit",
  TARGET_SHEET_URL: "https://docs.google.com/spreadsheets/d/1JCrVEDhivEJyI4KZD1dt5SRcBECjsHOx0kuD35Usqp4/edit",
  BATCH_SIZE: 1,        
  SLEEP_TIME: 2000,     
  MAX_RETRY: 3,
  TELEGRAM_TOKEN: "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY",
  TELEGRAM_CHAT_ID: "8518409134"
};

function onOpen() {
  SpreadsheetApp.getUi().createMenu('???명듅 V7.5 理쒖쥌')
    .addItem('?띰툘 [?묒뾽 ?쒖옉/?ш컻]', 'updateSeteukDirectly')
    .addSeparator()
    .addItem('?썞 ?먮룞 ?묒뾽 ?꾩쟾 以묐떒', 'clearAllTriggers')
    .addToUi();
}

/**
 * ?꾨㈃ ?ъ옉????湲곗〈 ?곗씠?곕? 鍮꾩슦???⑥닔 (?좏깮 ?ы빆)
 */
function startFreshFullBatchV7() {
  const ui = SpreadsheetApp.getUi();
  const res = ui.alert('?좑툘 ?꾨㈃ ?ъ옉???뺤씤', '紐⑤뱺 ?댁슜???덈줈 留뚮뱾源뚯슂? (湲곗〈 ?댁슜? ??젣?⑸땲??', ui.ButtonSet.YES_NO);
  if (res !== ui.Button.YES) return;

  const targetSS = SpreadsheetApp.openByUrl(CONFIG.TARGET_SHEET_URL);
  targetSS.getSheets().forEach(s => {
    const lastRow = s.getLastRow();
    if (lastRow > 1) s.getRange(2, 3, lastRow - 1, 2).clearContent(); 
  });
  
  clearAllTriggers();
  updateSeteukDirectly();
}

/**
 * 硫붿씤 ?ㅽ뻾 ?⑥닔 (?몃━嫄곗뿉 ?섑빐 ?먮룞 諛섎났 ?ㅽ뻾??
 */
function updateSeteukDirectly() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const responseSheet = SpreadsheetApp.openByUrl(CONFIG.RESPONSE_SHEET_URL).getSheets()[0];
  const responses = responseSheet.getDataRange().getValues();
  const targetSS = SpreadsheetApp.openByUrl(CONFIG.TARGET_SHEET_URL);
  
  let processedNow = 0;

  try {
    for (let i = 1; i < responses.length; i++) {
      if (processedNow >= CONFIG.BATCH_SIZE) break; 

      const rowData = responses[i];
      const hakbunRaw = String(rowData[1] || "").replace(/[^0-9]/g, '');
      if (hakbunRaw.length < 5) continue;

      const classNum = parseInt(hakbunRaw.substring(1, 3), 10);
      const studentNum = parseInt(hakbunRaw.substring(3, 5), 10);
      const tabName = classNum + "諛?;

      const targetSheet = targetSS.getSheetByName(tabName);
      if (!targetSheet) continue;

      const targetValues = targetSheet.getDataRange().getValues();
      const rowIdxInSheet = targetValues.findIndex(r => String(r[0]) === String(studentNum));

      if (rowIdxInSheet !== -1) {
        const existingVal = String(targetValues[rowIdxInSheet][2] || "").trim(); 
        
        if (!existingVal || existingVal === "" || existingVal === "誘몄젣異?) {
            ss.toast(`${tabName} ${studentNum}踰??앹꽦 以?..`, "?쨼 AI ?묐룞 以?);
            
            const isTypeB = rowData[3] && String(rowData[3]).includes("B??);
            const seteuk = callGeminiWithRetry(rowData, isTypeB);
            
            targetSheet.getRange(rowIdxInSheet + 1, 3).setValue(seteuk);
            targetSheet.getRange(rowIdxInSheet + 1, 4).setValue(calculateByte(seteuk));
            
            processedNow++;
            Utilities.sleep(CONFIG.SLEEP_TIME);
        }
      }
    }
  } catch (e) {
    console.error("?ㅽ뻾 ?ㅻ쪟: " + e.toString());
    ss.toast("?ㅻ쪟 諛쒖깮: " + e.toString(), "???먮윭");
  }

  if (processedNow > 0) {
    ss.toast("30珥????ㅼ쓬 ?숈깮 ?묒뾽???쒖옉?⑸땲??..", "???덉빟??);
    setupNextTrigger();
  } else {
    clearAllTriggers();
    ss.toast("紐⑤뱺 ?숈깮???묒뾽???꾨즺?섏뿀?듬땲??", "???꾨즺");
    sendTelegramNotification("?럳 [?명듅 ?먮룞 ?앹꽦 ?꾨즺]\n\n紐⑤뱺 ?숈깮??臾명븰 ?명듅 珥덉븞 ?앹꽦???깃났?곸쑝濡?留덈Т由щ릺?덉뒿?덈떎. ?쒗듃瑜??뺤씤??二쇱꽭??");
  }
}

/**
 * 吏?ν삎 蹂댁젙 諛??ъ떆??濡쒖쭅
 */
function callGeminiWithRetry(rowData, isB) {
  const prompt = createPromptV7(rowData, isB);
  let lastResult = "";
  
  for (let i = 0; i < CONFIG.MAX_RETRY; i++) {
    let res = callGemini(prompt);
    
    if (!res.startsWith("?먮윭") && !res.startsWith("API?ㅻ쪟")) {
       res = cleanResponse(res);
       
       if (!res.includes("?쎄쾶 ?뚯뼱吏???)) {
         res = "?ㅻ룞二쇱쓽 '?쎄쾶 ?뚯뼱吏???瑜??듯빐 " + res;
       }
       
       if (res.length > 30 && !res.endsWith('.')) {
         res = res + ".";
       }
       
       if (res.length > 50) return res;
       lastResult = res;
    } else {
       lastResult = res;
    }
    Utilities.sleep(2000); 
  }
  
  return "[?뺤씤?꾩슂] " + lastResult;
}

function cleanResponse(text) {
  if (!text) return "";
  return text
    .replace(/\*\*.*?\*\*/g, "")
    .replace(/Initial thought.*?\n/gi, "")
    .replace(/```.*?```/gs, "")
    .replace(/\\n/g, " ")
    .trim();
}

function createPromptV7(r, isB) {
  const dataStr = isB 
    ? `怨듦컙(${r[10]}), 遺?꾨윭?(${r[11]}), ?ㅼ쭚(${r[12]})` 
    : `?μ냼(${r[4]}), ?뚮━(${r[5]}), ?섎Т(${r[6]}), ?댁쭞(${r[7]}), 湲곕텇(${r[8]}), ?ㅼ쭚(${r[9]})`;
    
  return `?뱀떊? ??쒕?援?怨좊벑?숆탳 援?뼱 援먯궗?낅땲?? ?꾨옒 ?곗씠?곕? 諛뷀깢?쇰줈 ?숆탳?앺솢湲곕줉遺??'臾명븰 ?명듅(?몃??λ젰 諛??밴린?ы빆)'???묒꽦?섏꽭??

[?꾩닔 ?ы빆] 
- 諛섎뱶??"?ㅻ룞二쇱쓽 '?쎄쾶 ?뚯뼱吏???瑜??듯빐"濡??쒖옉?섏뿬 臾몄옣??援ъ꽦??寃?
- 諛섎뱶??臾몄옣 ?앹뿉 留덉묠??.)瑜?李띿쓣 寃?
- ?꾩껜 湲???섎뒗 怨듬갚 ?ы븿 ?쒓? 130~150???댁쇅濡??묒꽦??寃?

[?댁긽?곸씤 ?뺤떇 ?덉떆]
?ㅻ룞二쇱쓽 '?쎄쾶 ?뚯뼱吏???瑜??듯빐 ?먯븘 ?깆같怨??쒕???怨좊뇤瑜??댄빐?섎ŉ, ?먯떊??怨듦컙???깆같???μ쑝濡??쇱븘 媛移섍????뺤꽦?? 遺?꾨윭??????섏? 諛⑺뼢?쇰줈 ?섏븘媛??怨꾧린濡??쇨퀬, ?먯떊留뚯쓽 ?꾩묠??留욎씠?섍린 ?꾪빐 袁몄????몃젰?섎뒗 ?ㅼ쭚???뗫낫??

[?낅젰 ?숈깮 ?곗씠?? ${dataStr}]

[?묒꽦 洹쒖튃]
1. ?뺤쨷?섍퀬 ?꾨Ц?곸씤 援먯궗???댄닾瑜??좎??섏꽭??
2. 諛섎뱶??紐낆궗???대?(~?? ~?? ~??濡?臾몄옣???앸궪 寃?
3. ?ㅻⅨ ?ㅻ챸 ?놁씠 ?ㅼ쭅 ?명듅 蹂몃Ц ?댁슜留?異쒕젰?섏꽭??`;
}

function calculateByte(s) {
  if (!s) return 0;
  return s.split('').reduce((b, char) => b + (char.charCodeAt(0) > 128 ? 3 : 1), 0);
}

function callGemini(prompt) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.MODEL_NAME}:generateContent?key=${CONFIG.API_KEY}`;
  const payload = { 
    "contents": [{ "parts": [{ "text": prompt }] }], 
    "generationConfig": { 
      "temperature": 0.6,
      "maxOutputTokens": 1000 
    } 
  };
  
  try {
    const res = UrlFetchApp.fetch(url, { 
      "method": "post", 
      "contentType": "application/json", 
      "payload": JSON.stringify(payload), 
      "muteHttpExceptions": true 
    });
    const json = JSON.parse(res.getContentText());
    if (json.candidates && json.candidates[0].content) return json.candidates[0].content.parts[0].text;
    if (json.error) return "API?ㅻ쪟: " + json.error.message;
    return "?먮윭: ?묐떟?놁쓬";
  } catch(e) { 
    return "?먮윭: " + e.toString(); 
  }
}

/**
 * 30珥????먮룞?쇰줈 ?ㅼ쓬 ?묒뾽???섑뻾?섎룄濡??몃━嫄??덉빟
 */
function setupNextTrigger() {
  clearAllTriggers();
  ScriptApp.newTrigger('updateSeteukDirectly')
    .timeBased()
    .after(30 * 1000) 
    .create();
}

/**
 * ?붾젅洹몃옩 硫붿떆吏 ?꾩넚
 */
function sendTelegramNotification(message) {
  const url = `https://api.telegram.org/bot${CONFIG.TELEGRAM_TOKEN}/sendMessage`;
  const payload = {
    "chat_id": CONFIG.TELEGRAM_CHAT_ID,
    "text": message
  };
  
  try {
    UrlFetchApp.fetch(url, {
      "method": "post",
      "contentType": "application/json",
      "payload": JSON.stringify(payload)
    });
  } catch (e) {
    console.error("?붾젅洹몃옩 ?꾩넚 ?ㅻ쪟: " + e.toString());
  }
}

/**
 * 紐⑤뱺 ?명듅 愿???몃━嫄???젣
 */
function clearAllTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  for (let i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'updateSeteukDirectly') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
}

