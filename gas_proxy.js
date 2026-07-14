/**
 * Standalone GAS Proxy for School Firewall Bypass & Naver Block Resolution
 * 
 * [배포 방법]
 * 1. 구글 앱스 스크립트(https://script.google.com)로 이동하여 새 프로젝트를 만듭니다.
 * 2. 기존 코드를 모두 지우고 이 코드를 붙여넣습니다.
 * 3. 좌측 메뉴에서 [프로젝트 설정](톱니바퀴)을 클릭하고, [스크립트 속성]에 아래 두 값을 추가합니다 (KIS OpenAPI 사용 시):
 *    - 속성명: KIS_APP_KEY  /  값: PS2f8MYQli4WCOEbp4I2zvNwAu6tAJhQV0k2
 *    - 속성명: KIS_APP_SECRET  /  값: (로컬 .env의 KIS_APP_SECRET 값 입력)
 *    - 속성명: KIS_MOCK  /  값: False
 * 4. 상단 메뉴에서 [배포] -> [새 배포]를 선택합니다.
 * 5. 유형 선택(톱니바퀴)에서 [웹 앱]을 클릭합니다.
 * 6. 다음과 같이 설정합니다:
 *    - 설명: KOSPI Tracker Proxy
 *    - 다음 사용자 권한으로 실행: 나 (Me)
 *    - 액세스할 수 있는 사용자: 모든 사용자 (Anyone) -> 필수 설정
 * 7. [배포] 버튼을 누르고 생성된 [웹 앱 URL]을 복사하여 PC의 `.env` 파일에 `GAS_PROXY_URL=...` 형태로 입력합니다.
 */

function doGet(e) {
  var url = e.parameter.url;
  if (!url) {
    return ContentService.createTextOutput(JSON.stringify({error: "Missing 'url' parameter"}))
                         .setMimeType(ContentService.MimeType.JSON);
  }
  
  try {
    if (url === "KOSPI_INVESTOR_MULTIPLE") {
      var investorData = [];
      var success = false;
      
      // 1. KIS OpenAPI 시도
      var props = PropertiesService.getScriptProperties();
      var appKey = props.getProperty("KIS_APP_KEY");
      var appSecret = props.getProperty("KIS_APP_SECRET");
      var isMock = props.getProperty("KIS_MOCK") === "True";
      
      if (appKey && appSecret) {
        try {
          var token = getKisAccessToken(appKey, appSecret, isMock);
          investorData = getKospiInvestorDataFromKis(token, appKey, appSecret, isMock);
          success = true;
          Logger.log("Proxy: KIS OpenAPI를 통해 수급 데이터를 변환했습니다.");
        } catch(err) {
          Logger.log("Proxy: KIS OpenAPI 실패, 다음 금융으로 이동. 에러: " + err.toString());
        }
      }
      
      // 2. KIS 실패 시 다음 금융 시도
      if (!success) {
        try {
          investorData = getKospiInvestorDataFromDaum();
          success = true;
          Logger.log("Proxy: 다음 금융 API를 통해 수급 데이터를 변환했습니다.");
        } catch(err) {
          Logger.log("Proxy: 다음 금융 실패, 네이버 금융 크롤링 시도. 에러: " + err.toString());
        }
      }
      
      // 3. KIS 및 다음 금융 성공 시 Naver 호환 HTML 테이블 생성
      if (success && investorData.length > 0) {
        var html = "<html><body><table>";
        for (var i = 0; i < investorData.length; i++) {
          var row = investorData[i];
          html += "<tr>";
          html += "<td>" + row.date + "</td>";
          html += "<td>" + row.individual + "</td>";
          html += "<td>" + row.foreigner + "</td>";
          html += "<td>" + row.institution + "</td>";
          html += "<td>" + row.fin_inv + "</td>";
          html += "<td>" + row.insurance + "</td>";
          html += "<td>" + row.inv_trust + "</td>";
          html += "<td>" + row.bank + "</td>";
          html += "<td>" + row.other_fin + "</td>";
          html += "<td>" + row.pension + "</td>";
          html += "<td>" + row.other_corp + "</td>";
          html += "</tr>";
        }
        html += "</table></body></html>";
        return ContentService.createTextOutput(html);
      }
      
      // 4. 모든 API 실패 시 네이버 금융 다중 페이지 크롤링 폴백 (기존 로직)
      var combinedHtml = "";
      for (var page = 1; page <= 2; page++) {
        var pageUrl = "https://finance.naver.com/sise/investorDealTrendDay.nhn?sosok=0&page=" + page;
        try {
          var response = UrlFetchApp.fetch(pageUrl, {
            "headers": {
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
              "Referer": "https://finance.naver.com/"
            },
            "muteHttpExceptions": true
          });
          if (response.getResponseCode() === 200) {
            combinedHtml += response.getContentText("EUC-KR") + "\n";
          }
        } catch(err) {
          // 건너뛰기
        }
        Utilities.sleep(100);
      }
      return ContentService.createTextOutput(combinedHtml);
    }
    
    // 일반 단일 URL 프록시 요청 처리 (KOSPI 지수 등)
    var response = UrlFetchApp.fetch(url, {
      "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Referer": "https://finance.naver.com/"
      },
      "muteHttpExceptions": true
    });
    
    return ContentService.createTextOutput(response.getContentText());
  } catch(err) {
    return ContentService.createTextOutput("Error: " + err.toString());
  }
}

// ----------------- KIS 및 Daum 파싱 도우미 함수들 ----------------- //

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
    throw new Error("KIS 토큰 실패: " + response.getContentText());
  }
}

function getKospiInvestorDataFromKis(token, appKey, appSecret, isMock) {
  var baseUrl = isMock ? "https://openapivts.koreainvestment.com:29443" : "https://openapi.koreainvestment.com:9443";
  var url = baseUrl + "/uapi/domestic-stock/v1/quotations/inquire-investor-daily-by-market";
  
  var today = new Date();
  var start = new Date();
  start.setDate(today.getDate() - 220); // 120 영업일 보장용
  
  var todayYmd = Utilities.formatDate(today, "GMT+9", "yyyyMMdd");
  var startYmd = Utilities.formatDate(start, "GMT+9", "yyyyMMdd");
  
  // KIS OpenAPI의 inquire-investor-daily-by-market(FHPTJ04040000)은 FID_INPUT_ISCD와 FID_INPUT_ISCD_1을 요구합니다.
  // 단, FID_INPUT_ISCD_1의 값으로 0001을 주면 다음 인덱스인 ISCD_2를 찾으므로, 빈 값(FID_INPUT_ISCD_1=)으로 전송해야 합니다.
  var queryParams = "?FID_COND_MRKT_DIV_CODE=U&FID_INPUT_ISCD=0001&FID_INPUT_ISCD_1=&FID_INPUT_DATE_1=" + startYmd + "&FID_INPUT_DATE_2=" + todayYmd + "&FID_PERIOD_DIV_CODE=D";
  
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
    throw new Error("KIS API 에러: " + response.getContentText());
  }
  
  var output = json.output;
  var investorRows = [];
  
  for (var i = 0; i < output.length; i++) {
    var row = output[i];
    var dateRaw = row.stck_bsop_date;
    var formattedDate = dateRaw.substring(0, 4) + "." + dateRaw.substring(4, 6) + "." + dateRaw.substring(6, 8);
    
    investorRows.push({
      date: formattedDate,
      individual: Math.round(parseFloat(row.prsn_ntby_amt) / 100),
      foreigner: Math.round(parseFloat(row.frgn_ntby_amt) / 100),
      institution: Math.round(parseFloat(row.orgn_ntby_amt) / 100),
      fin_inv: Math.round(parseFloat(row.finv_ntby_amt) / 100),
      insurance: Math.round(parseFloat(row.insu_ntby_amt) / 100),
      inv_trust: Math.round(parseFloat(row.thst_ntby_amt) / 100),
      bank: Math.round(parseFloat(row.bank_ntby_amt) / 100),
      other_fin: Math.round(parseFloat(row.etcg_ntby_amt) / 100),
      pension: Math.round(parseFloat(row.pnsn_ntby_amt) / 100),
      other_corp: Math.round(parseFloat(row.etco_ntby_amt) / 100)
    });
  }
  
  return investorRows;
}

function getKospiInvestorDataFromDaum() {
  var url = "https://finance.daum.net/api/investor/days?symbolCode=U001&page=1&perPage=30";
  var response = UrlFetchApp.fetch(url, {
    "headers": {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
      "Referer": "https://finance.daum.net/domestic/investors"
    },
    "muteHttpExceptions": true
  });
  
  if (response.getResponseCode() !== 200) {
    throw new Error("Daum API 실패: " + response.getResponseCode());
  }
  
  var json = JSON.parse(response.getContentText());
  var list = json.data || json.output || json;
  if (!list || !Array.isArray(list) || list.length === 0) {
    throw new Error("Daum API 포맷 오류");
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
    divisor = 100000000;
  } else if (avgAbs > 100) {
    divisor = 100;
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
