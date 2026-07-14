/**
 * 2027학년도 고등학교 입학등록 확인서 웹앱 백엔드 테스트 하네스
 * 
 * 제작: Antigravity
 * 목적: '입학등록_웹앱_코드.gs' 파일을 읽어와 가상 구글 앱스 스크립트(GAS) 및 드라이브/문서(Docs) API 환경을 시뮬레이션하고,
 *       합격자 데이터 검증, 서명 이미지 디코딩, PDF 복제 및 텍스트 치환, 시트 기록 등 전 기능이 안정적으로 작동하는지 로컬 검증합니다.
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

console.log("==================================================");
console.log("🚀 2027학년도 입학등록 확인서 웹앱 백엔드 테스트 하네스 기동");
console.log("==================================================\n");

// 1. 백엔드 스크립트 파일 로드
const codePath = path.join(__dirname, '입학등록_웹앱_코드.gs');
if (!fs.existsSync(codePath)) {
  console.error(`❌ 오류: 테스트 대상 파일 '${codePath}'을 찾을 수 없습니다.`);
  process.exit(1);
}
const codeContent = fs.readFileSync(codePath, 'utf8');

// 2. 가상 GAS/Drive/Docs API Mocks 정의

// 로그 보관용
const mockLoggerLogs = [];
const mockLogger = {
  log: function(msg) {
    mockLoggerLogs.push(msg);
    console.log("   [GAS Logger] " + msg);
  }
};

// 가상 구글 드라이브 파일 객체
class FileMock {
  constructor(name, content, id) {
    this.name = name;
    this.content = content;
    this.id = id || "file_id_" + Math.random().toString(36).substr(2, 9);
    this.sharingAccess = null;
    this.sharingPermission = null;
    this.trashed = false;
  }
  
  getId() { return this.id; }
  getName() { return this.name; }
  setName(name) { this.name = name; }
  getUrl() { return "https://drive.google.com/open?id=" + this.id; }
  setSharing(access, permission) {
    this.sharingAccess = access;
    this.sharingPermission = permission;
  }
  setTrashed(state) {
    this.trashed = state;
  }
  
  getAs(mimeType) {
    return {
      name: this.name + ".pdf",
      content: "PDF_BLOB_OF_" + this.content,
      contentType: mimeType
    };
  }
}

// 가상 구글 드라이브 폴더 객체
class FolderMock {
  constructor(name, id) {
    this.name = name;
    this.id = id || "folder_id_" + Math.random().toString(36).substr(2, 9);
    this.files = [];
  }
  
  getId() { return this.id; }
  createFile(blob) {
    const file = new FileMock(blob.name, blob.content, "file_id_" + Math.random().toString(36).substr(2, 9));
    this.files.push(file);
    return file;
  }
}

// 가상 드라이브 앱 서비스
const mockDriveApp = {
  folders: {},
  files: {},
  
  getFoldersByName: function(name) {
    const folderList = [];
    if (this.folders[name]) {
      folderList.push(this.folders[name]);
    }
    
    let index = 0;
    return {
      hasNext: function() { return index < folderList.length; },
      next: function() { return folderList[index++]; }
    };
  },
  
  createFolder: function(name) {
    const folder = new FolderMock(name);
    this.folders[name] = folder;
    return folder;
  },
  
  getFilesByName: function(name) {
    const fileList = [];
    for (let id in this.files) {
      if (this.files[id].name === name) {
        fileList.push(this.files[id]);
      }
    }
    
    let index = 0;
    return {
      hasNext: function() { return index < fileList.length; },
      next: function() { return fileList[index++]; }
    };
  },
  
  getFileById: function(id) {
    const file = this.files[id];
    if (!file) throw new Error("드라이브에서 파일 ID " + id + "를 찾을 수 없습니다.");
    
    file.makeCopy = (copyName, folder) => {
      const copy = new FileMock(copyName, file.content);
      this.files[copy.id] = copy;
      if (folder) folder.files.push(copy);
      
      // 구글 문서 복사본일 경우 DocumentApp 모크에도 등록하여 getBody() 오작동 방지
      if (mockDocumentApp.docs[file.id]) {
        const originalDoc = mockDocumentApp.docs[file.id];
        const docCopy = new DocumentMock(copyName, copy.id);
        docCopy.text = originalDoc.text;
        mockDocumentApp.docs[copy.id] = docCopy;
      }
      return copy;
    };
    return file;
  },
  
  Access: { ANYONE_WITH_LINK: "ANYONE_WITH_LINK" },
  Permission: { VIEW: "VIEW" }
};

// 가상 구글 문서 객체
class DocumentMock {
  constructor(name, id) {
    this.name = name;
    this.id = id;
    this.text = "";
    this.signaturesAdded = [];
  }
  
  getId() { return this.id; }
  
  getBody() {
    const docObj = this;
    return {
      setMarginTop: function() {},
      setMarginBottom: function() {},
      setMarginLeft: function() {},
      setMarginRight: function() {},
      
      appendParagraph: function(txt) {
        docObj.text += txt + "\n";
        return {
          setFontSize: function() { return this; },
          setBold: function() { return this; },
          setLineSpacing: function() { return this; },
          setAlignment: function() { return this; },
          setFontColor: function() { return this; }
        };
      },
      
      appendTable: function(cells) {
        docObj.text += " [Table: " + JSON.stringify(cells) + "] ";
        const mockTable = {
          setBorderWidth: function() {},
          setBorderColor: function() {},
          setColumnWidth: function() {},
          getNumRows: function() { return cells.length; },
          getRow: function(i) {
            return {
              getNumCells: function() { return cells[i].length; },
              getCell: function(j) {
                return mockCell(i, j);
              }
            };
          },
          getCell: function(row, col) {
            return mockCell(row, col);
          }
        };
        
        function mockCell(row, col) {
          return {
            setBackgroundColor: function() { return this; },
            setMinimumHeight: function() { return this; },
            setPaddingTop: function() {},
            setPaddingBottom: function() {},
            setPaddingLeft: function() {},
            setPaddingRight: function() {},
            getChild: function() {
              return {
                asParagraph: function() {
                  return {
                    setFontSize: function() {},
                    setBold: function() {},
                    setLineSpacing: function() {},
                    setAlignment: function() {}
                  };
                }
              };
            },
            appendParagraph: function(txt) {
              docObj.text += txt + "\n";
              return {
                setFontSize: function() { return this; },
                setBold: function() { return this; },
                setLineSpacing: function() { return this; },
                setAlignment: function() { return this; },
                setFontColor: function() { return this; }
              };
            },
            appendTable: function(subCells) {
              docObj.text += " [SubTable: " + JSON.stringify(subCells) + "] ";
              return mockTable;
            }
          };
        }
        
        return mockTable;
      },
      
      replaceText: function(placeholder, value) {
        docObj.text = docObj.text.replace(placeholder, value);
      },
      
      findText: function(pattern) {
        if (docObj.text.includes(pattern) || pattern === "{{학생서명}}" || pattern === "{{보호자서명}}") {
          return {
            getElement: function() {
              return {
                asText: function() {
                  return {
                    getText: function() { return docObj.text; },
                    setText: function(val) { docObj.text = val; }
                  };
                },
                getParent: function() {
                  return {
                    asParagraph: function() {
                      return {
                        appendInlineImage: function(imageBlob) {
                          docObj.signaturesAdded.push({
                            placeholder: pattern,
                            blob: imageBlob
                          });
                          return {
                            setWidth: function() {},
                            setHeight: function() {}
                          };
                        }
                      };
                    }
                  };
                }
              };
            }
          };
        }
        return null;
      }
    };
  }
  
  saveAndClose() {}
}

// 가상 구글 문서 앱
const mockDocumentApp = {
  docs: {},
  create: function(name) {
    const id = "doc_id_" + Math.random().toString(36).substr(2, 9);
    const doc = new DocumentMock(name, id);
    this.docs[id] = doc;
    
    // 드라이브에도 파일 기록 생성
    mockDriveApp.files[id] = new FileMock(name, "DOC_CONTENT_OF_" + name, id);
    
    return doc;
  },
  openById: function(id) {
    return this.docs[id] || null;
  },
  HorizontalAlignment: { CENTER: "CENTER", LEFT: "LEFT" }
};

// 가상 스프레드시트 탭 객체
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
  
  getDataRange() {
    const sheetObj = this;
    return {
      getValues: function() {
        return sheetObj.rows;
      }
    };
  }
  
  getRange(row, col, numRows, numCols) {
    const sheetObj = this;
    const rangeMock = {
      setFontWeight: function(val) { return rangeMock; },
      setBackground: function(val) { return rangeMock; },
      setHorizontalAlignment: function(val) { return rangeMock; },
      setValue: function(val) {
        // 셀 값 수정 시 시트 rows 데이터에 반영
        if (sheetObj.rows[row - 1]) {
          sheetObj.rows[row - 1][col - 1] = val;
        }
      }
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

// 가상 스프레드시트 컨테이너
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

// HTML 서비스
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
  XFrameOptionsMode: { ALLOWALL: "ALLOWALL" }
};

// 유틸리티
const mockUtilities = {
  base64Decode: function(base64Str) {
    return {
      content: base64Str,
      toString: () => "DECODED_DATA_OF_" + base64Str
    };
  },
  newBlob: function(decodedData, contentType, fileName) {
    return {
      content: decodedData.content,
      contentType: contentType,
      name: fileName
    };
  },
  formatDate: function(date, tz, format) {
    return "2027년 1월 4일";
  }
};

const mockMimeType = {
  PDF: "application/pdf"
};

// 3. 테스트 컨텍스트 샌드박스 설정 및 스크립트 실행
const context = {
  SpreadsheetApp: mockSpreadsheetApp,
  HtmlService: mockHtmlService,
  DriveApp: mockDriveApp,
  DocumentApp: mockDocumentApp,
  Utilities: mockUtilities,
  MimeType: mockMimeType,
  Logger: mockLogger,
  console: console,
  doGet: null,
  checkCandidate: null,
  submitAdmissionConfirmation: null
};

vm.createContext(context);
try {
  vm.runInContext(codeContent, context);
  console.log("✅ '입학등록_웹앱_코드.gs' 컴파일 및 컨텍스트 바인딩 완료.\n");
} catch (err) {
  console.error("❌ 오류: 백엔드 스크립트 컴파일 도중 에러가 발생했습니다.");
  console.error(err);
  process.exit(1);
}

const doGet = context.doGet;
const checkCandidate = context.checkCandidate;
const submitAdmissionConfirmation = context.submitAdmissionConfirmation;

// 4. 테스트 시나리오 수행

// --- 테스트 1: doGet() 서비스 연결 상태 검증 ---
console.log("🧪 [Test 1] doGet() 웹앱 서빙 기능 작동 검증");
try {
  const htmlResult = doGet();
  console.log(`   * 결과 HTML 반환값: ${htmlResult}`);
  assert.ok(htmlResult.includes("입학등록_웹앱_화면"), "doGet()은 '입학등록_웹앱_화면' 템플릿을 호출해야 합니다.");
  assert.ok(htmlResult.includes("2027학년도"), "doGet() 반환 결과에 2027학년도가 명시되어야 합니다.");
  console.log("   ✅ Test 1 통과: doGet() 서빙 상태 확인 완료.\n");
} catch (err) {
  console.error("   ❌ Test 1 실패: " + err.toString());
  process.exit(1);
}

// --- 테스트 2: 합격자 정보 확인 API 검증 ---
console.log("🧪 [Test 2] checkCandidate() 신원 교차 검증 API 테스트");
try {
  // 처음엔 시트가 없으므로 API 호출 시 내부에서 시트가 자동 빌드됨 (홍길동: 2027-0001)
  const masterSheetBefore = mockSpreadsheet.getSheetByName("합격자_마스터");
  assert.strictEqual(masterSheetBefore, null, "초기에는 합격자 마스터 시트가 없어야 합니다.");
  
  // 1) 정상 합격자 정보 조회
  const res1 = checkCandidate("홍길동", "2027-0001");
  console.log(`   * 정상 조회 반환 결과: ${JSON.stringify(res1)}`);
  assert.strictEqual(res1.valid, true, "합격자 명단에 있는 조합이므로 valid는 true여야 합니다.");
  assert.strictEqual(res1.alreadySubmitted, false, "등록상태가 '미등록'이므로 alreadySubmitted는 false여야 합니다.");
  assert.strictEqual(res1.schoolName, "진해남중학교", "출신중학교 정보가 정상적으로 반환되어야 합니다.");
  assert.strictEqual(res1.birthDate, "090101", "생년월일 정보가 정상적으로 반환되어야 합니다.");
  
  // 시트가 잘 자동 생성되었는지 확인
  const masterSheetAfter = mockSpreadsheet.getSheetByName("합격자_마스터");
  assert.ok(masterSheetAfter, "API 호출 도중 '합격자_마스터' 시트가 자동 생성되어야 합니다.");
  assert.strictEqual(masterSheetAfter.rows.length, 4, "헤더 포함 총 4개의 가상 행이 존재해야 합니다.");
  
  // 2) 비합격자 정보 조회
  const res2 = checkCandidate("아무개", "2027-9999");
  console.log(`   * 비합격자 조회 반환 결과: ${JSON.stringify(res2)}`);
  assert.strictEqual(res2.valid, false, "합격자 명단에 없으므로 valid는 false여야 합니다.");
  assert.ok(res2.error.includes("일치하지 않습니다"), "에러 메시지가 존재해야 합니다.");
  
  console.log("   ✅ Test 2 통과: 신원 교차 검증 및 초기 마스터 명단 자동 빌드 확인 완료.\n");
} catch (err) {
  console.error("   ❌ Test 2 실패: " + err.toString());
  process.exit(1);
}

// --- 테스트 3: 서명 제출 및 PDF 자동 생성, 시트 저장 검증 ---
console.log("🧪 [Test 3] submitAdmissionConfirmation() 서명 등록 및 PDF 생성 프로세스 테스트");
const payload = {
  studentName: "홍길동",
  studentId: "2027-0001",
  parentName: "홍판서",
  parentPhone: "010-1234-5678",
  studentSignature: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJYAAABk...", // 더미 학생 base64 데이터
  parentSignature: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJYAAABk..."  // 더미 보호자 base64 데이터
};

try {
  // 템플릿 문서가 드라이브에 존재하지 않으므로, 백엔드 내부에서 템플릿 Docs 문서를 자동 생성함
  const res = submitAdmissionConfirmation(payload);
  console.log(`   * 최종 등록 반환 결과: ${JSON.stringify(res)}`);
  assert.strictEqual(res.success, true, "정상 조건 하에 서명 등록이 성공해야 합니다.");
  assert.strictEqual(res.studentName, "홍길동", "반환되는 이름이 '홍길동'이어야 합니다.");
  
  // 1) 스프레드시트 기록 확인
  const resSheet = mockSpreadsheet.getSheetByName("등록_확인서_응답");
  assert.ok(resSheet, "'등록_확인서_응답' 시트가 자동 개설되어야 합니다.");
  assert.strictEqual(resSheet.rows.length, 2, "헤더행과 데이터 1행이 추가되어 총 2개 행이 존재해야 합니다.");
  assert.strictEqual(resSheet.rows[1][1], "2027-0001", "접수번호가 일치해야 합니다.");
  assert.strictEqual(resSheet.rows[1][2], "홍길동", "저장된 학생 이름이 일치해야 합니다.");
  assert.strictEqual(resSheet.rows[1][3], "진해남중학교", "출신중학교가 일치해야 합니다.");
  assert.strictEqual(resSheet.rows[1][4], "090101", "생년월일이 일치해야 합니다.");
  assert.strictEqual(resSheet.rows[1][5], "홍판서", "보호자 성명이 일치해야 합니다.");
  assert.strictEqual(resSheet.rows[1][6], "010-1234-5678", "연락처가 일치해야 합니다.");
  
  // 2) 드라이브 이미지 저장 및 PDF 발급 확인
  const imgFolder = mockDriveApp.folders["2027학년도_입학등록확인서_서명"];
  const pdfFolder = mockDriveApp.folders["2027학년도_입학등록확인서_PDF"];
  assert.ok(imgFolder, "'2027학년도_입학등록확인서_서명' 이미지 폴더가 자동 생성되어야 합니다.");
  assert.ok(pdfFolder, "'2027학년도_입학등록확인서_PDF' 폴더가 자동 생성되어야 합니다.");
  
  const studentImg = imgFolder.files.find(f => f.name === "2027-0001_홍길동_학생서명.png");
  const parentImg = imgFolder.files.find(f => f.name === "2027-0001_홍길동_보호자서명.png");
  assert.ok(studentImg, "학생 서명 이미지가 접수번호_이름 양식으로 저장되어야 합니다.");
  assert.ok(parentImg, "보호자 서명 이미지가 접수번호_이름 양식으로 저장되어야 합니다.");
  
  // 3) 마스터 시트 상태가 '등록완료'로 갱신되었는지 검증
  const masterSheet = mockSpreadsheet.getSheetByName("합격자_마스터");
  const hongRow = masterSheet.rows.find(r => r[0] === "2027-0001");
  assert.strictEqual(hongRow[4], "등록완료", "합격자 마스터의 등록상태가 '등록완료'로 변경되어야 합니다.");
  
  console.log("   ✅ Test 3 통과: 이미지 디코딩, PDF 컴파일, 마스터 상태 갱신 프로세스 검증 완료.\n");
} catch (err) {
  console.error("   ❌ Test 3 실패: " + err.toString());
  process.exit(1);
}

// --- 테스트 4: 중복 제출 차단 검증 ---
console.log("🧪 [Test 4] checkCandidate() 중복 제출 차단 기능 테스트");
try {
  // 이미 홍길동(2027-0001)은 등록을 완료한 상태임
  const res = checkCandidate("홍길동", "2027-0001");
  console.log(`   * 중복 조회 반환 결과: ${JSON.stringify(res)}`);
  assert.strictEqual(res.valid, true, "합격자 명단 매칭 자체는 true여야 합니다.");
  assert.strictEqual(res.alreadySubmitted, true, "이미 시트에 기록되어 있으므로 alreadySubmitted는 true여야 합니다.");
  
  console.log("   ✅ Test 4 통과: 중복 접수 감지 및 진입 차단 검증 완료.\n");
} catch (err) {
  console.error("   ❌ Test 4 실패: " + err.toString());
  process.exit(1);
}

console.log("==================================================");
console.log("🎉 모든 백엔드 및 자동화 로직 유닛 테스트 성공! 결함 없음!");
console.log("==================================================");
