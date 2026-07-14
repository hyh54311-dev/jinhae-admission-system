/**
 * 2026학년도 진해고등학교 특별실 예약 시스템 - 백엔드 (Google Apps Script)
 * 
 * 제작: Antigravity (Google DeepMind Team)
 * 목적: 교내 공용 특별실 예약을 편리하게 조율하며, 구글 스프레드시트를 DB로 활용합니다.
 */

function doGet() {
  return HtmlService.createTemplateFromFile('특별실예약_웹앱_화면')
      .evaluate()
      .setTitle('진해고등학교 특별실 예약 시스템')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.SAMEORIGIN);
}

/**
 * 스프레드시트 초기화 함수
 * 시트가 없을 경우 자동으로 생성하고 교직원 데이터(111명) 및 기본 특별실 설정을 채워 넣습니다.
 */
function initSpreadsheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. 특별실_예약내역 시트 초기화
  var sheetReservations = ss.getSheetByName("특별실_예약내역");
  if (!sheetReservations) {
    sheetReservations = ss.insertSheet("특별실_예약내역");
    // FIX #14: var headers 중복 선언 방지를 위해 명시적 변수명 사용
    var headersRes = ["ID", "예약일자", "교시", "특별실", "예약자명", "대상학급", "사용목적", "등록일시"];
    sheetReservations.appendRow(headersRes);
    sheetReservations.getRange(1, 1, 1, headersRes.length)
                     .setFontWeight("bold")
                     .setBackground("#e2e8f0")
                     .setHorizontalAlignment("center");
    sheetReservations.setFrozenRows(1);
  }

  // 2. 특별실_설정 시트 초기화
  var sheetSettings = ss.getSheetByName("특별실_설정");
  if (!sheetSettings) {
    sheetSettings = ss.insertSheet("특별실_설정");
    var headersSettings = ["특별실명", "8교시이후제한여부", "설명"];
    sheetSettings.appendRow(headersSettings);
    sheetSettings.getRange(1, 1, 1, headersSettings.length)
                 .setFontWeight("bold")
                 .setBackground("#e2e8f0")
                 .setHorizontalAlignment("center");
    
    var defaultRooms = [
      ["홈베이스", "N", "1교시부터 예약 가능"],
      ["학교운영위원회실", "N", "1교시부터 예약 가능"],
      ["창의융합교실", "Y", "8교시(방과후)부터만 예약 가능"],
      ["체육관(강당)", "Y", "8교시(방과후)부터만 예약 가능"]
    ];
    for (var i = 0; i < defaultRooms.length; i++) {
      sheetSettings.appendRow(defaultRooms[i]);
    }
    sheetSettings.setFrozenRows(1);
  }

  // 3. 교직원_목록 시트 초기화 (초기화 시 111명 교직원을 자동 등록하지만, 이후 시트에서 직접 수정/추가 가능)
  var sheetTeachers = ss.getSheetByName("교직원_목록");
  if (!sheetTeachers) {
    sheetTeachers = ss.insertSheet("교직원_목록");
    var headersTeachers = ["성명", "직위", "전화번호", "비밀번호(뒷자리)"];
    sheetTeachers.appendRow(headersTeachers);
    sheetTeachers.getRange(1, 1, 1, headersTeachers.length)
                 .setFontWeight("bold")
                 .setBackground("#e2e8f0")
                 .setHorizontalAlignment("center");
    
    // 파싱된 111명 교직원 목록 삽입
    var teachersData = [
    {
        "name": "오길환",
        "role": "교장",
        "phone": "010-2552-3191",
        "last_4": "3191"
    },
    {
        "name": "조성규",
        "role": "교사",
        "phone": "010-5289-6286",
        "last_4": "6286"
    },
    {
        "name": "이인섭",
        "role": "교감",
        "phone": "010-3880-2150",
        "last_4": "2150"
    },
    {
        "name": "조진희",
        "role": "교사",
        "phone": "010-9301-7748",
        "last_4": "7748"
    },
    {
        "name": "최진영",
        "role": "행정실장",
        "phone": "010-5001-6545",
        "last_4": "6545"
    },
    {
        "name": "진주희",
        "role": "교사",
        "phone": "010-7743-8074",
        "last_4": "8074"
    },
    {
        "name": "강선희",
        "role": "교사",
        "phone": "010-4597-7866",
        "last_4": "7866"
    },
    {
        "name": "차지현",
        "role": "교사",
        "phone": "010-6581-6635",
        "last_4": "6635"
    },
    {
        "name": "강지영",
        "role": "교사",
        "phone": "010-4383-5670",
        "last_4": "5670"
    },
    {
        "name": "최선주",
        "role": "교사",
        "phone": "010-5397-7962",
        "last_4": "7962"
    },
    {
        "name": "강필성",
        "role": "교사",
        "phone": "010-3648-3634",
        "last_4": "3634"
    },
    {
        "name": "최영훈",
        "role": "교사",
        "phone": "010-8983-9499",
        "last_4": "9499"
    },
    {
        "name": "고장선",
        "role": "교사",
        "phone": "010-8369-0924",
        "last_4": "0924"
    },
    {
        "name": "최준호",
        "role": "교사",
        "phone": "010-3133-4187",
        "last_4": "4187"
    },
    {
        "name": "공수련",
        "role": "교사",
        "phone": "010-8013-3436",
        "last_4": "3436"
    },
    {
        "name": "한정규",
        "role": "교사",
        "phone": "010-4701-9845",
        "last_4": "9845"
    },
    {
        "name": "권현정",
        "role": "교사",
        "phone": "010-5112-7214",
        "last_4": "7214"
    },
    {
        "name": "허정화",
        "role": "교사",
        "phone": "010-7242-8187",
        "last_4": "8187"
    },
    {
        "name": "권혜원",
        "role": "교사",
        "phone": "010-3300-0224",
        "last_4": "0224"
    },
    {
        "name": "황요한",
        "role": "교사",
        "phone": "010-3127-3367",
        "last_4": "3367"
    },
    {
        "name": "김다해",
        "role": "교사",
        "phone": "010-2627-8875",
        "last_4": "8875"
    },
    {
        "name": "박은희",
        "role": "교사",
        "phone": "010-7147-0859",
        "last_4": "0859"
    },
    {
        "name": "김다혜",
        "role": "교사",
        "phone": "010-9471-9644",
        "last_4": "9644"
    },
    {
        "name": "이건민",
        "role": "교사",
        "phone": "010-2773-9184",
        "last_4": "9184"
    },
    {
        "name": "김대홍",
        "role": "교사",
        "phone": "010-2679-3527",
        "last_4": "3527"
    },
    {
        "name": "김경수",
        "role": "교사",
        "phone": "010-2325-6817",
        "last_4": "6817"
    },
    {
        "name": "김상우",
        "role": "교사",
        "phone": "010-5194-5410",
        "last_4": "5410"
    },
    {
        "name": "김수민",
        "role": "교사",
        "phone": "010-3588-5502",
        "last_4": "5502"
    },
    {
        "name": "이강수",
        "role": "교사",
        "phone": "010-2817-7769",
        "last_4": "7769"
    },
    {
        "name": "김수진",
        "role": "교사",
        "phone": "010-3377-2882",
        "last_4": "2882"
    },
    {
        "name": "이정한",
        "role": "교사",
        "phone": "010-4841-2271",
        "last_4": "2271"
    },
    {
        "name": "김승우",
        "role": "교사",
        "phone": "010-9345-4475",
        "last_4": "4475"
    },
    {
        "name": "김대현",
        "role": "교사",
        "phone": "010-2039-2184",
        "last_4": "2184"
    },
    {
        "name": "김정아",
        "role": "교사",
        "phone": "010-9408-2151",
        "last_4": "2151"
    },
    {
        "name": "백정용",
        "role": "교사",
        "phone": "010-2721-2450",
        "last_4": "2450"
    },
    {
        "name": "김정화",
        "role": "교사",
        "phone": "010-2694-6021",
        "last_4": "6021"
    },
    {
        "name": "이정희",
        "role": "교사",
        "phone": "010-3860-9210",
        "last_4": "9210"
    },
    {
        "name": "김주연",
        "role": "교사",
        "phone": "010-9314-3826",
        "last_4": "3826"
    },
    {
        "name": "차해경",
        "role": "교사",
        "phone": "010-5207-0014",
        "last_4": "0014"
    },
    {
        "name": "김지영",
        "role": "교사",
        "phone": "010-4907-0702",
        "last_4": "0702"
    },
    {
        "name": "박지혜",
        "role": "교사",
        "phone": "010-2327-7942",
        "last_4": "7942"
    },
    {
        "name": "김지혁",
        "role": "교사",
        "phone": "010-5155-4066",
        "last_4": "4066"
    },
    {
        "name": "임미영",
        "role": "교사",
        "phone": "010-6583-2435",
        "last_4": "2435"
    },
    {
        "name": "김태영",
        "role": "교사",
        "phone": "010-9231-0845",
        "last_4": "0845"
    },
    {
        "name": "남정화",
        "role": "교사",
        "phone": "010-2898-8870",
        "last_4": "8870"
    },
    {
        "name": "문예진",
        "role": "교사",
        "phone": "010-9329-6073",
        "last_4": "6073"
    },
    {
        "name": "조영수",
        "role": "행정과장",
        "phone": "010-2589-1759",
        "last_4": "1759"
    },
    {
        "name": "박민혜",
        "role": "교사",
        "phone": "010-4111-5616",
        "last_4": "5616"
    },
    {
        "name": "정미정",
        "role": "행정계장",
        "phone": "010-2998-1120",
        "last_4": "1120"
    },
    {
        "name": "박세진",
        "role": "교사",
        "phone": "010-8784-2493",
        "last_4": "2493"
    },
    {
        "name": "박지은",
        "role": "주무관",
        "phone": "010-3359-8847",
        "last_4": "8847"
    },
    {
        "name": "박수현",
        "role": "교사",
        "phone": "010-2835-1423",
        "last_4": "1423"
    },
    {
        "name": "박병건",
        "role": "주무관",
        "phone": "010-4554-0815",
        "last_4": "0815"
    },
    {
        "name": "박승현",
        "role": "교사",
        "phone": "010-9371-2714",
        "last_4": "2714"
    },
    {
        "name": "오연자",
        "role": "사무행정원",
        "phone": "010-7675-5606",
        "last_4": "5606"
    },
    {
        "name": "박지환",
        "role": "교사",
        "phone": "010-8914-8146",
        "last_4": "8146"
    },
    {
        "name": "최혜숙",
        "role": "특수행정실무원",
        "phone": "010-7538-5775",
        "last_4": "5775"
    },
    {
        "name": "박진효",
        "role": "교사",
        "phone": "010-8521-4982",
        "last_4": "4982"
    },
    {
        "name": "박현수",
        "role": "매점실무원",
        "phone": "010-4691-5278",
        "last_4": "5278"
    },
    {
        "name": "박혜진",
        "role": "교사",
        "phone": "010-4388-7858",
        "last_4": "7858"
    },
    {
        "name": "김현숙",
        "role": "교무행정원",
        "phone": "010-8758-3331",
        "last_4": "3331"
    },
    {
        "name": "박희영",
        "role": "교사",
        "phone": "010-2681-1110",
        "last_4": "1110"
    },
    {
        "name": "강옥숙",
        "role": "특수교육실무원",
        "phone": "010-4609-8539",
        "last_4": "8539"
    },
    {
        "name": "배미영",
        "role": "교사",
        "phone": "010-3166-4266",
        "last_4": "4266"
    },
    {
        "name": "최미정",
        "role": "전문상담사",
        "phone": "010-2559-0616",
        "last_4": "0616"
    },
    {
        "name": "배수현",
        "role": "교사",
        "phone": "010-4349-1617",
        "last_4": "1617"
    },
    {
        "name": "권계형",
        "role": "전담사서",
        "phone": "010-4998-0664",
        "last_4": "0664"
    },
    {
        "name": "서용환",
        "role": "교사",
        "phone": "010-5580-2542",
        "last_4": "2542"
    },
    {
        "name": "조경우",
        "role": "당직",
        "phone": "010-8978-2817",
        "last_4": "2817"
    },
    {
        "name": "서철민",
        "role": "교사",
        "phone": "010-2757-5960",
        "last_4": "5960"
    },
    {
        "name": "최상재",
        "role": "당직대직",
        "phone": "010-4547-6127",
        "last_4": "6127"
    },
    {
        "name": "서한성",
        "role": "교사",
        "phone": "010-7207-6139",
        "last_4": "6139"
    },
    {
        "name": "정미감",
        "role": "조리사 1",
        "phone": "010-9412-8613",
        "last_4": "8613"
    },
    {
        "name": "성유송",
        "role": "교사",
        "phone": "010-3238-7199",
        "last_4": "7199"
    },
    {
        "name": "이미경",
        "role": "조리사 2",
        "phone": "010-6399-3404",
        "last_4": "3404"
    },
    {
        "name": "안미란",
        "role": "교사",
        "phone": "010-9848-1230",
        "last_4": "1230"
    },
    {
        "name": "경정화",
        "role": "조리실무사",
        "phone": "010-3925-1784",
        "last_4": "1784"
    },
    {
        "name": "여지언",
        "role": "교사",
        "phone": "010-5390-5394",
        "last_4": "5394"
    },
    {
        "name": "김정아",
        "role": "조리실무사",
        "phone": "010-3743-2579",
        "last_4": "2579"
    },
    {
        "name": "이로겸",
        "role": "교사",
        "phone": "010-2060-5521",
        "last_4": "5521"
    },
    {
        "name": "김보경",
        "role": "조리실무사",
        "phone": "010-4627-3837",
        "last_4": "3837"
    },
    {
        "name": "이병의",
        "role": "교사",
        "phone": "010-9008-5961",
        "last_4": "5961"
    },
    {
        "name": "여미진",
        "role": "조리실무사",
        "phone": "010-4856-3753",
        "last_4": "3753"
    },
    {
        "name": "이숙경",
        "role": "교사",
        "phone": "010-5523-7319",
        "last_4": "7319"
    },
    {
        "name": "민숙경",
        "role": "조리실무사",
        "phone": "010-2559-9916",
        "last_4": "9916"
    },
    {
        "name": "이유정",
        "role": "교사",
        "phone": "010-2875-3970",
        "last_4": "3970"
    },
    {
        "name": "정선자",
        "role": "조리실무사",
        "phone": "010-9042-1541",
        "last_4": "1541"
    },
    {
        "name": "이은샘",
        "role": "교사",
        "phone": "010-2528-4875",
        "last_4": "4875"
    },
    {
        "name": "김희영",
        "role": "조리실무사",
        "phone": "010-9806-4888",
        "last_4": "4888"
    },
    {
        "name": "이재호",
        "role": "교사",
        "phone": "010-5461-3561",
        "last_4": "3561"
    },
    {
        "name": "최나리",
        "role": "조리실무사",
        "phone": "010-9555-1667",
        "last_4": "1667"
    },
    {
        "name": "이지형",
        "role": "교사",
        "phone": "010-7145-9702",
        "last_4": "9702"
    },
    {
        "name": "최명성",
        "role": "조리실무사",
        "phone": "010-4602-2967",
        "last_4": "2967"
    },
    {
        "name": "이지희",
        "role": "교사",
        "phone": "010-2993-0543",
        "last_4": "0543"
    },
    {
        "name": "최준미",
        "role": "조리실무사",
        "phone": "010-8653-1391",
        "last_4": "1391"
    },
    {
        "name": "이해빈",
        "role": "교사",
        "phone": "010-4540-3991",
        "last_4": "3991"
    },
    {
        "name": "탁은숙",
        "role": "조리실무사",
        "phone": "010-6767-1343",
        "last_4": "1343"
    },
    {
        "name": "임선곤",
        "role": "교사",
        "phone": "010-4277-7333",
        "last_4": "7333"
    },
    {
        "name": "김원태",
        "role": "배움터지킴이",
        "phone": "010-2441-1706",
        "last_4": "1706"
    },
    {
        "name": "임언숙",
        "role": "교사",
        "phone": "010-6766-4806",
        "last_4": "4806"
    },
    {
        "name": "윤문경",
        "role": "기숙사생활지도원",
        "phone": "010-2088-0430",
        "last_4": "0430"
    },
    {
        "name": "정경훈",
        "role": "교사",
        "phone": "010-6276-7881",
        "last_4": "7881"
    },
    {
        "name": "강한샘",
        "role": "기숙사생활지도원",
        "phone": "010-8579-4730",
        "last_4": "4730"
    },
    {
        "name": "정순영",
        "role": "교사",
        "phone": "010-4612-3624",
        "last_4": "3624"
    },
    {
        "name": "김현인",
        "role": "기숙사환경미화원",
        "phone": "010-9900-6925",
        "last_4": "6925"
    },
    {
        "name": "정은영",
        "role": "교사",
        "phone": "010-5871-1825",
        "last_4": "1825"
    },
    {
        "name": "김덕순",
        "role": "기숙사환경미화원",
        "phone": "010-3257-0355",
        "last_4": "0355"
    },
    {
        "name": "정지연",
        "role": "교사",
        "phone": "010-7313-5034",
        "last_4": "5034"
    },
    {
        "name": "고태경",
        "role": "사회복무요원",
        "phone": "010-8954-2415",
        "last_4": "2415"
    },
    {
        "name": "정현재",
        "role": "교사",
        "phone": "010-4341-4609",
        "last_4": "4609"
    },
    {
        "name": "강민정",
        "role": "학교보건시간강사",
        "phone": "010-8732-9732",
        "last_4": "9732"
    }
];
    
    var rows = [];
    for (var i = 0; i < teachersData.length; i++) {
      var t = teachersData[i];
      // 교직원 초기 비밀번호(휴대폰 번호 뒷 4자리)를 SHA-256 해시값으로 단방향 암호화하여 저장
      var hashedPassword = getSHA256Hash(t.last_4);
      rows.push([t.name, t.role, t.phone, hashedPassword]);
    }
    
    if (rows.length > 0) {
      // 4열(비밀번호 뒷자리)을 텍스트 서식("@")으로 지정하여 0616 등의 앞자리 0 누락 방지
      sheetTeachers.getRange(2, 4, rows.length, 1).setNumberFormat("@");
      sheetTeachers.getRange(2, 1, rows.length, 4).setValues(rows);
    }
    sheetTeachers.setFrozenRows(1);
  }
  
  return "스프레드시트 DB 초기화가 성공적으로 완료되었습니다! (시트: 특별실_예약내역, 특별실_설정, 교직원_목록)";
}

/**
 * 초기 렌더링에 필요한 공통 데이터 획득 API (타임존 방지 및 성능 최적화 적용)
 */
function getInitialData() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    
    // 시트가 제대로 생성되었는지 검사 (없으면 초기화 실행)
    if (!ss.getSheetByName("교직원_목록") || !ss.getSheetByName("특별실_설정") || !ss.getSheetByName("특별실_예약내역")) {
      initSpreadsheet();
    }
    
    var sheetReservations = ss.getSheetByName("특별실_예약내역");
    var sheetSettings = ss.getSheetByName("특별실_설정");
    var sheetTeachers = ss.getSheetByName("교직원_목록");
    
    // 1. 예약 목록 로드 (getDisplayValues()를 사용하여 문자열 그대로 취득하고, 역순 루프로 탐색 성능 개선)
    var resRows = sheetReservations.getDataRange().getDisplayValues();
    var reservations = [];
    var nowLimit = new Date();
    nowLimit.setDate(nowLimit.getDate() - 7);
    nowLimit.setHours(0, 0, 0, 0);
    
    var futureLimit = new Date();
    futureLimit.setDate(futureLimit.getDate() + 28);
    futureLimit.setHours(23, 59, 59, 999);
    
    // 성능 최적화: 역순 루프를 돌려 최근 데이터 우선 처리
    for (var i = resRows.length - 1; i >= 1; i--) {
      var dateStr = resRows[i][1]; // YYYY-MM-DD
      if (!dateStr) continue;
      
      // 타임존 영향을 피하기 위해 문자열을 안전하게 날짜 객체로 파싱
      var parts = dateStr.split('-');
      if (parts.length === 3) {
        var year = parseInt(parts[0], 10);
        var month = parseInt(parts[1], 10) - 1;
        var day = parseInt(parts[2], 10);
        var rDate = new Date(year, month, day);
        
        if (rDate >= nowLimit && rDate <= futureLimit) {
          reservations.push({
            id: resRows[i][0],
            date: dateStr,
            period: resRows[i][2],
            room: resRows[i][3],
            name: resRows[i][4],
            targetClass: resRows[i][5],
            purpose: resRows[i][6],
            createdAt: resRows[i][7]
          });
        }
      }
    }
    
    // 2. 특별실 설정 목록 로드 (getDisplayValues() 사용)
    var roomRows = sheetSettings.getDataRange().getDisplayValues();
    var rooms = [];
    for (var i = 1; i < roomRows.length; i++) {
      rooms.push({
        name: roomRows[i][0],
        restricted: roomRows[i][1] === "Y",
        desc: roomRows[i][2]
      });
    }
    
    // 3. 교직원 이름 및 직위 목록 로드
    var teacherRows = sheetTeachers.getDataRange().getDisplayValues();
    var teachers = [];
    for (var i = 1; i < teacherRows.length; i++) {
      teachers.push({
        name: teacherRows[i][0],
        role: teacherRows[i][1]
      });
    }
    
    // 이름 가나다순 정렬
    teachers.sort(function(a, b) {
      return a.name.localeCompare(b.name, 'ko');
    });
    
    return {
      success: true,
      reservations: reservations,
      rooms: rooms,
      teachers: teachers
    };
  } catch (err) {
    return { success: false, error: err.toString() };
  }
}

/**
 * 교직원 본인 검증 API
 */
function verifyUser(name, password) {
  try {
    var cache = CacheService.getScriptCache();
    var attemptsKey = "LOGIN_ATTEMPTS_" + name;
    var attempts = cache.get(attemptsKey) ? parseInt(cache.get(attemptsKey), 10) : 0;
    
    if (attempts >= 5) {
      return { success: false, error: "비밀번호 5회 오류로 인해 10분간 로그인이 제한됩니다." };
    }

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheetTeachers = ss.getSheetByName("교직원_목록");
    var rows = sheetTeachers.getDataRange().getDisplayValues(); // getDisplayValues() 적용
    
    var trimmedPassword = password ? password.toString().trim() : "";
    if (!trimmedPassword) {
      return { success: false, error: "비밀번호를 입력해 주세요." };
    }
    
    var isUserExist = false;
    for (var i = 1; i < rows.length; i++) {
      var tName = rows[i][0].toString().trim();
      var tPass = rows[i][3].toString().trim();
      
      // 이름이 일치하는 경우 비밀번호 검증 진행
      if (tName === name) {
        isUserExist = true;
        var isMatch = false;
        
        if (tPass.length === 64) {
          // 64자리인 경우 SHA-256 해시 비교 (보안 고도화 버전)
          var hashedInput = getSHA256Hash(trimmedPassword);
          isMatch = (tPass === hashedInput);
        } else {
          // 그렇지 않은 경우 구글 시트에서 숫자 포맷팅으로 인해 0이 유실되었는지 검사 후 평문 대조 (하이브리드 호환성 유지)
          if (/^\d+$/.test(tPass) && tPass.length < 4) {
            tPass = ("0000" + tPass).slice(-4);
          }
          isMatch = (tPass === trimmedPassword);
        }
        
        if (isMatch) {
          cache.remove(attemptsKey); // 성공 시 카운트 초기화
          return { success: true, name: name, role: rows[i][1] };
        }
      }
    }
    
    if (isUserExist) {
      cache.put(attemptsKey, (attempts + 1).toString(), 600); // 10분(600초) 보관
      return { success: false, error: "비밀번호(휴대폰 번호 뒷 4자리)가 일치하지 않습니다. (오류 횟수: " + (attempts + 1) + "/5)" };
    }
    return { success: false, error: "교직원 목록에 등록되지 않은 성명입니다." };
  } catch (err) {
    return { success: false, error: err.toString() };
  }
}

/**
 * 신규 예약 추가 API (LockService를 이용한 동시성 제어 및 타임존 오류 방지, 다중 교시 및 반복 예약 지원)
 */
function addReservation(data) {
  // [Zero Trust] 서버 사이드 데이터 형식 및 길이 엄격 검증
  if (!data.name || data.name.length > 10) return { success: false, error: "예약자 이름의 길이가 비정상적입니다. (최대 10자)" };
  if (!data.targetClass || data.targetClass.length > 30) return { success: false, error: "사용 대상 학급의 길이가 비정상적입니다. (최대 30자)" };
  if (!data.purpose || data.purpose.length > 100) return { success: false, error: "사용 목적은 100자를 초과할 수 없습니다." };
  if (!data.date || !/^\d{4}-\d{2}-\d{2}$/.test(data.date)) return { success: false, error: "날짜 포맷 형식이 변조되었습니다. (YYYY-MM-DD)" };
  
  // [서버 사이드 XSS 방지] 시트 저장 전 특수문자 이스케이프 강제화
  data.name = escapeHtmlGS(data.name);
  data.targetClass = escapeHtmlGS(data.targetClass);
  data.purpose = escapeHtmlGS(data.purpose);

  var lock = LockService.getScriptLock();
  var lockAcquired = false;
  try {
    // 1. 동시성 제어: 스크립트 락 획득 시도 (최대 30초 대기)
    lock.waitLock(30000);
    lockAcquired = true;
    
    // 2. 본인 인증
    var auth = verifyUser(data.name, data.password);
    if (!auth.success) {
      return { success: false, error: "본인 인증에 실패하였습니다. 이름과 휴대폰 번호 뒷자리를 다시 확인해 주세요." };
    }
    
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    
    // 3. 예약 날짜 및 교시 범위 파싱
    var recurrenceWeeks = data.recurrenceWeeks ? parseInt(data.recurrenceWeeks, 10) : 1;
    var targetDates = getRecurrenceDates(data.date, recurrenceWeeks);
    
    var startPeriod = data.startPeriod || data.period;
    var endPeriod = data.endPeriod || data.period;
    var targetPeriods = getPeriodsInRange(startPeriod, endPeriod);
    if (targetPeriods.length === 0) {
      return { success: false, error: "선택하신 시작 교시 또는 종료 교시가 유효하지 않습니다." };
    }
    
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    
    // 4. 통합 유효성 검사 (모든 대상 날짜와 교시에 대하여)
    var globalBlockedPeriods = ["점심시간", "청소시간"];
    
    // 4.1 특별실별 특정 교시 제한 여부 확인
    var sheetSettings = ss.getSheetByName("특별실_설정");
    var roomRows = sheetSettings.getDataRange().getDisplayValues();
    var isRestrictedRoom = false;
    for (var i = 1; i < roomRows.length; i++) {
      if (roomRows[i][0] === data.room && roomRows[i][1] === "Y") {
        isRestrictedRoom = true;
        break;
      }
    }
    
    for (var dIdx = 0; dIdx < targetDates.length; dIdx++) {
      var dateStr = targetDates[dIdx];
      var parts = dateStr.split('-');
      var year = parseInt(parts[0], 10);
      var month = parseInt(parts[1], 10) - 1;
      var day = parseInt(parts[2], 10);
      var targetDate = new Date(year, month, day);
      targetDate.setHours(0, 0, 0, 0);
      
      var diffTime = targetDate.getTime() - today.getTime();
      var diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays < 0) {
        return { success: false, error: "과거 날짜(" + dateStr + ")에는 예약할 수 없습니다." };
      }
      if (diffDays > 28) {
        return { success: false, error: "예약은 오늘 기준으로 최대 28일(4주) 앞의 일정까지만 가능합니다. (" + dateStr + "은 범위 초과)" };
      }
      
      for (var pIdx = 0; pIdx < targetPeriods.length; pIdx++) {
        var periodStr = targetPeriods[pIdx];
        
        // 공통 시간제한 검사
        if (globalBlockedPeriods.indexOf(periodStr) !== -1) {
          return { success: false, error: periodStr + " 시간에는 특별실 예약이 불가합니다." };
        }
        
        // 특별실 교시제한 검사
        if (isRestrictedRoom) {
          var allowedPeriods = ["8교시(방과후)", "저녁시간", "야자 1교시", "야자 2교시"];
          if (allowedPeriods.indexOf(periodStr) === -1) {
            return { 
              success: false, 
              error: data.room + "은(는) 정규 수업 활용을 위해 8교시(방과후)부터만 예약이 가능합니다. (" + periodStr + "은 불가)" 
            };
          }
        }
      }
    }
    
    // 5. 중복 예약 여부 통합 검사
    var sheetReservations = ss.getSheetByName("특별실_예약내역");
    var resRows = sheetReservations.getDataRange().getDisplayValues();
    
    for (var dIdx = 0; dIdx < targetDates.length; dIdx++) {
      var dateStr = targetDates[dIdx];
      for (var pIdx = 0; pIdx < targetPeriods.length; pIdx++) {
        var periodStr = targetPeriods[pIdx];
        
        for (var i = 1; i < resRows.length; i++) {
          var rDateStr = resRows[i][1];
          var rPeriod = resRows[i][2];
          var rRoom = resRows[i][3];
          
          if (rDateStr === dateStr && rPeriod === periodStr && rRoom === data.room) {
            return { 
              success: false, 
              error: "이미 다른 선생님께서 [" + dateStr + "] [" + periodStr + "]에 [" + data.room + "]을(를) 예약하셨습니다. (예약자: " + resRows[i][4] + ")"
            };
          }
        }
      }
    }
    
    // 6. 예약 등록 진행 (모든 검사 통과 시)
    var reservationIdBase = "RESRV_" + new Date().getTime() + "_";
    var formattedTodayStr = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss");
    var insertedReservations = [];
    var lastRoomName = data.room;
    var rowsToAppend = [];
    
    for (var dIdx = 0; dIdx < targetDates.length; dIdx++) {
      var dateStr = targetDates[dIdx];
      for (var pIdx = 0; pIdx < targetPeriods.length; pIdx++) {
        var periodStr = targetPeriods[pIdx];
        var reservationId = reservationIdBase + dIdx + "_" + pIdx + "_" + Math.floor(Math.random() * 100000);
        
        rowsToAppend.push([
          reservationId,
          dateStr,
          periodStr,
          data.room,
          data.name,
          data.targetClass,
          data.purpose,
          formattedTodayStr
        ]);
        
        insertedReservations.push({
          id: reservationId,
          date: dateStr,
          period: periodStr,
          room: data.room,
          name: data.name,
          targetClass: data.targetClass,
          purpose: data.purpose,
          createdAt: formattedTodayStr
        });
      }
    }
    
    // [최적화] 대량 행 데이터를 setValues()로 일괄 삽입하여 실행 성능을 비약적으로 개선
    if (rowsToAppend.length > 0) {
      var lastRow = sheetReservations.getLastRow();
      sheetReservations.getRange(lastRow + 1, 1, rowsToAppend.length, rowsToAppend[0].length)
                       .setValues(rowsToAppend);
    }
    
    var successMsg = "[" + lastRoomName + "] 예약이 성공적으로 등록되었습니다. (총 " + insertedReservations.length + "개 슬롯)";
    return {
      success: true,
      message: successMsg,
      reservations: insertedReservations
    };
  } catch (err) {
    return { success: false, error: "예약 등록 도중 오류가 발생했습니다: " + err.toString() };
  } finally {
    // 7. 락 해제
    if (lockAcquired) {
      lock.releaseLock();
    }
  }
}

/**
 * 교시 범위를 배열로 획득하는 헬퍼 함수
 */
function getPeriodsInRange(startPeriod, endPeriod) {
  var reservablePeriods = ["1교시", "2교시", "3교시", "4교시", "5교시", "6교시", "7교시", "8교시(방과후)", "저녁시간", "야자 1교시", "야자 2교시"];
  var startIndex = reservablePeriods.indexOf(startPeriod);
  var endIndex = reservablePeriods.indexOf(endPeriod);
  if (startIndex === -1 || endIndex === -1 || startIndex > endIndex) {
    return []; // 범위를 찾지 못할 경우 유효성 검사에서 걸리도록 빈 배열 반환
  }
  return reservablePeriods.slice(startIndex, endIndex + 1);
}

/**
 * 주간 반복 날짜 리스트를 획득하는 헬퍼 함수
 */
function getRecurrenceDates(baseDateStr, recurrenceWeeks) {
  var dates = [];
  var parts = baseDateStr.split('-');
  var year = parseInt(parts[0], 10);
  var month = parseInt(parts[1], 10) - 1;
  var day = parseInt(parts[2], 10);
  
  for (var w = 0; w < recurrenceWeeks; w++) {
    var d = new Date(year, month, day + (w * 7));
    var yyyy = d.getFullYear();
    var mm = String(d.getMonth() + 1).padStart(2, '0');
    var dd = String(d.getDate()).padStart(2, '0');
    dates.push(yyyy + "-" + mm + "-" + dd);
  }
  return dates;
}

/**
 * 예약 삭제 API (LockService를 이용한 동시성 제어)
 */
function deleteReservation(reservationId, name, password) {
  // [Zero Trust] 입력값 길이 및 형식 유효성 검사
  if (!reservationId || reservationId.length > 50) return { success: false, error: "예약 ID 형식이 비정상적입니다." };
  if (!name || name.length > 10) return { success: false, error: "이름 형식이 비정상적입니다." };

  var lock = LockService.getScriptLock();
  var lockAcquired = false;
  try {
    // 1. 동시성 제어: 스크립트 락 획득 시도 (최대 30초 대기)
    lock.waitLock(30000);
    lockAcquired = true;
    
    // 2. 본인 인증
    var auth = verifyUser(name, password);
    if (!auth.success) {
      return { success: false, error: "본인 인증에 실패하였습니다. 성명과 휴대폰 뒷자리를 확인해 주세요." };
    }
    
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheetReservations = ss.getSheetByName("특별실_예약내역");
    var rows = sheetReservations.getDataRange().getDisplayValues(); // getDisplayValues() 적용
    
    var rowIndex = -1;
    for (var i = 1; i < rows.length; i++) {
      if (rows[i][0] === reservationId) {
        rowIndex = i + 1; // 1-based index for sheet
        
        // 3. 예약자 본인 일치 검증
        if (rows[i][4] !== name) {
          return { success: false, error: "타인의 예약은 취소할 수 없습니다. 본인이 등록한 예약만 취소 가능합니다." };
        }
        break;
      }
    }
    
    if (rowIndex === -1) {
      return { success: false, error: "존재하지 않는 예약이거나 이미 취소된 예약입니다." };
    }
    
    // 4. 행 삭제
    sheetReservations.deleteRow(rowIndex);
    
    return { success: true, message: "예약이 성공적으로 취소되었습니다." };
  } catch (err) {
    return { success: false, error: "예약 취소 도중 오류가 발생했습니다: " + err.toString() };
  } finally {
    // 5. 락 해제
    if (lockAcquired) {
      lock.releaseLock();
    }
  }
}

/**
 * 30일 이전의 과거 예약 데이터를 백업 시트로 이동하고 삭제하는 배치 함수
 */
function archiveOldReservations() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheetReservations = ss.getSheetByName("특별실_예약내역");
    if (!sheetReservations) return "특별실_예약내역 시트가 존재하지 않습니다.";
    
    var sheetBackup = ss.getSheetByName("특별실_예약내역_백업");
    if (!sheetBackup) {
      sheetBackup = ss.insertSheet("특별실_예약내역_백업");
      var headers = ["ID", "예약일자", "교시", "특별실", "예약자명", "대상학급", "사용목적", "등록일시", "백업일시"];
      sheetBackup.appendRow(headers);
      sheetBackup.getRange(1, 1, 1, headers.length)
                 .setFontWeight("bold")
                 .setBackground("#e2e8f0")
                 .setHorizontalAlignment("center");
      sheetBackup.setFrozenRows(1);
    }
    
    var rows = sheetReservations.getDataRange().getDisplayValues();
    if (rows.length <= 1) return "아카이빙할 데이터가 없습니다.";
    
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    
    var archiveLimit = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
    archiveLimit.setHours(23, 59, 59, 999);
    
    var archiveCount = 0;
    var formattedTodayStr = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss");
    
    // 행 인덱스 유지를 위해 아래에서부터 위로 탐색하며 삭제
    for (var i = rows.length - 1; i >= 1; i--) {
      var dateStr = rows[i][1];
      if (!dateStr) continue;
      
      var parts = dateStr.split('-');
      if (parts.length === 3) {
        var year = parseInt(parts[0], 10);
        var month = parseInt(parts[1], 10) - 1;
        var day = parseInt(parts[2], 10);
        var rDate = new Date(year, month, day);
        
        if (rDate <= archiveLimit) {
          // 백업 시트에 추가
          var backupRow = [
            rows[i][0], // ID
            rows[i][1], // 예약일자
            rows[i][2], // 교시
            rows[i][3], // 특별실
            rows[i][4], // 예약자명
            rows[i][5], // 대상학급
            rows[i][6], // 사용목적
            rows[i][7], // 등록일시
            formattedTodayStr // 백업일시
          ];
          sheetBackup.appendRow(backupRow);
          
          // 원본 시트에서 삭제
          sheetReservations.deleteRow(i + 1); // 1-based index
          archiveCount++;
        }
      }
    }
    
    return "성공적으로 " + archiveCount + "건의 예약을 아카이빙했습니다.";
  } catch (err) {
    return "아카이빙 중 오류 발생: " + err.toString();
  }
}

/**
 * SHA-256 해시를 생성하는 헬퍼 함수
 */
function getSHA256Hash(input) {
  var digest = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, input, Utilities.Charset.UTF_8);
  var hexString = "";
  for (var i = 0; i < digest.length; i++) {
    var byteValue = digest[i];
    if (byteValue < 0) byteValue += 256;
    var byteString = byteValue.toString(16);
    if (byteString.length == 1) byteString = "0" + byteString;
    hexString += byteString;
  }
  return hexString;
}

/**
 * 백엔드 XSS 공격 방어용 HTML 특수문자 변환 유틸리티
 */
function escapeHtmlGS(unsafe) {
  return (unsafe || "").toString()
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
