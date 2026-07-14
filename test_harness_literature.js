const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

console.log("==========================================");
console.log("🧪 2학년 문학 수행평가 시스템 테스트 하네스 기동 (가로 명렬반 연동)");
console.log("==========================================\n");

// --- 1. MOCKING GOOGLE APPS SCRIPT SERVICES ---

// Mock Properties Service
let localApiKey = 'mock_api_key_12345';
try {
  const envContent = fs.readFileSync('.env', 'utf8');
  const match = envContent.match(/^GEMINI_API_KEY\s*=\s*(.*)$/m);
  if (match && match[1]) {
    localApiKey = match[1].trim();
  }
} catch (e) {
  // ignore
}

const scriptPropertiesStore = {
  'GEMINI_API_KEY': localApiKey
};
global.PropertiesService = {
  getScriptProperties: () => ({
    getProperty: (key) => scriptPropertiesStore[key],
    setProperty: (key, val) => {
      scriptPropertiesStore[key] = val;
    }
  })
};

// Mock Utilities
global.Utilities = {
  sleep: (ms) => {
    // console.log(`   [Utilities.sleep] ${ms}ms 대기`);
  }
};

// Mock HtmlService
global.HtmlService = {
  createTemplateFromFile: (fileName) => {
    return {
      evaluate: () => {
        return {
          setTitle: (title) => {
            return {
              addMetaTag: (name, content) => {
                return {
                  setXFrameOptionsMode: (mode) => {
                    return `Rendered ${fileName} with Title "${title}"`;
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

// Mock UrlFetchApp
let mockHttpFetchHandler = () => {
  return {
    getResponseCode: () => 200,
    getContentText: () => JSON.stringify({
      candidates: [{
        content: {
          parts: [{
            text: JSON.stringify({
              seteuk: "문학 시간에 고전시가 '만흥'을 학습한 후, 작품 속 화자의 안빈낙도 태도를 현대적 관점에서 깊이 성찰함. 무책임성을 포착하고 현대의 조용한 사직과 비교 분석하는 비평문을 작성함. 비판적 사고 역량을 훌륭히 발휘함."
            })
          }]
        }
      }]
    })
  };
};

global.UrlFetchApp = {
  fetch: (url, options) => {
    return mockHttpFetchHandler(url, options);
  }
};

// Mock UI interaction
let lastAlertMessage = "";
let mockPromptButton = "OK";
let mockPromptInput = "test_api_key";

const mockUi = {
  createMenu: (name) => {
    const menuObj = {
      addItem: function(itemName, functionName) {
        return this;
      },
      addSeparator: function() {
        return this;
      },
      addToUi: function() {
      }
    };
    return menuObj;
  },
  alert: (title, message, buttons) => {
    lastAlertMessage = title + ": " + message;
    return "OK";
  },
  prompt: (title, message, buttons) => {
    return {
      getSelectedButton: () => mockPromptButton,
      getResponseText: () => mockPromptInput
    };
  },
  Button: { OK: "OK", CANCEL: "CANCEL" },
  ButtonSet: { OK_CANCEL: "OK_CANCEL", OK: "OK" }
};

// Mock SpreadsheetApp
class MockRange {
  constructor(sheet, startRow, startCol, numRows = 1, numCols = 1) {
    this.sheet = sheet;
    this.startRow = startRow;
    this.startCol = startCol;
    this.numRows = numRows;
    this.numCols = numCols;
  }

  getValues() {
    const result = [];
    for (let r = 0; r < this.numRows; r++) {
      const rowData = [];
      for (let c = 0; c < this.numCols; c++) {
        const val = this.sheet._getCell(this.startRow + r, this.startCol + c);
        rowData.push(val);
      }
      result.push(rowData);
    }
    return result;
  }

  setValue(val) {
    for (let r = 0; r < this.numRows; r++) {
      for (let c = 0; c < this.numCols; c++) {
        this.sheet._setCell(this.startRow + r, this.startCol + c, val);
      }
    }
    return this;
  }

  setFontWeight(weight) {
    return this;
  }

  setBackground(color) {
    for (let r = 0; r < this.numRows; r++) {
      for (let c = 0; c < this.numCols; c++) {
        this.sheet._setMetadata(this.startRow + r, this.startCol + c, 'background', color);
      }
    }
    return this;
  }
}

class MockSheet {
  constructor(name) {
    this.name = name;
    this.rows = [];
    this.metadata = {};
  }

  getName() { return this.name; }

  getLastRow() {
    return this.rows.length;
  }

  getRange(row, col, numRows, numCols) {
    return new MockRange(this, row, col, numRows, numCols);
  }

  appendRow(rowValues) {
    this.rows.push([...rowValues]);
  }

  _getCell(row, col) {
    const rIdx = row - 1;
    const cIdx = col - 1;
    if (this.rows[rIdx] && this.rows[rIdx][cIdx] !== undefined) {
      return this.rows[rIdx][cIdx];
    }
    return "";
  }

  _setCell(row, col, val) {
    const rIdx = row - 1;
    const cIdx = col - 1;
    while (this.rows.length <= rIdx) {
      this.rows.push(new Array(20).fill("")); // 명렬 데이터 가로 20열 대응
    }
    this.rows[rIdx][cIdx] = val;
  }

  _setMetadata(row, col, key, val) {
    const coord = `${row},${col}`;
    if (!this.metadata[coord]) this.metadata[coord] = {};
    this.metadata[coord][key] = val;
  }

  _getMetadata(row, col, key) {
    const coord = `${row},${col}`;
    return this.metadata[coord] ? this.metadata[coord][key] : null;
  }
}

class MockSpreadsheet {
  constructor() {
    this.sheets = {};
  }

  getSheetByName(name) {
    return this.sheets[name] || null;
  }

  insertSheet(name) {
    const s = new MockSheet(name);
    this.sheets[name] = s;
    return s;
  }

  toast(msg, title) {
  }
}

let activeSpreadsheet = new MockSpreadsheet();

global.SpreadsheetApp = {
  getActiveSpreadsheet: () => activeSpreadsheet,
  getUi: () => mockUi,
  flush: () => {
  }
};

// Mock ScriptApp
let mockTriggers = [];
global.ScriptApp = {
  getProjectTriggers: () => mockTriggers,
  deleteTrigger: (trigger) => {
    mockTriggers = mockTriggers.filter(t => t !== trigger);
  },
  newTrigger: (functionName) => {
    return {
      timeBased: function() {
        return {
          everyMinutes: function(min) {
            return {
              create: function() {
                const newTrig = {
                  getHandlerFunction: () => functionName
                };
                mockTriggers.push(newTrig);
                return newTrig;
              }
            };
          }
        };
      }
    };
  }
};

// --- 2. LOAD CODE_LITERATURE.GS ---
const code = fs.readFileSync('Code_Literature.gs', 'utf8');
vm.runInThisContext(code);

// --- 3. RUNNING TEST SUITES ---
function runTestSuite() {
  console.log("🧪 [테스트 시나리오 1] doGet() 웹앱 서빙 테스트");
  const htmlOutput = doGet();
  assert.strictEqual(htmlOutput, 'Rendered index_literature with Title "2학년 문학 수행평가 - 현대적 관점으로 고전시가 비평하기"', "doGet 반환 형식이 올바르지 않습니다.");
  console.log("   ✅ 통과: doGet() 렌더링 완료\n");

  console.log("🧪 [테스트 시나리오 2] getRoster() 가로 명렬(Sheet1) 읽기 테스트");
  // 가로 명렬 시트 모킹 (Sheet1)
  const rosterSheet = activeSpreadsheet.insertSheet("Sheet1");
  // 1행: 헤더 (1반 번호, 1반 이름, 2반 번호, 2반 이름 ... 10반 번호, 10반 이름)
  const headers = [];
  for (let b = 1; b <= 10; b++) {
    headers.push(`${b}반 번호`, `${b}반 이름`);
  }
  rosterSheet.appendRow(headers);

  // 2행: 1반 1번 홍길동, 2반 1번 성춘향
  const row2 = new Array(20).fill("");
  row2[0] = 1; row2[1] = "홍길동"; // 1반 1번
  row2[2] = 1; row2[3] = "성춘향"; // 2반 1번
  rosterSheet.appendRow(row2);

  // 3행: 1반 2번 이몽룡, 그리고 class size summary row처럼 2반 번호에 2, 이름에 "31명" 입력하여 필터 테스트
  const row3 = new Array(20).fill("");
  row3[0] = 2; row3[1] = "이몽룡"; // 1반 2번
  row3[2] = 2; row3[3] = "31명";   // 필터링되어야 하는 데이터
  rosterSheet.appendRow(row3);

  const rosterRes = getRoster();
  assert.ok(rosterRes.success, "getRoster 호출이 실패했습니다. 에러: " + rosterRes.error);
  assert.strictEqual(rosterRes.roster[1].length, 2, "1반 학생 수가 맞지 않습니다.");
  assert.strictEqual(rosterRes.roster[2].length, 1, "2반 학생 수가 맞지 않습니다. ('31명' 필터링 확인)");
  assert.strictEqual(rosterRes.roster[1][0].name, "홍길동", "1반 1번 이름 오매칭");
  assert.strictEqual(rosterRes.roster[1][1].name, "이몽룡", "1반 2번 이름 오매칭");
  assert.strictEqual(rosterRes.roster[2][0].name, "성춘향", "2반 1번 이름 오매칭");
  console.log("   ✅ 통과: getRoster() 가로 정렬 파싱 및 반별 명렬 매핑 완벽 검증\n");

  console.log("🧪 [테스트 시나리오 3] submitLiteratureAnswer() 학생 답안 제출 테스트");
  const mockSubmitData = {
    ban: 1,
    num: 2,
    name: "이몽룡",
    theme: "안빈낙도의 재발견",
    question: "자연 속에서 안빈낙도하는 삶이 치열한 경쟁 사회를 살아가는 현대인에게 '진정한 휴식'의 모델이 되는가?",
    essay: "자연속에서의 안빈낙도는 치열한 경쟁 사회를 살아가는 현대인에게 단순한 현실도피이다..."
  };

  const submitRes = submitLiteratureAnswer(mockSubmitData);
  assert.ok(submitRes.success, "submitLiteratureAnswer 호출이 실패했습니다.");
  
  // 제출 후 시트를 검색하여 데이터가 기록되었는지 확인
  const responseSheet = activeSpreadsheet.getSheetByName("수행평가_응답");
  assert.ok(responseSheet, "수행평가_응답 시트가 생성되지 않았습니다.");
  const lastRow = responseSheet.getLastRow();
  assert.strictEqual(lastRow, 2, "제출 데이터가 시트에 기록되지 않았습니다.");
  assert.strictEqual(responseSheet._getCell(2, 4), "이몽룡", "이름 데이터 오매칭");
  assert.strictEqual(responseSheet._getCell(2, 10), "대기", "초기 상태는 '대기'여야 합니다.");
  console.log("   ✅ 통과: submitLiteratureAnswer() 저장 및 상태관리 검증 완료\n");

  console.log("🧪 [테스트 시나리오 4] promptApiKey() API 키 저장 기능 검증");
  mockPromptButton = "OK";
  mockPromptInput = "my_custom_api_key_9999";
  promptApiKey();
  const savedKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
  assert.strictEqual(savedKey, "my_custom_api_key_9999", "API 키가 PropertiesService에 정상적으로 저장되지 않았습니다.");
  console.log("   ✅ 통과: promptApiKey()를 통한 스크립트 속성 보안 저장 검증 완료\n");

  console.log("🧪 [테스트 시나리오 5] generateSingleTestSeteuk() 1명 테스트 생성 검증");
  lastAlertMessage = "";
  generateSingleTestSeteuk();
  
  assert.ok(lastAlertMessage.includes("테스트 생성 성공"), "1명 테스트 생성 결과 확인에 실패했습니다.");
  assert.strictEqual(responseSheet._getCell(2, 10), "완료", "세특 생성 후 상태가 '완료'로 변경되지 않았습니다.");
  assert.ok(responseSheet._getCell(2, 8).includes("안빈낙도"), "생성된 세특 내용에 핵심 키워드가 누락되었습니다.");
  console.log("   ✅ 통과: generateSingleTestSeteuk() 세특 생성 및 팝업 렌더링 검증 완료\n");

  console.log("🧪 [테스트 시나리오 6] generateSeteukInBatches() 배치 및 오류 복구력 검증");
  responseSheet.rows = [];
  responseSheet.appendRow(["제출일시", "반", "번호", "이름", "선택한 관점 주제", "비평 질문", "비평문", "세특 초안 (AI)", "글자수(바이트)", "처리 상태"]);
  responseSheet.appendRow([new Date(), 1, 1, "성공학생", "안빈낙도", "질문", "비평문 텍스트...", "", "", "대기"]);
  responseSheet.appendRow([new Date(), 1, 2, "실패학생", "안빈낙도", "질문", "비평문 텍스트...", "", "", "대기"]);

  mockHttpFetchHandler = (url, options) => {
    const payloadStr = options && options.payload ? options.payload : "";
    if (payloadStr.includes("실패학생")) {
      return {
        getResponseCode: () => 500,
        getContentText: () => "Internal Server Error"
      };
    }
    return {
      getResponseCode: () => 200,
      getContentText: () => JSON.stringify({
        candidates: [{
          content: {
            parts: [{
              text: JSON.stringify({ seteuk: "성공적으로 생성된 세특입니다. 안빈낙도 역량 발휘함." })
            }]
          }
        }]
      })
    };
  };

  generateSeteukInBatches();

  assert.strictEqual(responseSheet._getCell(2, 10), "완료", "성공 케이스에 대한 완료 처리가 되지 않았습니다.");
  assert.strictEqual(responseSheet._getCell(3, 10), "실패", "실패 케이스에 대한 예외 복구 및 실패 표기가 되지 않았습니다.");
  assert.strictEqual(responseSheet._getMetadata(3, 10, 'background'), "#fee2e2", "실패 행의 가시성 배경색 칠하기 검증 실패");
  console.log("   ✅ 통과: generateSeteukInBatches() 배치 처리 루프 및 예외 복구력 검증 완료\n");

  console.log("==========================================");
  console.log("🎉 모든 문학 수행평가 시스템 검증용 하네스 테스트를 통과했습니다!");
  console.log("==========================================");
}

try {
  runTestSuite();
} catch (e) {
  console.error("\n❌ [테스트 실패] 하네스 동작 중 검증 에러:");
  console.error(e);
  process.exit(1);
}
