# -*- coding: utf-8 -*-
"""
Antigravity 에이전트 코어
Gemini Function Calling을 사용하여 파일 읽기/쓰기, 명령 실행 등을 수행합니다.
"""

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import os
import subprocess
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_FILE_SIZE = 60 * 1024  # 60KB

# ─── 도구 함수 ───────────────────────────────────────────────────

def list_files(path="."):
    """폴더 내 파일 및 디렉토리 목록 반환"""
    try:
        target = os.path.join(BASE_DIR, path) if not os.path.isabs(path) else path
        target = os.path.normpath(target)
        if not os.path.exists(target):
            return f"경로가 존재하지 않습니다: {path}"

        items = []
        for item in sorted(os.listdir(target)):
            full_path = os.path.join(target, item)
            if os.path.isdir(full_path):
                items.append(f"📁 {item}/")
            else:
                size = os.path.getsize(full_path)
                items.append(f"📄 {item} ({size:,} bytes)")

        result = f"📂 {path} 목록 (총 {len(items)}개):\n" + "\n".join(items[:60])
        if len(items) > 60:
            result += f"\n... 외 {len(items) - 60}개 더 있음"
        return result
    except Exception as e:
        return f"오류: {e}"


def read_file(filepath):
    """파일 내용 읽기"""
    try:
        target = os.path.join(BASE_DIR, filepath) if not os.path.isabs(filepath) else filepath
        target = os.path.normpath(target)

        if not os.path.exists(target):
            return f"파일이 존재하지 않습니다: {filepath}"

        size = os.path.getsize(target)
        with open(target, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read(MAX_FILE_SIZE)

        truncated = size > MAX_FILE_SIZE
        result = f"[파일: {filepath} | {size:,} bytes]\n{content}"
        if truncated:
            result += f"\n\n⚠️ 파일이 커서 앞부분({MAX_FILE_SIZE:,} bytes)만 표시됩니다."
        return result
    except Exception as e:
        return f"오류: {e}"


def write_file(filepath, content):
    """파일 생성 또는 덮어쓰기"""
    try:
        target = os.path.join(BASE_DIR, filepath) if not os.path.isabs(filepath) else filepath
        target = os.path.normpath(target)

        parent = os.path.dirname(target)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"✅ 저장 완료: {filepath} ({len(content):,} chars)"
    except Exception as e:
        return f"오류: {e}"


def run_command(command):
    """PowerShell 명령어 실행"""
    try:
        # 파이썬 전체 종료 명령 시 자기 자신(봇) 종료 방지
        my_pid = os.getpid()
        if ("taskkill" in command.lower() or "stop-process" in command.lower()) and "python" in command.lower():
            command = f"Get-Process python -ErrorAction SilentlyContinue | Where-Object {{ $_.Id -ne {my_pid} }} | Stop-Process -Force"

        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command', command],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=BASE_DIR,
            encoding='utf-8',
            errors='replace'
        )
        output = (result.stdout + result.stderr).strip()
        if len(output) > 3000:
            output = output[:3000] + "\n...(출력 생략됨)"
        return output if output else "(출력 없음)"
    except subprocess.TimeoutExpired:
        return "⏱️ 명령 실행 시간 초과 (30초)"
    except Exception as e:
        return f"오류: {e}"


# ─── Gemini 도구 정의 ─────────────────────────────────────────────

TOOL_DEFINITIONS = {
    "function_declarations": [
        {
            "name": "list_files",
            "description": "지정된 경로의 파일 및 폴더 목록을 조회합니다.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "path": {
                        "type": "STRING",
                        "description": "조회할 경로. 기본값은 작업 디렉토리('.')."
                    }
                }
            }
        },
        {
            "name": "read_file",
            "description": "파일의 내용을 읽어서 반환합니다.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "filepath": {
                        "type": "STRING",
                        "description": "읽을 파일 경로 (상대 경로 또는 절대 경로)"
                    }
                },
                "required": ["filepath"]
            }
        },
        {
            "name": "write_file",
            "description": "파일을 생성하거나 내용을 덮어씁니다.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "filepath": {
                        "type": "STRING",
                        "description": "쓸 파일 경로"
                    },
                    "content": {
                        "type": "STRING",
                        "description": "파일에 저장할 내용"
                    }
                },
                "required": ["filepath", "content"]
            }
        },
        {
            "name": "run_command",
            "description": "PowerShell 명령어를 실행하고 결과를 반환합니다. 프로세스 목록, 파일 조작, 스크립트 실행 등에 사용합니다.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "command": {
                        "type": "STRING",
                        "description": "실행할 PowerShell 명령어"
                    }
                },
                "required": ["command"]
            }
        }
    ]
}

TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
}

# ─── 에이전트 루프 ────────────────────────────────────────────────

def run_agent(user_message, api_key, model_name="gemini-flash-lite-latest", send_update=None, history=None):
    """
    Gemini Function Calling 에이전트 루프.

    Args:
        user_message (str): 사용자 요청
        api_key (str): Gemini API 키
        model_name (str): 사용할 Gemini 모델
        send_update (callable): 중간 상태를 전송하는 콜백 (선택)

    Returns:
        str: 최종 응답
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    system_prompt = (
        f"당신은 'Antigravity' AI 에이전트입니다. 진해고등학교 선생님의 노트북(Windows)에서 실행 중입니다.\n"
        f"현재 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"작업 기본 디렉토리: {BASE_DIR}\n\n"
        "## 역할\n"
        "사용 가능한 도구(list_files, read_file, write_file, run_command)를 적극 활용하여\n"
        "사용자의 요청을 실제로 수행하는 에이전트입니다.\n"
        "단순 텍스트 답변이 아닌, 실제 파일 탐색·읽기·수정·명령 실행을 통해 작업합니다.\n\n"
        "## 답변 원칙\n"
        "- 작업 완료 후 무엇을 했는지 한국어로 명확히 설명\n"
        "- 파일 내용이나 명령 결과는 핵심만 요약해서 전달\n"
        "- 오류 발생 시 원인과 해결 방법 안내"
    )

    # 시스템 프롬프트는 첫 user 메시지로 삽입
    messages = [
        {"role": "user",  "parts": [{"text": system_prompt}]},
        {"role": "model", "parts": [{"text": "알겠습니다. 도구를 활용해 요청을 처리하겠습니다."}]}
    ]

    # 이전 대화 히스토리 삽입 (맥락 유지)
    if history:
        for past_user, past_model in history:
            messages.append({"role": "user",  "parts": [{"text": past_user}]})
            messages.append({"role": "model", "parts": [{"text": past_model}]})

    # 현재 메시지
    messages.append({"role": "user", "parts": [{"text": user_message}]})

    max_iterations = 15

    for iteration in range(max_iterations):
        payload = {
            "contents": messages,
            "tools": [TOOL_DEFINITIONS],
            "generationConfig": {
                "maxOutputTokens": 8192,
                "temperature": 0.1
            }
        }

        try:
            resp = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.Timeout:
            return "⏱️ API 응답 시간 초과 (60초)"
        except Exception as e:
            return f"❌ API 오류: {e}"

        candidates = data.get("candidates", [])
        if not candidates:
            # 안전 필터 등으로 응답이 없을 때
            prompt_feedback = data.get("promptFeedback", {})
            return f"응답을 생성할 수 없습니다. ({prompt_feedback})"

        candidate = candidates[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])

        # 모델 응답 히스토리에 추가
        messages.append({"role": "model", "parts": parts})

        # 함수 호출 파트 분리
        function_calls = [p for p in parts if "functionCall" in p]
        text_response = "".join([p.get("text", "") for p in parts if "text" in p])

        # 함수 호출이 없으면 최종 응답
        if not function_calls:
            return text_response.strip() if text_response.strip() else "✅ 작업 완료"

        # 도구 실행
        function_responses = []
        for fc_part in function_calls:
            fc = fc_part["functionCall"]
            func_name = fc.get("name", "")
            func_args = fc.get("args", {})

            # 중간 상태 전송
            if send_update:
                args_preview = ", ".join(f"{k}={repr(str(v))[:40]}" for k, v in func_args.items())
                send_update(f"🔧 `{func_name}({args_preview})`")

            # 도구 실행
            tool_func = TOOL_FUNCTIONS.get(func_name)
            if tool_func:
                try:
                    result = tool_func(**func_args)
                except Exception as e:
                    result = f"도구 실행 오류: {e}"
            else:
                result = f"알 수 없는 도구: {func_name}"

            function_responses.append({
                "functionResponse": {
                    "name": func_name,
                    "response": {"result": result}
                }
            })

        # 도구 결과 히스토리에 추가
        messages.append({
            "role": "user",
            "parts": function_responses
        })

    return "⚠️ 최대 작업 반복 횟수(15회)에 도달했습니다."
