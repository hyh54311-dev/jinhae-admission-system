// utils.js - 공통 유틸리티 모듈 (나이스 바이트 계산기 및 CSV 파서)

window.Utils = {
  /**
   * 교육부 나이스(NEIS) 입력 시스템 기준의 정확한 바이트 계산기
   * - 한글/기타 풀위드 문자: 3바이트
   * - 영문/숫자/공백/일반 아스키 기호: 1바이트
   * - 줄바꿈(엔터): 2바이트 (NEIS 내부 DB 저장시 \r\n 2바이트로 처리됨)
   */
  getNeisByteLength(text) {
    if (!text) return 0;
    
    // 개행 문자(\r\n)를 \n으로 정규화하여 중복 계산 방지
    let normalized = text.replace(/\r\n/g, '\n');
    let bytes = 0;
    
    for (let i = 0; i < normalized.length; i++) {
      const char = normalized.charAt(i);
      const code = normalized.charCodeAt(i);
      
      if (char === '\n') {
        bytes += 2; // 줄바꿈은 2바이트로 계산
      } else if (code <= 127) {
        bytes += 1; // 아스키 문자(영문, 숫자, 공백 등)는 1바이트
      } else {
        bytes += 3; // 한글, 한자, 전각 문자 등은 3바이트
      }
    }
    return bytes;
  },

  /**
   * 쌍따옴표(") 및 쉼표(,)를 포함하는 표준 CSV 데이터를 2차원 배열로 파싱하는 견고한 함수
   */
  parseCSV(text) {
    let lines = [];
    let row = [""];
    let inQuotes = false;

    for (let i = 0; i < text.length; i++) {
      let c = text[i];
      let next = text[i + 1];

      if (c === '"') {
        if (inQuotes && next === '"') {
          row[row.length - 1] += '"';
          i++; // 연속된 쌍따옴표는 이스케이프 처리하여 문자 하나로 취급
        } else {
          inQuotes = !inQuotes; // 인용부 구역 반전
        }
      } else if (c === ',' && !inQuotes) {
        row.push(""); // 쉼표 기준 열 구분
      } else if ((c === '\r' || c === '\n') && !inQuotes) {
        if (c === '\r' && next === '\n') {
          i++; // \r\n인 경우 \n을 뛰어넘음
        }
        lines.push(row);
        row = [""]; // 새 행으로 리셋
      } else {
        row[row.length - 1] += c;
      }
    }
    
    // 마지막 행 추가 처리
    if (row.length > 1 || row[0] !== "") {
      lines.push(row);
    }
    return lines;
  },

  /**
   * 날짜 형식을 YYYY-MM-DD 형식으로 가공하는 포맷터
   */
  formatDate(dateStr) {
    if (!dateStr) return "-";
    let d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    
    let year = d.getFullYear();
    let month = String(d.getMonth() + 1).padStart(2, '0');
    let day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  },

  /**
   * 클립보드로 텍스트 복사하는 유틸리티
   */
  copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    } else {
      let textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";  // 화면 밖으로 배치
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand("copy");
        document.body.removeChild(textarea);
        return Promise.resolve();
      } catch (err) {
        document.body.removeChild(textarea);
        return Promise.reject(err);
      }
    }
  }
};
