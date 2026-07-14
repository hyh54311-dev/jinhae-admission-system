const assert = require('assert');
const { 
  refreshAttendanceSystem, 
  getKoreanDateStr, 
  cleanUpUnusedColumnsInSheet, 
  addTodayColumn, 
  applyDropdownRetroactively 
} = require('./attendance_system');

// --- Utilities Mocking ---
global.Utilities = {
  formatDate: function(date, tz, format) {
    // GMT+9(KST) Timezone Mock
    const utc = date.getTime() + (date.getTimezoneOffset() * 60000);
    const kst = new Date(utc + (3600000 * 9));
    
    if (format === "MM/dd") {
      const mm = String(kst.getMonth() + 1).padStart(2, '0');
      const dd = String(kst.getDate()).padStart(2, '0');
      return `${mm}/${dd}`;
    } else if (format === "u") {
      const day = kst.getDay();
      return day === 0 ? "7" : String(day);
    }
    return "";
  }
};

// --- Data Validation Rule Mocking ---
class DataValidationMock {
  constructor(options, allowInvalid) {
    this.options = options;
    this.allowInvalid = allowInvalid;
  }
}

class DataValidationBuilderMock {
  constructor() {
    this.options = [];
    this.allowInvalid = true;
  }
  requireValueInList(options) {
    this.options = options;
    return this;
  }
  setAllowInvalid(allow) {
    this.allowInvalid = allow;
    return this;
  }
  build() {
    return new DataValidationMock(this.options, this.allowInvalid);
  }
}

// --- SpreadsheetApp Mocking ---
global.SpreadsheetApp = {
  getActiveSpreadsheet: function() {
    return activeSpreadsheetInstance;
  },
  newDataValidation: function() {
    return new DataValidationBuilderMock();
  },
  flush: function() {
    // console.log("   [SpreadsheetApp.flush] 구글 시트 새로고침 실행 완료");
  }
};

let activeSpreadsheetInstance = null;

// --- Range Mocking ---
class RangeMock {
  constructor(sheet, row, col, numRows, numCols) {
    this.sheet = sheet;
    this.startRow = row;
    this.startCol = col;
    this.numRows = numRows || 1;
    this.numCols = numCols || 1;
  }

  getValue() {
    // 단일 셀 값 반환
    return this.sheet._getCell(this.startRow, this.startCol);
  }

  getValues() {
    // 2차원 배열 반환
    const values = [];
    for (let r = 0; r < this.numRows; r++) {
      const rowArr = [];
      for (let c = 0; c < this.numCols; c++) {
        rowArr.push(this.sheet._getCell(this.startRow + r, this.startCol + c));
      }
      values.push(rowArr);
    }
    return values;
  }

  getDisplayValue() {
    const val = this.getValue();
    return val === null || val === undefined ? "" : String(val);
  }

  getDisplayValues() {
    const values = [];
    for (let r = 0; r < this.numRows; r++) {
      const rowArr = [];
      for (let c = 0; c < this.numCols; c++) {
        const val = this.sheet._getCell(this.startRow + r, this.startCol + c);
        rowArr.push(val === null || val === undefined ? "" : String(val));
      }
      values.push(rowArr);
    }
    return values;
  }

  setValue(value) {
    for (let r = 0; r < this.numRows; r++) {
      for (let c = 0; c < this.numCols; c++) {
        this.sheet._setCell(this.startRow + r, this.startCol + c, value);
      }
    }
    return this;
  }

  setValues(values) {
    for (let r = 0; r < this.numRows; r++) {
      for (let c = 0; c < this.numCols; c++) {
        this.sheet._setCell(this.startRow + r, this.startCol + c, values[r][c]);
      }
    }
    return this;
  }

  insertCheckboxes() {
    // 체크박스 생성: 기본값 false로 설정
    this.setValue(false);
    return this;
  }

  setBackground(color) {
    this.sheet._setMetadata(this.startRow, this.startCol, 'background', color);
    return this;
  }

  setFontWeight(weight) {
    this.sheet._setMetadata(this.startRow, this.startCol, 'fontWeight', weight);
    return this;
  }

  setHorizontalAlignment(align) {
    for (let r = 0; r < this.numRows; r++) {
      for (let c = 0; c < this.numCols; c++) {
        this.sheet._setMetadata(this.startRow + r, this.startCol + c, 'horizontalAlignment', align);
      }
    }
    return this;
  }

  setDataValidation(rule) {
    for (let r = 0; r < this.numRows; r++) {
      for (let c = 0; c < this.numCols; c++) {
        this.sheet._setMetadata(this.startRow + r, this.startCol + c, 'dataValidation', rule);
      }
    }
    return this;
  }
}

// --- Sheet Mocking ---
class SheetMock {
  constructor(name, maxRows = 100, maxCols = 50) {
    this.name = name;
    this.maxRows = maxRows;
    this.maxCols = maxCols;
    this.data = {}; // key: "row,col"
    this.metadata = {}; // key: "row,col" -> { background, fontWeight, ... }
  }

  getName() {
    return this.name;
  }

  getMaxColumns() {
    return this.maxCols;
  }

  getLastColumn() {
    let lastCol = 0;
    for (let key in this.data) {
      const [r, c] = key.split(',').map(Number);
      if (c > lastCol && this.data[key] !== "") {
        lastCol = c;
      }
    }
    return lastCol;
  }

  getLastRow() {
    let lastRow = 0;
    for (let key in this.data) {
      const [r, c] = key.split(',').map(Number);
      if (r > lastRow && this.data[key] !== "") {
        lastRow = r;
      }
    }
    return lastRow;
  }

  insertColumnAfter(col) {
    this.maxCols++;
    // col 이후의 데이터 오른쪽으로 시프트
    const newData = {};
    for (let key in this.data) {
      const [r, c] = key.split(',').map(Number);
      if (c > col) {
        newData[`${r},${c + 1}`] = this.data[key];
      } else {
        newData[`${r},${c}`] = this.data[key];
      }
    }
    this.data = newData;

    const newMetadata = {};
    for (let key in this.metadata) {
      const [r, c] = key.split(',').map(Number);
      if (c > col) {
        newMetadata[`${r},${c + 1}`] = this.metadata[key];
      } else {
        newMetadata[`${r},${c}`] = this.metadata[key];
      }
    }
    this.metadata = newMetadata;
  }

  deleteColumn(col) {
    // col 삭제 후 왼쪽으로 시프트
    const newData = {};
    for (let key in this.data) {
      const [r, c] = key.split(',').map(Number);
      if (c === col) {
        // 삭제
      } else if (c > col) {
        newData[`${r},${c - 1}`] = this.data[key];
      } else {
        newData[`${r},${c}`] = this.data[key];
      }
    }
    this.data = newData;

    const newMetadata = {};
    for (let key in this.metadata) {
      const [r, c] = key.split(',').map(Number);
      if (c === col) {
        // 삭제
      } else if (c > col) {
        newMetadata[`${r},${c - 1}`] = this.metadata[key];
      } else {
        newMetadata[`${r},${c}`] = this.metadata[key];
      }
    }
    this.metadata = newMetadata;
  }

  setColumnWidth(col, width) {
    // console.log(`   [SheetMock] Set column ${col} width to ${width}`);
  }

  getRange(row, col, numRows, numCols) {
    return new RangeMock(this, row, col, numRows, numCols);
  }

  // --- Mock Helpers ---
  _getCell(row, col) {
    const key = `${row},${col}`;
    return this.data[key] !== undefined ? this.data[key] : "";
  }

  _setCell(row, col, val) {
    const key = `${row},${col}`;
    this.data[key] = val;
  }

  _setMetadata(row, col, metaKey, val) {
    const key = `${row},${col}`;
    if (!this.metadata[key]) this.metadata[key] = {};
    this.metadata[key][metaKey] = val;
  }

  _getMetadata(row, col, metaKey) {
    const key = `${row},${col}`;
    return this.metadata[key] ? this.metadata[key][metaKey] : null;
  }
}

// --- Spreadsheet Mocking ---
class SpreadsheetMock {
  constructor() {
    this.sheets = [];
  }
  addSheet(sheet) {
    this.sheets.push(sheet);
  }
  getSheets() {
    return this.sheets;
  }
}

// ==========================================
// TEST SCENARIOS
// ==========================================

console.log("==========================================");
console.log("🚀 구글 앱스 스크립트 출결 자동화 시스템 테스트 하네스 기동");
console.log("==========================================\n");

function runTests() {
  // 테스트용 KST 오늘 날짜 문자열 획득
  const todayStr = getKoreanDateStr();
  console.log(`📌 KST 기준 오늘 날짜 문자열: ${todayStr}\n`);

  // --- 시나리오 1: 표준 데이터 세트 및 신규 생성 검증 ---
  console.log("🧪 [테스트 시나리오 1] 기본 출결 갱신 및 과거 체크해제 열 정리");
  
  const ss = new SpreadsheetMock();
  const sheet3_1 = new SheetMock("3학년1반");
  ss.addSheet(sheet3_1);
  activeSpreadsheetInstance = ss;

  // 학생 이름 설정 (B열: 학번 A열, 이름 B열)
  // 3행부터 학생 데이터 시작
  const students = [
    { id: "30101", name: "강하늘" },
    { id: "30102", name: "김태리(자퇴)" }, // 이름에 자퇴 키워드 포함
    { id: "30103", name: "박보검" },
    { id: "30104", name: "아이유(위탁교육)" }, // 이름에 위탁교육 키워드 포함
    { id: "30105", name: "임윤아" }
  ];

  students.forEach((s, idx) => {
    const row = 3 + idx;
    sheet3_1._setCell(row, 1, s.id);
    sheet3_1._setCell(row, 2, s.name);
  });

  // 열 설정
  // 1열: A열(학번), 2열: B열(이름)
  // 3열: C열 - 어제 날짜 (05/19(화)), 체크박스 True (보존되어야 함)
  sheet3_1._setCell(1, 3, true); // 체크박스 True
  sheet3_1._setCell(2, 3, "05/19(화)"); // 어제 날짜
  students.forEach((s, idx) => {
    sheet3_1._setCell(3 + idx, 3, "출석"); // 기존 출결 데이터
  });

  // 4열: D열 - 그저께 날짜 (05/18(월)), 체크박스 False (삭제되어야 함)
  sheet3_1._setCell(1, 4, false); // 체크박스 False
  sheet3_1._setCell(2, 4, "05/18(월)"); // 그저께 날짜
  students.forEach((s, idx) => {
    sheet3_1._setCell(3 + idx, 4, "출석");
  });

  console.log("   -> 스크립트 실행 전 시트 상태:");
  console.log(`      * 총 열 수: ${sheet3_1.getLastColumn()}`);
  console.log(`      * 3열 날짜: ${sheet3_1._getCell(2, 3)} (체크: ${sheet3_1._getCell(1, 3)})`);
  console.log(`      * 4열 날짜: ${sheet3_1._getCell(2, 4)} (체크: ${sheet3_1._getCell(1, 4)})`);

  // 앱스스크립트 핵심 함수 작동
  refreshAttendanceSystem();

  console.log("   -> 스크립트 실행 후 시트 상태:");
  console.log(`      * 총 열 수: ${sheet3_1.getLastColumn()}`);
  
  // 검증:
  // 1. D열(체크 안 된 어제 이전 날짜)은 삭제되고, C열(체크박스 True)은 보존됨.
  // 2. 그리고 오늘 날짜 열이 새로 추가되어야 함.
  // C열(05/19)은 그대로 보존되어 있고, 새로 생성된 열은 4열(D열)이 되어야 함.
  const col3Date = sheet3_1._getCell(2, 3);
  const col4Date = sheet3_1._getCell(2, 4);
  const col3Check = sheet3_1._getCell(1, 3);
  const col4Check = sheet3_1._getCell(1, 4);

  console.log(`      * 3열 날짜 (실제): ${col3Date} (기대: 05/19(화))`);
  console.log(`      * 3열 체크 (실제): ${col3Check} (기대: true)`);
  console.log(`      * 4열 날짜 (실제): ${col4Date} (기대: ${todayStr})`);
  console.log(`      * 4열 체크 (실제): ${col4Check} (기대: false - 빈 체크박스)`);

  assert.strictEqual(col3Date, "05/19(화)", "C열은 체크 표시가 설정되어 있으므로 삭제되지 않고 보관되어야 합니다.");
  assert.strictEqual(col3Check, true, "C열의 체크박스는 true 상태를 유지해야 합니다.");
  assert.strictEqual(col4Date, todayStr, "D열에 오늘 날짜 열이 새로 개설되어야 합니다.");
  assert.strictEqual(col4Check, false, "새로 생성된 오늘 열의 1행 체크박스는 false 상태여야 합니다.");

  // 학생별 자동 출결 기본값 검증
  // B열 3행: 강하늘 -> 일반학생 ("출석")
  // B열 4행: 김태리(자퇴) -> 자퇴생 ("자퇴")
  // B열 5행: 박보검 -> 일반학생 ("출석")
  // B열 6행: 아이유(위탁교육) -> 위탁생 ("위탁교육")
  // B열 7행: 임윤아 -> 일반학생 ("출석")
  // 34행 이상 빈 영역: ""
  const att1 = sheet3_1._getCell(3, 4); // 강하늘
  const att2 = sheet3_1._getCell(4, 4); // 김태리(자퇴)
  const att3 = sheet3_1._getCell(5, 4); // 박보검
  const att4 = sheet3_1._getCell(6, 4); // 아이유(위탁교육)
  const att5 = sheet3_1._getCell(7, 4); // 임윤아
  const attEmpty = sheet3_1._getCell(32, 4); // 빈 학생 줄 (B열 빈줄)

  console.log(`      * 강하늘 출결: ${att1} (기대: 출석)`);
  console.log(`      * 김태리(자퇴) 출결: ${att2} (기대: 자퇴)`);
  console.log(`      * 박보검 출결: ${att3} (기대: 출석)`);
  console.log(`      * 아이유(위탁교육) 출결: ${att4} (기대: 위탁교육)`);
  console.log(`      * 임윤아 출결: ${att5} (기대: 출석)`);
  console.log(`      * 빈 영역(32행) 출결: '${attEmpty}' (기대: '')`);

  assert.strictEqual(att1, "출석", "일반 학생의 기본 출결값은 '출석'이어야 합니다.");
  assert.strictEqual(att2, "자퇴", "이름에 '자퇴' 키워드가 매칭되면 자동으로 '자퇴' 기본값이 세팅되어야 합니다.");
  assert.strictEqual(att3, "출석", "일반 학생의 기본 출결값은 '출석'이어야 합니다.");
  assert.strictEqual(att4, "위탁교육", "이름에 '위탁교육' 키워드가 매칭되면 자동으로 '위탁교육' 기본값이 세팅되어야 합니다.");
  assert.strictEqual(att5, "출석", "일반 학생의 기본 출결값은 '출석'이어야 합니다.");
  assert.strictEqual(attEmpty, "", "학생 명부가 비어있는 행(32행)의 출결칸은 완전히 빈 상태여야 합니다.");

  // 드롭다운 검증
  // applyDropdownRetroactively에서 12종 리스트 데이터 유효성 검사 생성 후 cell metadata에 저장됨
  const validationRule = sheet3_1._getMetadata(3, 4, 'dataValidation');
  assert.ok(validationRule, "오늘 날짜 출결 범위에 데이터 유효성 검사 룰이 적용되어야 합니다.");
  assert.strictEqual(validationRule.options.length, 12, "드롭다운 옵션의 개수는 총 12종이어야 합니다.");
  assert.ok(validationRule.options.includes("자퇴"), "드롭다운 옵션에 '자퇴'가 포함되어야 합니다.");
  assert.ok(validationRule.options.includes("위탁교육"), "드롭다운 옵션에 '위탁교육'이 포함되어야 합니다.");
  console.log("   ✅ 시나리오 1 통과: 과거 삭제, 오늘 열 개설, 스마트 기본값, 드롭다운 12종 완벽 검증 완료!");

  // --- 시나리오 2: 중복 방지 검증 ---
  console.log("\n🧪 [테스트 시나리오 2] 오늘 날짜 열이 이미 존재하는 경우 (중복 생성 방지)");
  
  // 이미 오늘 날짜 열이 존재하는 상태에서 시스템을 다시 돌렸을 때 중복 생성되지 않아야 함
  const preColCount = sheet3_1.getLastColumn();
  refreshAttendanceSystem();
  const postColCount = sheet3_1.getLastColumn();

  console.log(`      * 실행 전 열 수: ${preColCount}`);
  console.log(`      * 실행 후 열 수: ${postColCount} (기대: 동일)`);
  assert.strictEqual(preColCount, postColCount, "오늘 날짜가 이미 시트에 있으면 새로운 열이 절대 중복 생성되어서는 안 됩니다.");
  console.log("   ✅ 시나리오 2 통과: 중복 생성 차단 확인 완료!");

  // --- 시나리오 3: 경계값 및 대형/소형 범위 방어선 검증 ---
  console.log("\n🧪 [테스트 시나리오 3] 경계 조건 (시트가 매우 작거나 행 수가 극단적인 경우)");
  
  const sheetEmpty = new SheetMock("3학년2반", 10, 2); // 10행 2열의 극단적으로 작은 시트
  ss.addSheet(sheetEmpty);
  
  // 이름 영역도 다 빈칸으로 둠 (학생 없음)
  // Apps Script의 lastRow는 데이터가 입력된 마지막 줄을 리턴하므로,
  // 아무것도 입력하지 않으면 0을 반환.
  // 이 경우 addTodayColumn에서 `let lastRow = sheet.getLastRow();`가 0을 반환할 것임.
  // 방어선 작동 여부 체크: `if (lastRow < 32) lastRow = 34;`에 의해 lastRow는 34로 강제 조정됨.
  
  console.log(`      * 실행 전 빈 시트의 최대 열 수: ${sheetEmpty.getMaxColumns()}`);
  console.log(`      * 실행 전 빈 시트의 마지막 행 수: ${sheetEmpty.getLastRow()}`);

  refreshAttendanceSystem();

  console.log(`      * 실행 후 빈 시트의 최대 열 수: ${sheetEmpty.getMaxColumns()}`);
  console.log(`      * 실행 후 빈 시트의 마지막 열 수: ${sheetEmpty.getLastColumn()}`);
  console.log(`      * 실행 후 빈 시트의 마지막 행 수: ${sheetEmpty.getLastRow()}`);
  
  // 검증:
  // 1. 학생이 하나도 없더라도 `lastRow`가 34로 강제 조정되어 에러 없이 돌았는지.
  // 2. 최대 열(2열)을 초과하는 3번째 열을 만들 때 insertColumnAfter가 호출되어 최대 열 수가 늘어났는지.
  assert.ok(sheetEmpty.getMaxColumns() >= 3, "열 개수가 한계를 초과하면 자동으로 insertColumnAfter를 통해 시트 크기가 확장되어야 합니다.");
  assert.strictEqual(sheetEmpty._getCell(2, 3), todayStr, "안전하게 확장된 열에 오늘 날짜가 성공적으로 들어가야 합니다.");
  console.log("   ✅ 시나리오 3 통과: 극단적 무(無) 데이터 조건 및 자동 컬럼 확장 완벽 검증 완료!");

  console.log("\n==========================================");
  console.log("🎉 모든 하네스 테스트 케이스가 완벽하게 통과했습니다! 100% 정상 작동!");
  console.log("==========================================");
}

try {
  runTests();
} catch (err) {
  console.error("\n❌ [테스트 실패] 하네스 검증 중 에러 발생:");
  console.error(err);
  process.exit(1);
}
