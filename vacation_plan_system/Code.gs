/**
 * 방학 계획서 입력 시스템 (Vacation Plan Entry System)
 * Backend Google Apps Script (Code.gs)
 * 
 * - doGet(e): Serves Index.html as an HTML template with viewport meta tag and title.
 * - initSheets(): Checks and initializes sheet structures and header rows.
 * - loadExistingContent(name, password): Loads user submissions if credentials match.
 * - processForm(formData): Saves/overwrites user submissions with transactional locks.
 */

/**
 * Serves the web app UI (Index.html).
 */
function doGet(e) {
  try {
    var template = HtmlService.createTemplateFromFile('Index');
    return template.evaluate()
      .setTitle('방학 계획서 입력 시스템')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1.0');
  } catch (error) {
    return HtmlService.createHtmlOutput("<h3>시스템 초기화 오류</h3><p>" + error.toString() + "</p>");
  }
}

/**
 * Initializes Spreadsheet structures if sheets do not exist.
 * Sheets created: '출장 및 연수 계획', '공무외 국외여행 계획'
 * Header row: [제출일시, 성명, 비밀번호, 기간, 장소, 내용]
 */
function initSheets() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!ss) {
    throw new Error("Active spreadsheet not found. Please bind this script to a Google Spreadsheet.");
  }
  
  var sheetNames = ['출장 및 연수 계획', '공무외 국외여행 계획'];
  var headers = ['제출일시', '성명', '비밀번호', '기간', '장소', '내용'];
  
  sheetNames.forEach(function(name) {
    var sheet = ss.getSheetByName(name);
    if (!sheet) {
      sheet = ss.insertSheet(name);
      sheet.appendRow(headers);
      
      // Basic formatting for headers
      sheet.getRange(1, 1, 1, headers.length)
        .setFontWeight('bold')
        .setBackground('#f2f2f2')
        .setHorizontalAlignment('center')
        .setBorder(true, true, true, true, true, true);
      
      sheet.setFrozenRows(1);
    }
  });
}

/**
 * Loads existing submissions for the given Name after validating Password.
 * 
 * @param {string} name - User name (성명)
 * @param {string} password - User password (비밀번호)
 * @returns {object} Response object indicating success and containing arrays of plans
 */
function loadExistingContent(name, password) {
  try {
    initSheets(); // Ensure sheets are initialized
    
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var trainingSheet = ss.getSheetByName('출장 및 연수 계획');
    var travelSheet = ss.getSheetByName('공무외 국외여행 계획');
    
    var trainingData = trainingSheet.getDataRange().getValues();
    var travelData = travelSheet.getDataRange().getValues();
    
    var trainingRows = [];
    var travelRows = [];
    var storedPassword = null;
    var userExists = false;
    
    // Normalize input name and password
    var cleanName = name ? String(name).trim() : "";
    var cleanPassword = password ? String(password).trim() : "";
    
    if (!cleanName) {
      return { success: false, message: "⚠️ 성명을 입력해 주세요." };
    }
    
    // Scan '출장 및 연수 계획' (Training) starting from row 2 (index 1)
    for (var i = 1; i < trainingData.length; i++) {
      var row = trainingData[i];
      if (row[1] && String(row[1]).trim() === cleanName) {
        userExists = true;
        if (!storedPassword && row[2]) {
          storedPassword = String(row[2]).trim();
        }
        trainingRows.push({
          dateStr: row[3] ? String(row[3]) : "",
          location: row[4] ? String(row[4]) : "",
          title: row[5] ? String(row[5]) : ""
        });
      }
    }
    
    // Scan '공무외 국외여행 계획' (Travel) starting from row 2 (index 1)
    for (var j = 1; j < travelData.length; j++) {
      var row = travelData[j];
      if (row[1] && String(row[1]).trim() === cleanName) {
        userExists = true;
        if (!storedPassword && row[2]) {
          storedPassword = String(row[2]).trim();
        }
        travelRows.push({
          dateStr: row[3] ? String(row[3]) : "",
          location: row[4] ? String(row[4]) : "",
          title: row[5] ? String(row[5]) : ""
        });
      }
    }
    
    // If user has no existing entries in both sheets
    if (!userExists) {
      return {
        success: true,
        training: [],
        travel: []
      };
    }
    
    // Verify password
    if (cleanPassword !== storedPassword) {
      return {
        success: false,
        message: "⚠️ 성명에 해당하는 비밀번호가 올바르지 않습니다. 기존 데이터 보안을 위해 조회가 제한됩니다."
      };
    }
    
    return {
      success: true,
      training: trainingRows,
      travel: travelRows
    };
    
  } catch (error) {
    return {
      success: false,
      message: "⚠️ 조회를 진행하는 중 오류가 발생했습니다: " + error.toString()
    };
  }
}

/**
 * Overwrite-saves the user's plan entries.
 * Deletes existing entries for this user and appends new entries within a script lock transaction.
 * 
 * @param {object} formData - Form submission data containing name, password, training, and travel plans
 * @returns {string} Success message or errors
 */
function processForm(formData) {
  var lock = LockService.getScriptLock();
  
  try {
    // Acquire lock with 30 seconds timeout to prevent concurrency race conditions
    var lockAcquired = lock.tryLock(30000);
    if (!lockAcquired) {
      throw new Error("⚠️ 다른 사용자가 데이터를 입력 또는 수정 중입니다. 잠시 후 다시 시도해 주세요.");
    }
    
    // 1. Initialize and get sheets
    initSheets();
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var trainingSheet = ss.getSheetByName('출장 및 연수 계획');
    var travelSheet = ss.getSheetByName('공무외 국외여행 계획');
    
    // 2. Normalize and validate inputs
    var name = formData.name ? String(formData.name).trim() : "";
    var password = formData.password ? String(formData.password).trim() : "";
    
    if (!name) {
      throw new Error("⚠️ 성명이 입력되지 않았습니다.");
    }
    if (!password) {
      throw new Error("⚠️ 비밀번호가 입력되지 않았습니다.");
    }
    
    var trainingData = trainingSheet.getDataRange().getValues();
    var travelData = travelSheet.getDataRange().getValues();
    var storedPassword = null;
    var userExists = false;
    
    // Check if there is an existing password for this user
    for (var i = 1; i < trainingData.length; i++) {
      if (trainingData[i][1] && String(trainingData[i][1]).trim() === name) {
        userExists = true;
        if (!storedPassword && trainingData[i][2]) {
          storedPassword = String(trainingData[i][2]).trim();
        }
      }
    }
    for (var j = 1; j < travelData.length; j++) {
      if (travelData[j][1] && String(travelData[j][1]).trim() === name) {
        userExists = true;
        if (!storedPassword && travelData[j][2]) {
          storedPassword = String(travelData[j][2]).trim();
        }
      }
    }
    
    // If the user already has records, the password must match the stored password
    if (userExists && storedPassword && password !== storedPassword) {
      throw new Error("⚠️ 성명에 해당하는 비밀번호가 올바르지 않습니다. 기존 데이터 보안을 위해 저장이 제한됩니다.");
    }
    
    // 3. Delete existing records for this user (bottom-to-top traversal to prevent index shifting)
    // For training sheet:
    for (var i = trainingData.length - 1; i >= 1; i--) {
      if (trainingData[i][1] && String(trainingData[i][1]).trim() === name) {
        trainingSheet.deleteRow(i + 1);
      }
    }
    
    // For travel sheet:
    for (var j = travelData.length - 1; j >= 1; j--) {
      if (travelData[j][1] && String(travelData[j][1]).trim() === name) {
        travelSheet.deleteRow(j + 1);
      }
    }
    
    var timestamp = new Date();
    
    // 4. Append new '출장 및 연수 계획' (Training)
    if (formData.training && Array.isArray(formData.training)) {
      formData.training.forEach(function(item) {
        var dateStr = item.dateStr ? String(item.dateStr).trim() : "";
        var location = item.location ? String(item.location).trim() : "";
        var title = item.title ? String(item.title).trim() : "";
        
        // Only write row if at least one field has content to prevent empty row clutter
        if (dateStr || location || title) {
          trainingSheet.appendRow([
            timestamp,
            name,
            password,
            dateStr,
            location,
            title
          ]);
        }
      });
    }
    
    // 5. Append new '공무외 국외여행 계획' (Travel)
    if (formData.travel && Array.isArray(formData.travel)) {
      formData.travel.forEach(function(item) {
        var dateStr = item.dateStr ? String(item.dateStr).trim() : "";
        var location = item.location ? String(item.location).trim() : "";
        var title = item.title ? String(item.title).trim() : "";
        
        // Only write row if at least one field has content
        if (dateStr || location || title) {
          travelSheet.appendRow([
            timestamp,
            name,
            password,
            dateStr,
            location,
            title
          ]);
        }
      });
    }
    
    return "성공적으로 계획서가 저장/수정 완료되었습니다.";
    
  } catch (error) {
    // Propagate custom errors or standard errors nicely
    throw new Error(error.message || error.toString());
  } finally {
    // Release the script lock to prevent deadlock under all circumstances
    lock.releaseLock();
  }
}
