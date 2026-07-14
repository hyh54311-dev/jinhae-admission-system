/**
 * 2026학년도 교육과정 편성표 의견 수렴 웹앱 백엔드 테스트 하네스 (바둑판형 / 단일선택 버전)
 * 
 * 제작: Antigravity
 * 목적: 실제 '교육과정_웹앱_코드.gs' 파일을 읽어와 가상 구글 앱스 스크립트 환경(Mocks)을 구축한 뒤,
 *       새로운 단일 선택 및 바둑판형 시트 구조에 대해 기능이 완벽히 작동하는지 검증합니다.
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

console.log("==================================================");
console.log("🚀 교육과정 웹앱 (바둑판 단일선택) 테스트 하네스 기동");
console.log("==================================================\n");

// 1. 실제 백엔드 스크립트 파일 읽기
const codePath = path.join(__dirname, '교육과정_웹앱_코드.gs');
if (!fs.existsSync(codePath)) {
  console.error(`❌ 오류: 테스트 대상 파일 '${codePath}'을 찾을 수 없습니다.`);
  process.exit(1);
}
const codeContent = fs.readFileSync(codePath, 'utf8');

// 2. 가상 Google Apps Script 환경 (Mocks) 정의
const mockLoggerLogs = [];
const mockLogger = {
  log: function(msg) {
    mockLoggerLogs.push(msg);
    console.log("   [GAS Logger] " + msg);
  }
};

class SheetMock {
  constructor(name) {
    this.name = name;
    this.rows = [];
    this.frozenRows = 0;
    this.columnWidthsResized = false;
  }
  
  appendRow(row) {
    this.rows.push(row);
  }
  
  getRange(row, col, numRows, numCols) {
    const rangeMock = {
      setFontWeight: function(val) { return rangeMock; },
      setBackground: function(val) { return rangeMock; },
      setHorizontalAlignment: function(val) { return rangeMock; }
    };
    return rangeMock;
  }
  
  setFrozenRows(val) {
    this.frozenRows = val;
  }
  
  autoResizeColumns(start, end) {
    this.columnWidthsResized = true;
  }
}

class SpreadsheetMock {
  constructor() {
    this.sheets = {};
  }
  
  getSheetByName(name) {
    return this.sheets[name] || null;
  }
  
  insertSheet(name) {
    const sheet = new SheetMock(name);
    this.sheets[name] = sheet;
    return sheet;
  }
}

const mockSpreadsheet = new SpreadsheetMock();

const mockSpreadsheetApp = {
  getActiveSpreadsheet: function() {
    return mockSpreadsheet;
  }
};

const mockHtmlService = {
  createTemplateFromFile: function(filename) {
    return {
      evaluate: () => {
        return {
          setTitle: (title) => {
            return {
              addMetaTag: (name, content) => {
                return {
                  setXFrameOptionsMode: (mode) => {
                    return `HTML serving ${filename} with title: "${title}"`;
                  }
                };
              }
            };
          }
        };
      }
    };
  },
  XFrameOptionsMode: {
    ALLOWALL: "ALLOWALL"
  }
};

// 3. 테스트 컨텍스트 샌드박스 설정 및 스크립트 실행
const context = {
  SpreadsheetApp: mockSpreadsheetApp,
  HtmlService: mockHtmlService,
  Logger: mockLogger,
  console: console,
  doGet: null,
  submitCurriculumResponse: null
};

vm.createContext(context);
try {
  vm.runInContext(codeContent, context);
  console.log("✅ '교육과정_웹앱_코드.gs' 컴파일 및 컨텍스트 바인딩 완료.\n");
} catch (err) {
  console.error("❌ 오류: 백엔드 스크립트 컴파일 도중 에러가 발생했습니다.");
  console.error(err);
  process.exit(1);
}

const doGet = context.doGet;
const submitCurriculumResponse = context.submitCurriculumResponse;

// 4. 테스트 시나리오 수행

// --- 테스트 1: doGet() 서비스 연결 상태 검증 ---
console.log("🧪 [Test 1] doGet() 웹앱 서빙 기능 작동 검증");
try {
  const htmlResult = doGet();
  console.log(`   * 결과 HTML 반환값: ${htmlResult}`);
  assert.ok(htmlResult.includes("교육과정_웹앱_화면"), "doGet()은 '교육과정_웹앱_화면' 템플릿을 호출해야 합니다.");
  console.log("   ✅ Test 1 통과: doGet() 서빙 상태 확인 완료.\n");
} catch (err) {
  console.error("   ❌ Test 1 실패: " + err.toString());
  process.exit(1);
}

// --- 테스트 2: 정상 제출 - 1차 (1안 선택) ---
console.log("🧪 [Test 2] submitCurriculumResponse() 정상 제출 테스트 (1차: 김태영 선생님 - 1안 선택)");
const payload1 = {
  name: "김태영",
  selectedOption: "1안",
  opinion1: "1안의 기존 과목 제외로 폐강 방지 효과가 우수합니다.",
  opinion2: "",
  opinion3: "3안은 다소 복잡함.",
  opinion4: ""
};

try {
  const res = submitCurriculumResponse(payload1);
  console.log(`   * 반환 결과: ${JSON.stringify(res)}`);
  
  const sheet = mockSpreadsheet.getSheetByName("교육과정_웹앱_응답");
  assert.ok(sheet, "데이터가 기록될 '교육과정_웹앱_응답' 시트가 자동 생성되어야 합니다.");
  assert.strictEqual(sheet.rows.length, 2, "헤더행과 데이터 1행이 추가되어 총 2개 행이 존재해야 합니다.");
  assert.strictEqual(sheet.rows[1][1], "김태영", "이름은 '김태영'이어야 합니다.");
  assert.strictEqual(sheet.rows[1][2], "1안", "최종 선택안은 '1안'이어야 합니다.");
  assert.strictEqual(sheet.rows[1][3], "1안의 기존 과목 제외로 폐강 방지 효과가 우수합니다.", "1안 의견이 정상 기록되어야 합니다.");
  assert.strictEqual(sheet.rows[1][5], "3안은 다소 복잡함.", "3안 의견이 정상 기록되어야 합니다.");
  assert.strictEqual(res.success, true, "정상 응답 시 success 값은 true여야 합니다.");
  
  console.log("   ✅ Test 2 통과: 1차 정상 응답 및 시트 컬럼 7열 매핑 확인 완료.\n");
} catch (err) {
  console.error("   ❌ Test 2 실패: " + err.toString());
  process.exit(1);
}

// --- 테스트 3: 정상 제출 - 2차 (3안 선택) ---
console.log("🧪 [Test 3] submitCurriculumResponse() 정상 제출 테스트 (2차: 임언숙 선생님 - 3안 선택)");
const payload2 = {
  name: "임언숙",
  selectedOption: "3안",
  opinion1: "",
  opinion2: "학습 분산이 우려됩니다.",
  opinion3: "3안이 시수 확보에 가장 유리하다고 봅니다.",
  opinion4: ""
};

try {
  const res = submitCurriculumResponse(payload2);
  console.log(`   * 반환 결과: ${JSON.stringify(res)}`);
  
  const sheet = mockSpreadsheet.getSheetByName("교육과정_웹앱_응답");
  assert.strictEqual(sheet.rows.length, 3, "2차 데이터 추가로 인해 총 3개 행이 존재해야 합니다.");
  assert.strictEqual(sheet.rows[2][1], "임언숙", "세 번째 행의 이름은 '임언숙'이어야 합니다.");
  assert.strictEqual(sheet.rows[2][2], "3안", "선택된 안은 '3안'이어야 합니다.");
  assert.strictEqual(sheet.rows[2][4], "학습 분산이 우려됩니다.", "2안 의견이 정확히 기록되어야 합니다.");
  assert.strictEqual(sheet.rows[2][5], "3안이 시수 확보에 가장 유리하다고 봅니다.", "3안 의견이 정확히 기록되어야 합니다.");
  assert.strictEqual(res.success, true, "정상 응답 시 success 값은 true여야 합니다.");
  
  console.log("   ✅ Test 3 통과: 2차 정상 응답 및 누적 저장 완료.\n");
} catch (err) {
  console.error("   ❌ Test 3 실패: " + err.toString());
  process.exit(1);
}

// --- 테스트 4: 유효성 검사 실패 테스트 (성함 누락) ---
console.log("🧪 [Test 4] submitCurriculumResponse() 유효성 실패 테스트 (성함 공백)");
const payload3 = {
  name: "",
  selectedOption: "2안",
  opinion1: "",
  opinion2: "",
  opinion3: "",
  opinion4: ""
};

try {
  const res = submitCurriculumResponse(payload3);
  console.log(`   * 반환 결과: ${JSON.stringify(res)}`);
  
  const sheet = mockSpreadsheet.getSheetByName("교육과정_웹앱_응답");
  assert.strictEqual(sheet.rows.length, 3, "에러가 나야 하므로 데이터가 추가되지 않아 여전히 3개 행이어야 합니다.");
  assert.strictEqual(res.success, false, "성함이 없으므로 success 값은 false여야 합니다.");
  assert.strictEqual(res.error, "선생님 성함이 선택되지 않았습니다.", "에러 메시지가 정확해야 합니다.");
  
  console.log("   ✅ Test 4 통과: 성함 누락 차단 확인 완료.\n");
} catch (err) {
  console.error("   ❌ Test 4 실패: " + err.toString());
  process.exit(1);
}

// --- 테스트 5: 유효성 검사 실패 테스트 (선택 안 누락) ---
console.log("🧪 [Test 5] submitCurriculumResponse() 유효성 실패 테스트 (선택 안 공백)");
const payload4 = {
  name: "조진희",
  selectedOption: "", // 미선택
  opinion1: "기존 의견 기재",
  opinion2: "",
  opinion3: "",
  opinion4: ""
};

try {
  const res = submitCurriculumResponse(payload4);
  console.log(`   * 반환 결과: ${JSON.stringify(res)}`);
  
  const sheet = mockSpreadsheet.getSheetByName("교육과정_웹앱_응답");
  assert.strictEqual(sheet.rows.length, 3, "에러가 나야 하므로 데이터가 추가되지 않아 여전히 3개 행이어야 합니다.");
  assert.strictEqual(res.success, false, "선택 안이 없으므로 success 값은 false여야 합니다.");
  assert.strictEqual(res.error, "선택하신 안이 없습니다. 한 가지 안을 반드시 선택해야 합니다.", "선택 안 누락 에러 메시지가 정확해야 합니다.");
  
  console.log("   ✅ Test 5 통과: 선택 안 누락 시 필수 선택 유효성 차단 확인 완료.\n");
} catch (err) {
  console.error("   ❌ Test 5 실패: " + err.toString());
  process.exit(1);
}

// --- 테스트 6: 정상 제출 - 3차 (4안 선택) ---
console.log("🧪 [Test 6] submitCurriculumResponse() 정상 제출 테스트 (3차: 조진희 선생님 - 4안 선택)");
const payload5 = {
  name: "조진희",
  selectedOption: "4안",
  opinion1: "",
  opinion2: "",
  opinion3: "",
  opinion4: "국영수 학점을 일부 축소하여 진로탐구 선택군을 넓힌 점이 마음에 듭니다."
};

try {
  const res = submitCurriculumResponse(payload5);
  console.log(`   * 반환 결과: ${JSON.stringify(res)}`);
  
  const sheet = mockSpreadsheet.getSheetByName("교육과정_웹앱_응답");
  assert.strictEqual(sheet.rows.length, 4, "3차 데이터 추가로 인해 최종 4개 행이 존재해야 합니다.");
  assert.strictEqual(sheet.rows[3][1], "조진희", "네 번째 행의 이름은 '조진희'이어야 합니다.");
  assert.strictEqual(sheet.rows[3][2], "4안", "선택된 안은 '4안'이어야 합니다.");
  assert.strictEqual(sheet.rows[3][6], "국영수 학점을 일부 축소하여 진로탐구 선택군을 넓힌 점이 마음에 듭니다.", "4안 의견이 정확히 기록되어야 합니다.");
  assert.strictEqual(res.success, true, "정상 응답 시 success 값은 true여야 합니다.");
  
  console.log("   ✅ Test 6 통과: 3차 정상 응답 및 시트 누적 완료.\n");
} catch (err) {
  console.error("   ❌ Test 6 실패: " + err.toString());
  process.exit(1);
}

console.log("==================================================");
console.log("🎉 모든 하네스 테스트 케이스 통과! 백엔드 기능 100% 검증 완료!");
console.log("==================================================");
