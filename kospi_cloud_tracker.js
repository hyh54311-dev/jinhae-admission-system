/**
 * KOSPI Daily Index & Investor Trend Cloud Tracker
 * Runs on Google Cloud (Google Apps Script).
 * PC가 완전히 꺼져 있어도 작동하며, 한국투자증권(KIS) OpenAPI 및 Daum 금융 API를 통해 수급 데이터를 안전하게 수집합니다.
 * 
 * [설치 및 등록 방법]
 * 1. 구글 앱스 스크립트(https://script.google.com)에 로그인 후 [새 프로젝트]를 생성합니다.
 * 2. 기존 코드를 모두 삭제하고 이 파일의 전체 코드를 복사하여 붙여넣습니다.
 * 3. 좌측 메뉴에서 [프로젝트 설정](톱니바퀴)을 클릭하고, [스크립트 속성]에 아래 값들을 추가합니다:
 *    - 속성명: TELEGRAM_TOKEN  /  값: 8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY
 *    - 속성명: TELEGRAM_CHAT_ID  /  값: 8518409134
 *    - 속성명: KIS_APP_KEY  /  값: PS2f8MYQli4WCOEbp4I2zvNwAu6tAJhQV0k2
 *    - 속성명: KIS_APP_SECRET  /  값: (로컬 .env의 KIS_APP_SECRET 값 입력)
 *    - 속성명: KIS_MOCK  /  값: False
 * 4. 상단 [저장] 아이콘을 클릭합니다.
 * 5. 좌측 메뉴의 [트리거](시계 아이콘)를 클릭하고 [트리거 추가]를 선택합니다.
 *    - 실행할 함수 선택: setDailyTriggers
 *    - 이벤트 소스 선택: 시간 기반
 *    - 시간 기반 트리거 유형 선택: 일일 타이머
 *    - 시간 선택: 오전 12시~오전 1시 사이 (매일 자정에 당일 실행용 정시 트리거를 동적으로 셋업합니다)
 * 6. 저장합니다. 이제 매 영업일 10:30 AM 및 15:30 PM 정시에 텔레그램으로 시황 보고서가 옵니다.
 */

// ----------------- 일회성 동적 트리거 관리 로직 ----------------- //

/**
 * 매일 자정~오전 1시 사이에 실행되어 당일 오전 10:30 및 오후 3:30에 정시 가동될 
 * 일회성 시간 트리거들을 셋업합니다. (토, 일요일은 자동 스킵)
 */
function setDailyTriggers() {
  // 기존에 남아있던 동적 단발성 트리거 정리
  deleteDynamicTriggers();
  
  var today = new Date();
  var dayOfWeek = today.getDay(); // 0: 일요일, 6: 토요일
  
  // 주말(토, 일)에는 코스피 개장이 없으므로 트리거 생성을 생략합니다.
  if (dayOfWeek === 0 || dayOfWeek === 6) {
    Logger.log("주말이므로 오늘의 트리거 설정을 스킵합니다.");
    return;
  }
  
  // 1. 오전 10:30 실행 트리거 예약
  var amTime = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 10, 30, 0);
  ScriptApp.newTrigger('sendAMReport')
           .timeBased()
           .at(amTime)
           .create();
  Logger.log("오전 10:30 트리거가 예약되었습니다: " + amTime.toString());
           
  // 2. 오후 15:30 실행 트리거 예약
  var pmTime = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 15, 30, 0);
  ScriptApp.newTrigger('sendPMReport')
           .timeBased()
           .at(pmTime)
           .create();
  Logger.log("오후 15:30 트리거가 예약되었습니다: " + pmTime.toString());
}

/**
 * 이전에 생성된 일회성 실행용 동적 트리거들을 모두 삭제합니다.
 */
function deleteDynamicTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    var handlerName = triggers[i].getHandlerFunction();
    if (handlerName === 'sendAMReport' || handlerName === 'sendPMReport') {
      ScriptApp.deleteTrigger(triggers[i]);
      Logger.log("이전 동적 트리거 삭제 완료: " + handlerName);
    }
  }
}

// ----------------- 트리거 대상 실행 함수 ----------------- //

function sendAMReport() {
  sendReport("오전 장중 (10:30)");
  deleteDynamicTriggersByHandler('sendAMReport');
}

function sendPMReport() {
  sendReport("오후 마감 (15:30)");
  deleteDynamicTriggersByHandler('sendPMReport');
}

function deleteDynamicTriggersByHandler(handlerName) {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === handlerName) {
      ScriptApp.deleteTrigger(triggers[i]);
      Logger.log("단일 동적 트리거 소멸 완료: " + handlerName);
    }
  }
}

// ----------------- KIS OpenAPI 연동 로직 ----------------- //

/**
 * KIS OpenAPI 토큰을 발급받습니다.
 */
function getKisAccessToken(appKey, appSecret, isMock) {
  var props = PropertiesService.getScriptProperties();
  var cachedToken = props.getProperty("KIS_ACCESS_TOKEN");
  var tokenTimeStr = props.getProperty("KIS_TOKEN_TIME");
  
  var now = new Date().getTime();
  if (cachedToken && tokenTimeStr) {
    var tokenTime = parseInt(tokenTimeStr, 10);
    // KIS 토큰은 24시간 동안 유효하므로, 23시간(82,800,000 ms) 이내이면 재사용
    if (now - tokenTime < 82800000) {
      Logger.log("캐시된 KIS 토큰을 재사용합니다.");
      return cachedToken;
    }
  }

  var baseUrl = isMock ? "https://openapivts.koreainvestment.com:29443" : "https://openapi.koreainvestment.com:9443";
  var url = baseUrl + "/oauth2/tokenP";
  
  var payload = {
    "grant_type": "client_credentials",
    "appkey": appKey,
    "appsecret": appSecret
  };
  
  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  var response = UrlFetchApp.fetch(url, options);
  var json = JSON.parse(response.getContentText());
  if (response.getResponseCode() === 200 && json.access_token) {
    props.setProperty("KIS_ACCESS_TOKEN", json.access_token);
    props.setProperty("KIS_TOKEN_TIME", now.toString());
    Logger.log("신규 KIS 토큰을 발급하고 캐시에 저장했습니다.");
    return json.access_token;
  } else {
    throw new Error("KIS 토큰 발급 실패: " + response.getContentText());
  }
}

/**
 * KIS OpenAPI를 통해 코스피 지수를 수집합니다.
 */
function getKospiIndexDataFromKis(token, appKey, appSecret, isMock) {
  var baseUrl = isMock ? "https://openapivts.koreainvestment.com:29443" : "https://openapi.koreainvestment.com:9443";
  var url = baseUrl + "/uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice";
  
  var today = new Date();
  var start = new Date();
  start.setDate(today.getDate() - 220); // Cover 120 trading days (approx. 6 months)
  
  var todayYmd = Utilities.formatDate(today, "GMT+9", "yyyyMMdd");
  var startYmd = Utilities.formatDate(start, "GMT+9", "yyyyMMdd");
  
  var queryParams = "?FID_COND_MRKT_DIV_CODE=U&FID_INPUT_ISCD=0001&FID_INPUT_DATE_1=" + startYmd + "&FID_INPUT_DATE_2=" + todayYmd + "&FID_PERIOD_DIV_CODE=D";
  
  var options = {
    "method": "get",
    "headers": {
      "authorization": "Bearer " + token,
      "appkey": appKey,
      "appsecret": appSecret,
      "tr_id": "FHKUP03500100"
    },
    "muteHttpExceptions": true
  };
  
  var response = UrlFetchApp.fetch(url + queryParams, options);
  var json = JSON.parse(response.getContentText());
  
  if (response.getResponseCode() !== 200 || json.rt_cd !== "0") {
    throw new Error("KIS 업종 기간별 시세 호출 실패: " + response.getContentText());
  }
  
  var output2 = json.output2;
  if (output2 && output2.length > 0) Logger.log("지수 API 원본: " + JSON.stringify(output2[0]));
  var indexRows = [];
  
  for (var i = 0; i < output2.length - 1; i++) {
    var row = output2[i];
    var prevRow = output2[i + 1]; // 어제 종가 데이터와 비교
    
    var dateRaw = row.stck_bsop_date; // YYYYMMDD
    var formattedDate = dateRaw.substring(0, 4) + "." + dateRaw.substring(4, 6) + "." + dateRaw.substring(6, 8);
    
    var todayClose = parseFloat(row.bstp_nmix_prpr);
    var yesterdayClose = parseFloat(prevRow.bstp_nmix_prpr);
    
    var changeVal = todayClose - yesterdayClose;
    var flucRateVal = (changeVal / yesterdayClose) * 100;
    
    var sign = changeVal > 0 ? "+" : "";
    
    indexRows.push({
      date: formattedDate,
      close: todayClose.toFixed(2),
      change: sign + changeVal.toFixed(2),
      fluc_rate: sign + flucRateVal.toFixed(2) + "%"
    });
  }
  
  return indexRows;
}

/**
 * KIS OpenAPI를 통해 투자자 일별 매매동향을 수집합니다.
 */
function getKospiInvestorDataFromKis(token, appKey, appSecret, isMock) {
  var baseUrl = isMock ? "https://openapivts.koreainvestment.com:29443" : "https://openapi.koreainvestment.com:9443";
  var url = baseUrl + "/uapi/domestic-stock/v1/quotations/inquire-investor-daily-by-market";
  
  var today = new Date();
  var start = new Date();
  start.setDate(today.getDate() - 220); // Cover 120 trading days
  
  var todayYmd = Utilities.formatDate(today, "GMT+9", "yyyyMMdd");
  var startYmd = Utilities.formatDate(start, "GMT+9", "yyyyMMdd");
  
  var queryParams = "?FID_COND_MRKT_DIV_CODE=U&FID_INPUT_ISCD=0001&FID_INPUT_ISCD_1=&FID_INPUT_ISCD_2=&FID_INPUT_DATE_1=" + todayYmd + "&FID_INPUT_DATE_2=" + startYmd + "&FID_PERIOD_DIV_CODE=D";
  
  var options = {
    "method": "get",
    "headers": {
      "authorization": "Bearer " + token,
      "appkey": appKey,
      "appsecret": appSecret,
      "tr_id": "FHPTJ04040000",
      "custtype": "P"
    },
    "muteHttpExceptions": true
  };
  
  var response = UrlFetchApp.fetch(url + queryParams, options);
  var json = JSON.parse(response.getContentText());
  
  if (response.getResponseCode() !== 200 || json.rt_cd !== "0") {
    throw new Error("KIS 투자자 일별 매매동향 호출 실패: " + response.getContentText());
  }
  
  var output = json.output;
  if (output && output.length > 0) Logger.log("수급 API 원본: " + JSON.stringify(output[0]));
  var investorRows = [];
  
  for (var i = 0; i < output.length; i++) {
    var row = output[i];
    var dateRaw = row.stck_bsop_date;
    var formattedDate = dateRaw.substring(0, 4) + "." + dateRaw.substring(4, 6) + "." + dateRaw.substring(6, 8);
    
    // KIS 업종별 순매수금액 단위: 백만 원 -> 억 원 단위 변환을 위해 100으로 나눔
    function parseKisAmt(val) {
      if (!val) return 0;
      var num = parseFloat(val);
      return isNaN(num) ? 0 : Math.round(num / 100); // 백만원 -> 억원 변환
    }
    
    investorRows.push({
      date: formattedDate,
      individual: parseKisAmt(row.prsn_ntby_tr_pbmn),
      foreigner: parseKisAmt(row.frgn_ntby_tr_pbmn),
      institution: parseKisAmt(row.orgn_ntby_tr_pbmn),
      fin_inv: parseKisAmt(row.scrt_ntby_tr_pbmn), // 증권(금융투자)
      insurance: parseKisAmt(row.insu_ntby_tr_pbmn), // 보험
      inv_trust: parseKisAmt(row.fund_ntby_tr_pbmn), // 투신
      bank: parseKisAmt(row.bank_ntby_tr_pbmn), // 은행
      other_fin: parseKisAmt(row.ivtr_ntby_tr_pbmn), // 기타금융
      pension: parseKisAmt(row.etc_orgt_ntby_tr_pbmn), // 기타기관(연기금 대용)
      other_corp: parseKisAmt(row.etc_corp_ntby_tr_pbmn) // 기타법인
    });
  }
  
  // 내림차순 정렬 (최근 날짜가 앞부분에 오도록)
  investorRows.sort(function(a, b) {
    return b.date.localeCompare(a.date);
  });
  
  if (investorRows.length > 0) {
    Logger.log("정렬 후 최신 수급 데이터 샘플 (첫 3개): " + JSON.stringify(investorRows.slice(0, 3)));
  }
  
  return investorRows;
}

// ----------------- 다음 금융 (Daum Finance) API 연동 로직 ----------------- //

/**
 * 다음 금융에서 코스피 투자자 일자별 매매동향을 가져옵니다.
 */
function getKospiInvestorDataFromDaum() {
  var mainUrl = "https://finance.daum.net/domestic/investors";
  var headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
  };
  
  // 1. 쿠키를 받아오기 위해 먼저 메인 페이지 호출
  var preResponse = UrlFetchApp.fetch(mainUrl, {
    "headers": headers,
    "muteHttpExceptions": true
  });
  
  var cookieHeader = "";
  var headersAll = preResponse.getAllHeaders();
  if (headersAll["Set-Cookie"]) {
    var cookies = headersAll["Set-Cookie"];
    if (Array.isArray(cookies)) {
      cookieHeader = cookies.map(function(c) { return c.split(';')[0]; }).join('; ');
    } else {
      cookieHeader = cookies.split(';')[0];
    }
  }
  
  // 2. 획득한 쿠키를 헤더에 얹어 API 호출
  var url = "https://finance.daum.net/api/investor/days?symbolCode=U001&page=1&perPage=30";
  var apiHeaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": mainUrl
  };
  if (cookieHeader) {
    apiHeaders["Cookie"] = cookieHeader;
  }
  
  var response = UrlFetchApp.fetch(url, {
    "headers": apiHeaders,
    "muteHttpExceptions": true
  });
  
  if (response.getResponseCode() !== 200) {
    throw new Error("Daum Finance API 호출 실패: " + response.getResponseCode());
  }
  
  var json = JSON.parse(response.getContentText());
  var list = json.data || json.output || json;
  if (!list || !Array.isArray(list) || list.length === 0) {
    throw new Error("Daum Finance 데이터 형식이 올바르지 않습니다.");
  }
  
  var investorRows = [];
  for (var i = 0; i < list.length; i++) {
    var item = list[i];
    
    var rawDate = item.date || item.datetime || "";
    var formattedDate = "";
    if (rawDate) {
      var match = rawDate.match(/^(\d{4})[-.](\d{2})[-.](\d{2})/);
      if (match) {
        formattedDate = match[1] + "." + match[2] + "." + match[3];
      }
    }
    if (!formattedDate) continue;
    
    var ind = item.individualNetPurchase !== undefined ? item.individualNetPurchase : (item.individualNetBuy !== undefined ? item.individualNetBuy : item.individual);
    var frg = item.foreignerNetPurchase !== undefined ? item.foreignerNetPurchase : (item.foreignerNetBuy !== undefined ? item.foreignerNetBuy : item.foreigner);
    var inst = item.institutionNetPurchase !== undefined ? item.institutionNetPurchase : (item.institutionNetBuy !== undefined ? item.institutionNetBuy : item.institution);
    
    var fin = item.financialNetPurchase !== undefined ? item.financialNetPurchase : (item.financialNetBuy !== undefined ? item.financialNetBuy : item.financial);
    var ins = item.insuranceNetPurchase !== undefined ? item.insuranceNetPurchase : (item.insuranceNetBuy !== undefined ? item.insuranceNetBuy : item.insurance);
    var tru = item.trustNetPurchase !== undefined ? item.trustNetPurchase : (item.trustNetBuy !== undefined ? item.trustNetBuy : item.trust);
    var bnk = item.bankNetPurchase !== undefined ? item.bankNetPurchase : (item.bankNetBuy !== undefined ? item.bankNetBuy : item.bank);
    var pen = item.pensionNetPurchase !== undefined ? item.pensionNetPurchase : (item.pensionNetBuy !== undefined ? item.pensionNetBuy : item.pension);
    var etcC = item.etcCorpNetPurchase !== undefined ? item.etcCorpNetPurchase : (item.etcCorpNetBuy !== undefined ? item.etcCorpNetBuy : item.etcCorp);
    var etcF = item.etcFinNetPurchase !== undefined ? item.etcFinNetPurchase : (item.etcFinNetBuy !== undefined ? item.etcFinNetBuy : item.etcFin);
    
    ind = ind ? parseFloat(ind) : 0;
    frg = frg ? parseFloat(frg) : 0;
    inst = inst ? parseFloat(inst) : 0;
    fin = fin ? parseFloat(fin) : 0;
    ins = ins ? parseFloat(ins) : 0;
    tru = tru ? parseFloat(tru) : 0;
    bnk = bnk ? parseFloat(bnk) : 0;
    pen = pen ? parseFloat(pen) : 0;
    etcC = etcC ? parseFloat(etcC) : 0;
    etcF = etcF ? parseFloat(etcF) : 0;
    
    investorRows.push({
      date: formattedDate,
      individual: ind,
      foreigner: frg,
      institution: inst,
      fin_inv: fin,
      insurance: ins,
      inv_trust: tru,
      bank: bnk,
      pension: pen,
      other_corp: etcC,
      other_fin: etcF
    });
  }
  
  // 수급 금액 단위 동적 감지 및 변환
  var sumAbs = 0;
  var countValid = 0;
  for (var j = 0; j < investorRows.length; j++) {
    var val = Math.abs(investorRows[j].foreigner);
    if (val > 0) {
      sumAbs += val;
      countValid++;
    }
  }
  var avgAbs = countValid > 0 ? sumAbs / countValid : 0;
  var divisor = 1;
  if (avgAbs > 10000000) {
    divisor = 100000000; // 원 -> 억원
  } else if (avgAbs > 100) {
    divisor = 100; // 백만원 -> 억원
  }
  
  if (divisor > 1) {
    for (var k = 0; k < investorRows.length; k++) {
      var row = investorRows[k];
      row.individual = Math.round(row.individual / divisor);
      row.foreigner = Math.round(row.foreigner / divisor);
      row.institution = Math.round(row.institution / divisor);
      row.fin_inv = Math.round(row.fin_inv / divisor);
      row.insurance = Math.round(row.insurance / divisor);
      row.inv_trust = Math.round(row.inv_trust / divisor);
      row.bank = Math.round(row.bank / divisor);
      row.pension = Math.round(row.pension / divisor);
      row.other_corp = Math.round(row.other_corp / divisor);
      row.other_fin = Math.round(row.other_fin / divisor);
    }
  }
  
  return investorRows;
}

// ----------------- 하이브리드 진입점 ----------------- //

/**
 * 코스피 지수를 다중 채널(KIS -> 네이버)로 안전하게 수집합니다.
 */
function getKospiIndexData(token, appKey, appSecret, isMock) {
  if (token && appKey && appSecret) {
    try {
      Logger.log("KIS OpenAPI를 통해 코스피 지수를 수집합니다.");
      return getKospiIndexDataFromKis(token, appKey, appSecret, isMock);
    } catch (e) {
      Logger.log("KIS OpenAPI 코스피 지수 수집 실패, 네이버 금융으로 폴백합니다. 에러: " + e.toString());
    }
  }
  
  return getKospiIndexDataFromNaver();
}

/**
 * 코스피 투자자 수급 데이터를 다중 채널(KIS -> 다음 -> 네이버)로 안전하게 수집합니다.
 */
function getKospiInvestorData(token, appKey, appSecret, isMock) {
  if (token && appKey && appSecret) {
    try {
      Logger.log("KIS OpenAPI를 통해 코스피 투자자 수급 데이터를 수집합니다.");
      var kisData = getKospiInvestorDataFromKis(token, appKey, appSecret, isMock);
      if (kisData && kisData.length > 0) {
        var first = kisData[0];
        if (first.individual === 0 && first.foreigner === 0 && first.institution === 0) {
          throw new Error("KIS OpenAPI에서 반환한 수급 수치가 모두 0입니다.");
        }
        return kisData;
      }
    } catch (e) {
      Logger.log("KIS OpenAPI 코스피 수급 수집 실패 또는 데이터 0 수신, 다음 금융으로 폴백합니다. 에러: " + e.toString());
    }
  }
  
  try {
    Logger.log("다음 금융 API를 통해 코스피 투자자 수급 데이터를 수집합니다.");
    return getKospiInvestorDataFromDaum();
  } catch (e) {
    Logger.log("다음 금융 수급 수집 실패, 네이버 금융으로 폴백합니다. 에러: " + e.toString());
  }
  
  return getKospiInvestorDataFromNaver();
}

// ----------------- 네이버 금융 (Naver Finance) Fallback 스크래퍼 ----------------- //

/**
 * 네이버 금융에서 일별 코스피 지수를 스크래핑합니다. (EUC-KR 디코딩 적용)
 */
function getKospiIndexDataFromNaver() {
  var url = "https://finance.naver.com/sise/sise_index_day.nhn?code=KOSPI&page=1";
  var response = UrlFetchApp.fetch(url, {
    "headers": {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
      "Referer": "https://finance.naver.com/"
    },
    "muteHttpExceptions": true
  });
  
  var htmlContent = response.getContentText("EUC-KR");
  var trRegex = /<tr[^>]*>([\s\S]*?)<\/tr>/gi;
  var tdRegex = /<td[^>]*>([\s\S]*?)<\/td>/gi;
  var match;
  var indexRows = [];
  
  while ((match = trRegex.exec(htmlContent)) !== null) {
    var trHtml = match[1];
    var tdMatch;
    var tds = [];
    tdRegex.lastIndex = 0;
    
    while ((tdMatch = tdRegex.exec(trHtml)) !== null) {
      tds.push(tdMatch[1].replace(/<[^>]*>/g, "").trim());
    }
    
    if (tds.length >= 4) {
      var dateText = tds[0];
      if (/^\d{4}\.\d{2}\.\d{2}$/.test(dateText) || /^\d{2}\.\d{2}\.\d{2}$/.test(dateText)) {
        if (dateText.length === 8) dateText = "20" + dateText;
        
        var close = tds[1];
        var changeVal = tds[2];
        var flucVal = tds[3];
        
        var cleanChange = changeVal.replace(/[▲▼상승하락]/g, "").trim();
        var sign = "";
        if (flucVal.indexOf("-") !== -1) {
          sign = "-";
        } else if (flucVal.indexOf("+") !== -1) {
          sign = "+";
        }
        
        indexRows.push({
          date: dateText,
          close: close,
          change: sign + cleanChange,
          fluc_rate: flucVal
        });
      }
    }
  }
  
  if (indexRows.length === 0) {
    throw new Error("네이버 코스피 지수 데이터 수집 실패");
  }
  return indexRows;
}

/**
 * 네이버 금융에서 투자자별 순매수/순매도 대금을 페이지 1, 2에 걸쳐 스크래핑합니다. (EUC-KR 디코딩 적용)
 */
function getKospiInvestorDataFromNaver() {
  var dataRows = [];
  for (var page = 1; page <= 2; page++) {
    var url = "https://finance.naver.com/sise/investorDealTrendDay.nhn?sosok=0&page=" + page;
    try {
      var response = UrlFetchApp.fetch(url, {
        "headers": {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
          "Referer": "https://finance.naver.com/"
        },
        "muteHttpExceptions": true
      });
      
      var code = response.getResponseCode();
      if (code !== 200) {
        Logger.log("네이버 페이지 " + page + " 수집 실패 (응답 코드: " + code + ")");
        continue;
      }
      
      var htmlContent = response.getContentText("EUC-KR");
      var trRegex = /<tr[^>]*>([\s\S]*?)<\/tr>/gi;
      var tdRegex = /<td[^>]*>([\s\S]*?)<\/td>/gi;
      var match;
      
      while ((match = trRegex.exec(htmlContent)) !== null) {
        var trHtml = match[1];
        var tdMatch;
        var tds = [];
        tdRegex.lastIndex = 0;
        
        while ((tdMatch = tdRegex.exec(trHtml)) !== null) {
          tds.push(tdMatch[1].replace(/<[^>]*>/g, "").trim());
        }
        
        if (tds.length >= 11) {
          var dateText = tds[0];
          if (/^\d{4}\.\d{2}\.\d{2}$/.test(dateText) || /^\d{2}\.\d{2}\.\d{2}$/.test(dateText)) {
            if (dateText.length === 8) dateText = "20" + dateText;
            
            dataRows.push({
              date: dateText,
              individual: parseIntSafe(tds[1]),
              foreigner: parseIntSafe(tds[2]),
              institution: parseIntSafe(tds[3]),
              fin_inv: parseIntSafe(tds[4]),
              insurance: parseIntSafe(tds[5]),
              inv_trust: parseIntSafe(tds[6]),
              bank: parseIntSafe(tds[7]),
              other_fin: parseIntSafe(tds[8]),
              pension: parseIntSafe(tds[9]),
              other_corp: parseIntSafe(tds[10])
            });
          }
        }
      }
    } catch (err) {
      Logger.log("네이버 페이지 " + page + " 통신 오류: " + err.toString());
    }
    
    Utilities.sleep(100);
  }
  
  if (dataRows.length === 0) {
    throw new Error("네이버 투자자별 수급 데이터 수집 실패");
  }
  
  var uniqueRows = [];
  var seenDates = {};
  for (var i = 0; i < dataRows.length; i++) {
    var row = dataRows[i];
    if (!seenDates[row.date]) {
      seenDates[row.date] = true;
      uniqueRows.push(row);
    }
  }
  
  uniqueRows.sort(function(a, b) {
    return b.date.localeCompare(a.date);
  });
  
  return uniqueRows;
}

// ----------------- 데이터 분석 및 파싱 보조 함수 ----------------- //

function parseIntSafe(val) {
  if (!val) return 0;
  var cleaned = val.replace(/,/g, "").replace(/\+/g, "").trim();
  var num = parseInt(cleaned, 10);
  return isNaN(num) ? 0 : num;
}

function formatAmount(val) {
  var sign = val > 0 ? "+" : "";
  var formatted = Math.abs(val).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return sign + formatted + "억";
}

function analyzeCumulativeTrend(dataList, numDays) {
  var subList = dataList.slice(0, numDays);
  if (subList.length === 0) {
    return null;
  }
  
  var sumIndividual = 0;
  var sumForeigner = 0;
  var sumInstitution = 0;
  
  for (var i = 0; i < subList.length; i++) {
    var row = subList[i];
    sumIndividual += row.individual;
    sumForeigner += row.foreigner;
    sumInstitution += row.institution;
  }
  
  return {
    individual: sumIndividual,
    foreigner: sumForeigner,
    institution: sumInstitution,
    total_days: subList.length
  };
}

function htmlEscape(str) {
  if (!str) return "";
  return str.toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
}

// ----------------- 핵심 수급 정제 및 텔레그램 메시지 송출 프로세스 ----------------- //

function sendReport(timeLabel) {
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty("TELEGRAM_TOKEN");
  var chatId = props.getProperty("TELEGRAM_CHAT_ID");
  
  if (!token || !chatId) {
    throw new Error("텔레그램 토큰 또는 Chat ID가 스크립트 속성에 등록되어 있지 않습니다.");
  }
  
  var appKey = props.getProperty("KIS_APP_KEY");
  var appSecret = props.getProperty("KIS_APP_SECRET");
  var isMock = props.getProperty("KIS_MOCK") === "True";
  
  var kisToken = null;
  if (appKey && appSecret) {
    try {
      kisToken = getKisAccessToken(appKey, appSecret, isMock);
      Logger.log("KIS OpenAPI 액세스 토큰 획득 성공");
    } catch (e) {
      Logger.log("KIS OpenAPI 액세스 토큰 획득 실패 (폴백 가동): " + e.toString());
    }
  }
  
  // 1. 지수 데이터 수집
  var indexHistory;
  try {
    indexHistory = getKospiIndexData(kisToken, appKey, appSecret, isMock);
  } catch (e) {
    Logger.log("지수 데이터 수집 실패: " + e.toString());
    indexHistory = null;
  }
  
  // 2. 수급 데이터 수집
  var investorList;
  try {
    investorList = getKospiInvestorData(kisToken, appKey, appSecret, isMock);
  } catch (e) {
    Logger.log("수급 데이터 수집 실패: " + e.toString());
    investorList = null;
  }
  
  if (!indexHistory) {
    throw new Error("코스피 지수 데이터를 수집할 수 없어 메시지를 발송하지 않습니다.");
  }
  
  var latestIndex = indexHistory[0];
  var reportDate = latestIndex.date;
  
  var today = new Date();
  var todayYmd = Utilities.formatDate(today, Session.getScriptTimeZone(), "yyyy.MM.dd");
  var isTodayTrading = (reportDate === todayYmd);
  
  if (!isTodayTrading && timeLabel.indexOf("테스트") === -1) {
    Logger.log("오늘(" + todayYmd + ")은 개장일이 아닙니다 (최근 거래일: " + reportDate + "). 알림 전송 없이 종료합니다.");
    return;
  }
  
  var dateDisplay = reportDate + " " + timeLabel;
  if (!isTodayTrading) {
    dateDisplay = reportDate + " (최근 거래일 마감)";
  }
  
  var escTimeLabel = htmlEscape(timeLabel);
  var escDateDisplay = htmlEscape(dateDisplay);
  var escClose = htmlEscape(latestIndex.close);
  var escChange = htmlEscape(latestIndex.change);
  var escFluc = htmlEscape(latestIndex.fluc_rate);
  
  var msgLines = [
    "📊 <b>[코스피 " + escTimeLabel + "]</b> (" + escDateDisplay + ")",
    "• 지수: <b>" + escClose + "</b> (" + escChange + ", " + escFluc + ")",
    ""
  ];
  
  if (investorList && investorList.length > 0) {
    var latestInvestor = investorList[0];
    var trend30 = analyzeCumulativeTrend(investorList, 30);
    var trend120 = analyzeCumulativeTrend(investorList, 120);
    
    var instDetails = [];
    if (latestInvestor.fin_inv !== 0) instDetails.push("금투 " + formatAmount(latestInvestor.fin_inv));
    if (latestInvestor.pension !== 0) instDetails.push("연기금 " + formatAmount(latestInvestor.pension));
    if (latestInvestor.inv_trust !== 0) instDetails.push("투신 " + formatAmount(latestInvestor.inv_trust));
    var instDetailStr = instDetails.length > 0 ? " (" + instDetails.join(" / ") + ")" : "";
    
    msgLines.push("👥 <b>투자자 순매매</b> (억 원)");
    msgLines.push("• 개인: <code>" + formatAmount(latestInvestor.individual) + "</code>");
    msgLines.push("• 외국인: <code>" + formatAmount(latestInvestor.foreigner) + "</code>");
    msgLines.push("• 기관: <code>" + formatAmount(latestInvestor.institution) + "</code>" + instDetailStr);
    msgLines.push("");
    
    if (trend30 && trend120) {
      msgLines.push("📅 <b>기간별 누적 매매동향</b>");
      msgLines.push("• 1달(30일): 개인 <code>" + formatAmount(trend30.individual) + "</code> | 외인 <code>" + formatAmount(trend30.foreigner) + "</code> | 기관 <code>" + formatAmount(trend30.institution) + "</code>");
      msgLines.push("• 6개월(120일): 개인 <code>" + formatAmount(trend120.individual) + "</code> | 외인 <code>" + formatAmount(trend120.foreigner) + "</code> | 기관 <code>" + formatAmount(trend120.institution) + "</code>");
      msgLines.push("");
    }
    
    // 요약 분석 작성
    var analysis = [];
    var indVal = latestInvestor.individual;
    var frgVal = latestInvestor.foreigner;
    var instVal = latestInvestor.institution;
    
    if (frgVal > 0 && instVal > 0) {
      analysis.push("외인/기관 쌍끌이 매수세 지수 견인.");
    } else if (frgVal < 0 && instVal < 0) {
      analysis.push("외인/기관 동반 순매도세 수급 압박.");
    } else if (frgVal > 0) {
      analysis.push("기관 매도 속 외인 순매수 지수 방어.");
    } else if (instVal > 0) {
      analysis.push("외인 매도 속 기관 순매수 지수 지탱.");
    }
    
    if (Math.abs(indVal) > Math.abs(frgVal) && Math.abs(indVal) > Math.abs(instVal) && indVal > 0) {
      analysis.push("개인 순매수세로 시장 주도.");
    }
    if (analysis.length === 0) {
      analysis.push("투자자별 관망세로 수급 분산.");
    }
    msgLines.push("💡 <b>요약:</b> " + analysis.join(" "));
  } else {
    // 수급 데이터 조회 실패 경고 추가
    msgLines.push("⚠️ <b>[경고] 수급 데이터 수집 실패</b>");
    msgLines.push("네이버 및 다음 금융 스크래핑이 차단되었습니다.");
    msgLines.push("안정적인 수집을 위해 [스크립트 속성]에 한국투자증권 API 키(KIS_APP_KEY, KIS_APP_SECRET)를 입력해 주세요.");
  }
  
  var telegramMsg = msgLines.join("\n");
  Logger.log("전송할 텔레그램 메시지:\n" + telegramMsg);
  
  // 텔레그램 API 송출
  var telegramUrl = "https://api.telegram.org/bot" + token + "/sendMessage";
  var payload = {
    "chat_id": chatId,
    "text": telegramMsg,
    "parse_mode": "HTML"
  };
  
  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  var response = UrlFetchApp.fetch(telegramUrl, options);
  if (response.getResponseCode() !== 200) {
    throw new Error("텔레그램 발송 오류: " + response.getContentText());
  }
}

/**
 * 수동 실행용 테스트 함수
 * Apps Script 콘솔에서 이 함수를 선택하고 [실행]을 누르면 즉시 수집 후 발송을 수행합니다.
 */
function test_run() {
  sendReport("수동 테스트");
}

/**
 * 수급 데이터 파싱 진단을 위한 디버그 함수
 */
function run_debug() {
  Logger.log("=== [DEBUG] KIS 및 공공 데이터 소스 진단 ===");
  var props = PropertiesService.getScriptProperties();
  var appKey = props.getProperty("KIS_APP_KEY");
  var appSecret = props.getProperty("KIS_APP_SECRET");
  Logger.log("KIS_APP_KEY 존재 여부: " + (appKey ? "True" : "False"));
  Logger.log("KIS_APP_SECRET 존재 여부: " + (appSecret ? "True" : "False"));
  
  // 1. 다음 금융 테스트
  try {
    var daumData = getKospiInvestorDataFromDaum();
    Logger.log("다음 금융 수집 성공! 데이터 개수: " + daumData.length);
    Logger.log("최근 데이터 샘플: " + JSON.stringify(daumData[0]));
  } catch (e) {
    Logger.log("다음 금융 수집 실패: " + e.toString());
  }
  
  // 2. KIS 테스트 (키가 있는 경우)
  if (appKey && appSecret) {
    try {
      var token = getKisAccessToken(appKey, appSecret, false);
      Logger.log("KIS 토큰 발급 성공!");
      var indexKis = getKospiIndexDataFromKis(token, appKey, appSecret, false);
      Logger.log("KIS 코스피 지수 수집 성공! 데이터 개수: " + indexKis.length);
      var investorKis = getKospiInvestorDataFromKis(token, appKey, appSecret, false);
      Logger.log("KIS 투자자 수급 수집 성공! 데이터 개수: " + investorKis.length);
    } catch (e) {
      Logger.log("KIS OpenAPI 디버그 실패: " + e.toString());
    }
  }
}

/**
 * KIS 토큰 캐시 진단 및 강제 갱신 테스트 함수
 * 필요 시 Apps Script 콘솔에서 실행하여 캐시 작동 여부를 확인할 수 있습니다.
 */
function clearAndDebugKis() {
  Logger.log("=== KIS 토큰 캐시 및 API 진단 시작 ===");
  var props = PropertiesService.getScriptProperties();
  
  // 1. 기존 캐시 토큰 확인
  var oldToken = props.getProperty("KIS_ACCESS_TOKEN");
  var oldTime = props.getProperty("KIS_TOKEN_TIME");
  Logger.log("기존 캐시 토큰 존재 여부: " + (oldToken ? "True" : "False"));
  Logger.log("기존 캐시 시간 기록: " + oldTime);
  
  // 2. 강제 캐시 초기화
  props.deleteProperty("KIS_ACCESS_TOKEN");
  props.deleteProperty("KIS_TOKEN_TIME");
  Logger.log("기존 캐시를 비웠습니다.");
  
  // 3. 신규 토큰 발급 테스트 (신규 발급 로그가 찍혀야 함)
  var appKey = props.getProperty("KIS_APP_KEY");
  var appSecret = props.getProperty("KIS_APP_SECRET");
  var isMock = props.getProperty("KIS_MOCK") === "True";
  
  if (!appKey || !appSecret) {
    Logger.log("[오류] 스크립트 속성에 KIS_APP_KEY 또는 KIS_APP_SECRET이 등록되어 있지 않습니다.");
    return;
  }
  
  try {
    var token1 = getKisAccessToken(appKey, appSecret, isMock);
    Logger.log("1차 요청 결과: 토큰 발급 성공!");
    
    // 4. 캐시 작동 테스트 (이번에는 '캐시된 KIS 토큰을 재사용합니다.' 로그가 찍혀야 함)
    var token2 = getKisAccessToken(appKey, appSecret, isMock);
    Logger.log("2차 요청 결과: 토큰 캐시 재사용 성공! (두 토큰이 동일함: " + (token1 === token2) + ")");
  } catch (e) {
    Logger.log("에러 발생: " + e.toString());
  }
}

