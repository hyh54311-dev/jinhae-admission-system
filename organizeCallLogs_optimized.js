/**
 * 진해고등학교 황요한 선생님 업무 지원 스크립트 (최종 완성본 - v4 에러 방어 및 최저가 가성비 모델 적용)
 * 1. 모델: 음성인식 능력이 탁월하고 비용이 기존 3.1 Flash-Lite 대비 60% 이상 저렴한 최신 gemini-2.0-flash 적용
 * 2. 상세 로깅: 요약 실패 시 구체적인 HTTP 에러 코드 및 파일 크기 기록
 * 3. 에러 방어: 실패한 파일은 휴지통으로 버리지 않고 재시도 가능하도록 보존
 * 4. 버그 수정: 마지막 정렬 시 발생하는 ReferenceError 완벽 해결
 */

function getConfiguration() {
  const scriptProperties = PropertiesService.getScriptProperties();
  const apiKey = scriptProperties.getProperty('GEMINI_API_KEY');
  
  if (!apiKey) {
    throw new Error("스크립트 설정 -> 프로젝트 설정 -> 스크립트 속성에 'GEMINI_API_KEY'를 등록해야 합니다.");
  }

  return {
    API_KEY: apiKey,
    FOLDER_ID: '1R7llguArNo8N-R9A9S8Aik7nohRNILIt', 
    MODEL_NAME: 'models/gemini-3.1-flash-lite', // ✅ 백만 토큰당 $0.25로 3.5 Flash 대비 6배 이상 저렴한 초가성비 3.1 Flash-Lite 모델 적용
    CONTACT_SHEET_NAME: '연락처',
    BATCH_SIZE: 10
  };
}

const cachedSheetData = {};

function organizeCallLogs() {
  const START_TIME = Date.now();
  const MAX_EXECUTION_TIME = 3.5 * 60 * 1000;

  const lock = LockService.getScriptLock();
  if (!lock.tryLock(5000)) {
    console.log("이전 작업이 아직 실행 중입니다. 중복 요약을 방지하기 위해 이번 턴은 건너뜁니다.");
    return;
  }

  try {
    const CONFIG = getConfiguration();
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const contacts = getContactsMap_(ss, CONFIG.CONTACT_SHEET_NAME);
    
    let folder;
    try {
      folder = DriveApp.getFolderById(CONFIG.FOLDER_ID);
    } catch (e) {
      console.error("폴더를 찾을 수 없습니다.");
      return;
    }

    const files = folder.getFiles();
    const subFolders = folder.getFoldersByName('처리완료');
    const processedFolder = subFolders.hasNext() ? subFolders.next() : folder.createFolder('처리완료');

    let processedCount = 0;
    let skippedCount = 0;
    let errorCount = 0;
    const modifiedSheets = new Set(); // ✅ ReferenceError(sheet is not defined) 방지용 집합

    while (files.hasNext() && processedCount < CONFIG.BATCH_SIZE) {
      if (Date.now() - START_TIME > MAX_EXECUTION_TIME) {
        console.log("⏳ 실행 시간 제한 초과 방지를 위해 작업을 안전하게 일시 중단합니다.");
        break;
      }

      const file = files.next();
      const fileName = file.getName();
      
      const dateMatch = fileName.match(/\d{14}/);
      if (!dateMatch) continue;
      
      const dt = dateMatch[0];
      const formattedDate = `${dt.substring(0, 4)}/${dt.substring(4, 6)}/${dt.substring(6, 8)} ${dt.substring(8, 10)}:${dt.substring(10, 12)}`;

      let infoPart = fileName.replace(dt, "").replace(/\.[^/.]+$/, "").replace(/[_\-\s]+$/g, "");
      const cleanInfo = infoPart.replace(/\D/g, "");
      const phoneMatch = cleanInfo.match(/(010\d{7,8}|0[2-6]{1,2}\d{7,8})/);
      const rawPhoneNumber = phoneMatch ? phoneMatch[0] : "";
      
      let callerIdentity = "";
      if (rawPhoneNumber && contacts[rawPhoneNumber]) {
        callerIdentity = contacts[rawPhoneNumber];
      } else {
        const phoneRegexWithSep = /(010[- .]?\d{3,4}[- .]?\d{4}|0[2-6]{1,2}[- .]?\d{3,4}[- .]?\d{4})/;
        const matchWithSep = infoPart.match(phoneRegexWithSep);
        let cleanName = matchWithSep ? infoPart.split(matchWithSep[0])[0] : infoPart;
        callerIdentity = cleanName.replace(/[_\-\s]+$/g, "").trim() || rawPhoneNumber || "알 수 없음";
      }

      if (callerIdentity.includes("박지혜")) callerIdentity = "박지혜(아내) ❤️";

      const monthName = `${dt.substring(0, 4)}년 ${dt.substring(4, 6)}월`;
      const sheet = getOrCreateMonthlySheet_(ss, monthName);
      modifiedSheets.add(monthName); 
      
      const sheetData = getSheetDataFast_(sheet, monthName);
      
      if (isAlreadyProcessedFast_(sheetData, formattedDate, callerIdentity)) {
        console.log(`[중복 스킵] 이미 시트에 기록되어 있습니다. 휴지통으로 이동: ${fileName}`);
        file.setTrashed(true); 
        skippedCount++;
        continue; 
      }

      if (Date.now() - START_TIME > MAX_EXECUTION_TIME - 30000) {
        console.log("⏳ API 호출 전 시간이 촉박하여 안전하게 다음 실행으로 넘깁니다.");
        break;
      }

      console.time(`Gemini_${callerIdentity}`);
      const summary = callGeminiHwangContext_(file, callerIdentity, CONFIG);
      console.timeEnd(`Gemini_${callerIdentity}`);

      sheet.insertRowBefore(2);
      const rowRange = sheet.getRange(2, 1, 1, 3);
      rowRange.setValues([[formattedDate, callerIdentity, summary]]);
      
      sheetData.unshift({ dateKey: dt.substring(0, 12), identity: callerIdentity });
      
      rowRange.setFontSize(13).setVerticalAlignment('top');
      const summaryCell = sheet.getRange(2, 3);
      summaryCell.setWrap(true);
      
      if (callerIdentity.includes("아내")) {
        sheet.getRange(2, 2).setBackground('#FFF0F5');
      } else if (callerIdentity.includes("학교") || callerIdentity.includes("고등")) {
        sheet.getRange(2, 2).setBackground('#E6F3FF');
      }

      // ✅ 에러가 났는지 구별하여 스타일 처리 및 폴더 이동 결정
      if (summary.startsWith("요약 실패") || summary.startsWith("연결 오류")) {
        summaryCell.setBackground('#fce8e6').setFontColor('#c53929').setFontWeight('bold'); // 에러행 강조 (빨강)
        console.warn(`[에러] ${callerIdentity} - ${summary}`);
        errorCount++;
        // 실패한 파일은 '처리완료' 폴더로 이동시키지 않아 나중에 재시도 가능하게 함
      } else {
        if (summary.includes('*')) {
          summaryCell.setBackground('#FFF9C4').setFontWeight('bold');
        }
        file.moveTo(processedFolder); // 성공시에만 파일 이동
        processedCount++;
        console.log(`[처리완료] ${callerIdentity} (${formattedDate})`);
      }

      Utilities.sleep(2000); 
    }

    // ✅ 4. 모든 파일 처리 후 수정된 시트들에 대해서만 강제 정렬 실시
    if (modifiedSheets.size > 0 && (processedCount > 0 || errorCount > 0)) {
      modifiedSheets.forEach(sheetName => {
        let s = ss.getSheetByName(sheetName);
        if (s && s.getLastRow() > 1) {
          s.getRange(2, 1, s.getLastRow() - 1, 3).sort({column: 1, ascending: false});
          console.log(`[정렬완료] ${sheetName} 시트 최신순 정렬 완료`);
        }
      });
    }
    
    console.log(`[종료] 성공: ${processedCount}건, 에러: ${errorCount}건, 중복삭제: ${skippedCount}건`);

  } finally {
    lock.releaseLock();
  }
}

/**
 * 중복 행 정리 도우미 유틸
 */
function cleanupDuplicates() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;

  const data = sheet.getRange(1, 1, lastRow, 2).getValues();
  const seen = new Set();
  const rowsToDelete = [];

  for (let i = data.length - 1; i >= 1; i--) {
    let dateVal = data[i][0];
    let dateStr = (dateVal instanceof Date) 
      ? Utilities.formatDate(dateVal, Session.getScriptTimeZone(), "yyyy/MM/dd HH:mm")
      : String(dateVal).trim();
    
    let identity = String(data[i][1]).trim();
    let key = dateStr.replace(/\D/g, "") + "|" + identity;

    if (seen.has(key)) {
      rowsToDelete.push(i + 1);
    } else {
      seen.add(key);
    }
  }

  rowsToDelete.forEach(row => sheet.deleteRow(row));
  console.log(`[정리 완료] 총 ${rowsToDelete.length}개의 중복 행을 삭제했습니다.`);
  sortCurrentSheet();
}

function sortCurrentSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;

  sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).sort({column: 1, ascending: false});
  console.log(`[정렬 완료] '${sheet.getName()}' 시트가 최신순(내림차순)으로 정렬되었습니다.`);
}

function getSheetDataFast_(sheet, monthName) {
  if (!cachedSheetData[monthName]) {
    const lastRow = sheet.getLastRow();
    if (lastRow < 2) {
      cachedSheetData[monthName] = [];
    } else {
      const data = sheet.getRange(1, 1, lastRow, 2).getValues();
      cachedSheetData[monthName] = data.map(row => {
        let sheetDate = row[0];
        let dateKey = "";
        if (sheetDate instanceof Date) {
          dateKey = Utilities.formatDate(sheetDate, Session.getScriptTimeZone(), "yyyyMMddHHmm");
        } else {
          dateKey = String(sheetDate).replace(/\D/g, ""); 
        }
        return { dateKey: dateKey, identity: String(row[1]).trim() };
      });
    }
  }
  return cachedSheetData[monthName];
}

function isAlreadyProcessedFast_(sheetData, targetDateString, identity) {
  const targetDateKey = targetDateString.replace(/\D/g, ""); 
  const targetId = identity.trim();
  for (let i = 0; i < sheetData.length; i++) {
    if (sheetData[i].dateKey === targetDateKey && sheetData[i].identity === targetId) {
      return true; 
    }
  }
  return false;
}

// ✅ API 통신을 정밀하게 분석하여 에러 정보를 추출하는 구조로 완전 개편
// ✅ API 통신 및 파일 크기 방어막이 강화된 버전
function callGeminiHwangContext_(file, callerIdentity, CONFIG) {
  const fileSize = file.getSize(); // 파일 크기(바이트)
  
  // 1️⃣ [에러 방어] 14.5MB 초과 파일 사전 차단 (인코딩 시 20MB를 초과하여 API 오류 및 GAS 메모리 부족 유발 방지)
  const MAX_FILE_SIZE_LIMIT = 14.5 * 1024 * 1024; // 14.5 MB
  if (fileSize > MAX_FILE_SIZE_LIMIT) {
    const sizeInMB = (fileSize / (1024 * 1024)).toFixed(1);
    console.warn(`[크기 초과 스킵] ${callerIdentity} - 파일이 너무 큽니다. (${sizeInMB}MB)`);
    return `요약 실패: 녹음 파일 용량 초과 (${sizeInMB}MB) - 14.5MB 이하의 파일만 요약이 가능합니다.`;
  }

  const url = `https://generativelanguage.googleapis.com/v1beta/${CONFIG.MODEL_NAME}:generateContent?key=${CONFIG.API_KEY}`;
  
  // 2️⃣ [MIME 타입 정밀 처리] 드라이브 인식 오류 방지 및 호환되는 정확한 오디오 포맷 매핑
  let mimeType = file.getMimeType();
  const fileName = file.getName().toLowerCase();
  
  if (fileName.endsWith('.m4a')) {
    mimeType = 'audio/x-m4a'; // Gemini API에서 M4A 처리에 가장 안정적인 마임타입 지정
  } else if (fileName.endsWith('.mp3')) {
    mimeType = 'audio/mp3';
  } else if (fileName.endsWith('.wav')) {
    mimeType = 'audio/wav';
  } else if (mimeType === 'application/octet-stream') {
    // 마임타입이 불분명할 경우 확장자 기준으로 재강제
    mimeType = 'audio/mp3'; 
  }

  let base64Data;
  try {
    base64Data = Utilities.base64Encode(file.getBlob().getBytes());
  } catch (memError) {
    return `요약 실패: 앱스스크립트 메모리 부족 (파일 크기: ${(fileSize / (1024 * 1024)).toFixed(1)}MB)`;
  }

  const prompt = `너는 국어 선생님의 업무 비서야. 통화 상대 '${callerIdentity}'와의 내용을 이모지를 섞어 줄글로 상세 요약해줘.
                  만약 소음만 들린다면 '내용 없음'이라고 답변해.
                  요청사항이나 할 일은 마지막에 '*'로 시작하는 줄에 정리해줘.`;

  const payload = { 
    contents: [{ parts: [{ text: prompt }, { inlineData: { mimeType: mimeType, data: base64Data } }] }],
    safetySettings: [
      { category: "HARM_CATEGORY_HARASSMENT", threshold: "BLOCK_NONE" },
      { category: "HARM_CATEGORY_HATE_SPEECH", threshold: "BLOCK_NONE" },
      { category: "HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold: "BLOCK_NONE" },
      { category: "HARM_CATEGORY_DANGEROUS_CONTENT", threshold: "BLOCK_NONE" }
    ]
  };

  const options = { 
    method: "post", 
    contentType: "application/json", 
    payload: JSON.stringify(payload), 
    muteHttpExceptions: true 
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const code = response.getResponseCode();
    const resultText = response.getContentText();
    
    // 3️⃣ HTTP 응답 코드 분석 및 오류 대응
    if (code !== 200) {
      let errorMsg = `요약 실패 [HTTP ${code}]`;
      try {
        const errJson = JSON.parse(resultText);
        if (errJson.error && errJson.error.message) {
          errorMsg += `: ${errJson.error.message}`;
        }
      } catch(e) { 
        errorMsg += `: 알 수 없는 API 오류`;
      }
      return errorMsg + ` (파일크기: ${(fileSize / (1024 * 1024)).toFixed(1)}MB)`;
    }

    let result = null;
    try {
      result = JSON.parse(resultText);
    } catch(e) {
      return `요약 실패: 응답 파싱 에러`;
    }
    
    if (result && result.candidates && result.candidates.length > 0) {
      const candidate = result.candidates[0];
      if (candidate.content && candidate.content.parts && candidate.content.parts.length > 0) {
        return candidate.content.parts[0].text.trim();
      } else if (candidate.finishReason) {
        return `요약 실패: 생성 거부 (사유: ${candidate.finishReason})`;
      }
    }
    
    return `요약 실패: API 응답 본문이 비어있음 (크기: ${(fileSize / 1024).toFixed(0)} KB)`;
  } catch (e) { 
    return "연결 오류: " + e.toString() + ` (크기: ${(fileSize / 1024).toFixed(0)} KB)`; 
  }
}

function getContactsMap_(ss, sheetName) {
  let sheet = ss.getSheetByName(sheetName) || ss.insertSheet(sheetName);
  const data = sheet.getDataRange().getValues();
  const map = {};
  for (let i = 1; i < data.length; i++) {
    const phone = String(data[i][1]).replace(/\D/g, ''); 
    if (phone) map[phone] = data[i][2] ? `${data[i][0]}(${String(data[i][2]).trim()})` : String(data[i][0]).trim();
  }
  return map;
}

function getOrCreateMonthlySheet_(ss, name) {
  let sheet = ss.getSheetByName(name) || ss.insertSheet(name);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(['통화 일시', '통화 대상', '상세 요약 내용']);
    sheet.getRange('A1:C1').setBackground('#1A237E').setFontColor('white').setFontWeight('bold').setFontSize(14).setHorizontalAlignment('center');
    sheet.setFrozenRows(1);
    sheet.setColumnWidth(1, 160);
    sheet.setColumnWidth(2, 200);
    sheet.setColumnWidth(3, 850);
  }
  return sheet;
}
