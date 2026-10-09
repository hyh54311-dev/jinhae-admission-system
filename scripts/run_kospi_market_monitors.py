# -*- coding: utf-8 -*-
"""
KOSPI 종합 시장 위험 감지 통합 러너 (run_kospi_market_monitors.py)
------------------------------------------------------------------
평일 16:05 KST 장 마감 후 KOSPI 시장의 4대 주요 위험 지표를 순차 점검합니다.
1. 장기 하락장 감지 (kospi_bear_detector.py)
2. 중기 조정장 감지 (kospi_correction_detector.py)
3. 반등 및 FTD 신호 감지 (kospi_rebound_detector.py)
4. 거래 정지 및 서킷브레이커 감지 (kospi_halt_monitor.py)
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

# Windows OS 신뢰 인증서 저장소(학내망/기관망 SSL) 자동 연동
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

# 콘솔 UTF-8 설정
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "kospi_monitors.log"

DETECTORS = [
    ("장기 하락장 감지기", PROJECT_ROOT / "kospi_bear_detector.py"),
    ("중기 조정장 감지기", PROJECT_ROOT / "kospi_correction_detector.py"),
    ("반등 신호 감지기", PROJECT_ROOT / "kospi_rebound_detector.py"),
    ("거래정지 모니터", PROJECT_ROOT / "kospi_halt_monitor.py"),
]


def log(msg: str):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{now_str}] {msg}"
    print(formatted)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


KRX_HOLIDAYS_2026 = {
    "2026-01-01",  # 신정
    "2026-02-16", "2026-02-17", "2026-02-18",  # 설날 연휴
    "2026-03-01", "2026-03-02",  # 삼일절 및 대체공휴일
    "2026-05-01",  # 근로자의 날
    "2026-05-05",  # 어린이날
    "2026-05-24", "2026-05-25",  # 부처님오신날 및 대체공휴일
    "2026-06-06",  # 현충일
    "2026-07-17",  # 제헌절
    "2026-08-15", "2026-08-17",  # 광복절 및 대체공휴일
    "2026-09-24", "2026-09-25", "2026-09-26",  # 추석 연휴
    "2026-10-03", "2026-10-05",  # 개천절 및 대체공휴일
    "2026-10-09",  # 한글날 (휴장일)
    "2026-12-25",  # 성탄절
    "2026-12-31",  # 연말 결산 폐장일
}


def run_monitors():
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    is_dry_run = "--dry-run" in sys.argv

    log("==================================================")
    log(f"🚀 [KOSPI 종합 시장 위험 감지] 일일 정기 점검 시작 ({today_str})")
    log("==================================================")

    # [휴장일 처리 - 클로드 2차 감사 D 항목 반영]
    if today_str in KRX_HOLIDAYS_2026 or now.weekday() >= 5:
        log(f"⏸️ [휴장일 건너뜀] 오늘({today_str})은 KRX 증시 휴장일(공휴일/한글날/주말)입니다.")
        log("   상태 파일 갱신 및 감지 로직을 수행하지 않고 정상 종료합니다.")
        log("==================================================")
        return 0

    # [휴장일 캘린더 갱신 알림 - 클로드 3차 감사 2.3 항목 반영]
    if now.year > 2026 or (now.year == 2026 and now.month == 12):
        log(f"⚠️ [캘린더 갱신 안내] 차기 연도({now.year + 1}년) KRX 휴장일 목록 갱신 점검이 필요합니다.")

    results = []
    for name, script_path in DETECTORS:
        if not script_path.exists():
            log(f"⚠️ {name} 스크립트를 찾을 수 없습니다: {script_path}")
            continue

        log(f"▶ {name} 실행 중..." + (" [DRY-RUN]" if is_dry_run else ""))
        try:
            cmd = [sys.executable, str(script_path)]
            if is_dry_run:
                cmd.append("--dry-run")
            res = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
            stdout_clean = res.stdout.strip()
            stderr_clean = res.stderr.strip()
            
            if stdout_clean:
                for line in stdout_clean.splitlines():
                    log(f"  {line}")
            if stderr_clean and res.returncode != 0:
                log(f"  [STDERR] {stderr_clean}")

            status = "성공" if res.returncode == 0 else f"오류(코드 {res.returncode})"
            results.append((name, status))
        except subprocess.TimeoutExpired:
            log(f"❌ {name} 실행 시간 초과 (30초)")
            results.append((name, "시간초과"))
        except Exception as e:
            log(f"❌ {name} 실행 중 예외 발생: {e}")
            results.append((name, f"예외: {e}"))

    has_failure = any(status != "성공" for _, status in results)
    log("--------------------------------------------------")
    log("📊 [KOSPI 점검 결과 요약]:")
    for name, status in results:
        log(f" - {name}: {status}")
    log("==================================================")
    return 1 if has_failure else 0


if __name__ == "__main__":
    code = run_monitors()
    sys.exit(code)
