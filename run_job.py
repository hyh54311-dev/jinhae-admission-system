# -*- coding: utf-8 -*-
"""
================================================================================
Antigravity Automations 공통 안전 실행 런처 (run_job.py)
--------------------------------------------------------------------------------
Claude Opus 감사 권고사항(P1)을 100% 반영한 통합 안전 실행기입니다.

1. 정본 폴더(PROJECT_ROOT) 디렉터리 강제 고정 (상대경로 유실 방지)
2. 자식 프로세스 UTF-8 강제 환경변수 주입 (PYTHONUTF8=1, PYTHONIOENCODING=utf-8)
3. 작업별 정밀 타임아웃 방어 (무한 프리징 원천 차단)
4. 일자/시간별 중복 실행 방지 락파일 (Duplicate Lock)
5. 비정상 종료/타임아웃 시 텔레그램 긴급 실패 경보 자동 발송 (.env 연동)
================================================================================
"""

import os
import sys
import subprocess
import datetime
import time
import json
import urllib.request
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

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

PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)

LOG_DIR = PROJECT_ROOT / "logs"
LOCK_DIR = LOG_DIR / "locks"
LAST_SUCCESS_DIR = LOG_DIR / "last_success"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOCK_DIR.mkdir(parents=True, exist_ok=True)
LAST_SUCCESS_DIR.mkdir(parents=True, exist_ok=True)

MAIN_LOG_FILE = LOG_DIR / "run_job.log"

# .env 로드 (텔레그램 토큰)
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# 작업별 정의 (실행 명령, 타임아웃 초, 설명)
JOB_SPECS = {
    "selftest": {
        "name": "오토메이션 사전 점검 (Self-Test)",
        "cmd": [sys.executable, "scripts/selftest_runner.py"],
        "timeout": 60,
    },
    "selftest-fail": {
        "name": "오토메이션 모의 실패 점검 (Self-Test Failure)",
        "cmd": [sys.executable, "scripts/selftest_runner.py", "--fail"],
        "timeout": 60,
    },
    "morning": {
        "name": "매일 아침 학사·일정 브리핑",
        "cmd": [sys.executable, "scripts/daily_morning_briefing.py"],
        "timeout": 300,
    },
    "parenting": {
        "name": "주간 육아시간 분석 & 조기퇴근 알리미",
        "cmd": [sys.executable, "scratch/send_friday_parenting_leave_telegram.py"],
        "timeout": 300,
    },
    "admission": {
        "name": "주간 대입 입시 뉴스 & 팩트 리포터",
        "cmd": [sys.executable, "admission_news.py", "run_now"],
        "timeout": 1800,
    },
    "news": {
        "name": "조간·야간 국내외 뉴스 브리핑",
        "cmd": [sys.executable, "news_briefing_bot.py"],
        "timeout": 300,
    },
    "kospi": {
        "name": "KOSPI 증시 위험 모니터링",
        "cmd": [sys.executable, "scripts/run_kospi_market_monitors.py"],
        "timeout": 600,
    },
}


def log(msg: str):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{now_str}] [run_job] {msg}"
    print(formatted)
    try:
        with open(MAIN_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def send_failure_telegram(job_name: str, reason: str, log_snippet: str = ""):
    """작업 실패 시 사용자 텔레그램으로 비상 알림 발송"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        log("⚠️ TELEGRAM_TOKEN 또는 TELEGRAM_CHAT_ID가 없어 실패 알림을 보내지 못했습니다.")
        return

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    snippet_text = f"\n\n<b>[최근 로그 요약]:</b>\n<pre>{log_snippet[-1500:]}</pre>" if log_snippet else ""

    text = (
        f"🚨 <b>[Antigravity 자동화 작업 실패 경보]</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"• <b>작업명:</b> {job_name}\n"
        f"• <b>발생 시각:</b> {now_str}\n"
        f"• <b>실패 사유:</b> {reason}"
        f"{snippet_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ 시스템 로그(logs/run_job.log)를 확인해 주시기 바랍니다."
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            log(f"🔔 텔레그램 실패 경보 발송 완료 (HTTP {resp.status})")
    except Exception as e:
        log(f"❌ 텔레그램 실패 경보 전송 실패: {e}")


def execute_job(job_key: str) -> int:
    if job_key not in JOB_SPECS:
        err = f"알 수 없는 작업 키: '{job_key}'. 가능한 키: {list(JOB_SPECS.keys())}"
        log(f"❌ {err}")
        send_failure_telegram(job_key, err)
        return 1

    spec = JOB_SPECS[job_key]
    job_name = spec["name"]
    cmd = spec["cmd"]
    timeout = spec["timeout"]

    now = datetime.datetime.now()
    date_hour = now.strftime("%Y%m%d_%H")
    lock_file = LOCK_DIR / f"{job_key}_{date_hour}.lock"

    # 중복 실행 방지 락 검사 (점검 작업은 제외)
    if job_key not in ["selftest", "selftest-fail"] and lock_file.exists():
        log(f"🔒 락 파일 존재({lock_file.name}). 이번 시간대({date_hour})는 이미 실행되었으므로 건너뜁니다.")
        return 0

    log(f"==================================================")
    log(f"🚀 작업 시작: [{job_name}] (키: {job_key})")
    log(f"• 작업 디렉터리: {PROJECT_ROOT}")
    log(f"• 실행 명령: {' '.join(str(c) for c in cmd)}")
    log(f"• 타임아웃 제한: {timeout}초")
    log(f"==================================================")

    # 자식 프로세스 환경변수 보강 (UTF-8 강제 및 사이드카 감지 전달)
    child_env = os.environ.copy()
    child_env["PYTHONUTF8"] = "1"
    child_env["PYTHONIOENCODING"] = "utf-8"
    if "--sidecar" in sys.argv or os.getenv("ANTIGRAVITY_SIDECAR") == "1":
        child_env["ANTIGRAVITY_SIDECAR"] = "1"
        if "--sidecar" not in cmd and job_key in ["selftest", "selftest-fail"]:
            cmd = list(cmd) + ["--sidecar"]

    start_time = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            env=child_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )

        elapsed = time.time() - start_time
        combined_output = (proc.stdout or "") + ("\n[STDERR]\n" + proc.stderr if proc.stderr else "")

        if proc.returncode == 0:
            log(f"✅ [{job_name}] 정상 완료 (소요시간: {elapsed:.2f}초, 종료코드: 0)")
            # 성공 시 락 생성 및 마지막 성공 시각 기록 (감시 워치독 연동)
            if job_key not in ["selftest", "selftest-fail"]:
                try:
                    lock_file.write_text(f"Executed at {now.isoformat()}\n", encoding="utf-8")
                except Exception:
                    pass
            try:
                success_file = LAST_SUCCESS_DIR / f"{job_key}.txt"
                success_file.write_text(f"{now.isoformat()}\n", encoding="utf-8")
            except Exception:
                pass
            return 0
        else:
            reason = f"비정상 종료 (종료코드: {proc.returncode})"
            log(f"❌ [{job_name}] {reason} (소요시간: {elapsed:.2f}초)")
            if proc.stderr:
                log(f"  [STDERR]: {proc.stderr[:500]}")
            send_failure_telegram(job_name, reason, combined_output)
            return proc.returncode

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        reason = f"실행 시간 초과 (제한 {timeout}초 초과로 프로세스 강제 중단)"
        log(f"❌ [{job_name}] {reason} (경과: {elapsed:.2f}초)")
        send_failure_telegram(job_name, reason)
        return 124

    except Exception as e:
        elapsed = time.time() - start_time
        reason = f"런처 예외 발생: {e}"
        log(f"❌ [{job_name}] {reason} (소요: {elapsed:.2f}초)")
        send_failure_telegram(job_name, reason)
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python run_job.py <job_key>")
        print(f"가능한 작업 키: {list(JOB_SPECS.keys())}")
        sys.exit(1)

    target_key = sys.argv[1].strip()
    exit_code = execute_job(target_key)
    sys.exit(exit_code)
