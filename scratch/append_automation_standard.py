import os

standard_path = "automation_standard.md"

guide_content = """

## 구글 폼/시트 수기 입력 자동화 표준 가이드 (2026-06-08 추가)

### 1. 도메인 제한 구글 폼 제출 문제 해결 표준
* **문제점**: 교육청/학교 Workspace 도메인 제한이 있는 구글 폼은 로그인하지 않은 익명 HTTP POST(Python requests 등) 요청 시 `200 OK` 응답 코드와 함께 로그인 안내 페이지 HTML을 리턴하므로, 코드상으로는 전송 성공으로 오판하나 실제로는 데이터가 유실되는 심각한 오류가 발생합니다.
* **표준 해결책**: 구글 폼 우회 제출을 시도하지 않고, **연동된 구글 스프레드시트 API를 활용해 시트에 직접 데이터를 삽입(Append)합니다.** 이는 `token.json` 구글 인증을 활용하여 도메인 제한의 영향을 전혀 받지 않으므로 100% 안전하고 확실합니다.

### 2. 3학년 화법과작문 수행평가 시트 구조 규격
* **스프레드시트 ID**: `1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU` (구글 드라이브 내 '제목 없는 스프레드시트')
* **대상 탭 이름**: `설문지 응답 시트6`
* **열 구성 (17개 열 - 0부터 시작하는 인덱스 기준)**:
  * `[0]`: 타임스탬프 (형식: `YYYY. M. D. 오전/오후 H:MM:SS`)
  * `[1]`: 반 선택 (값 예시: `"8반"`, `"6반"`)
  * `[2] ~ [11]`: 각 반별 이름 선택 (1반은 index 2, 2반은 index 3, ..., 10반은 index 11). **반드시 해당 학생의 학반 열에만 "번호 이름" 형태로 기입하고, 다른 9개 반의 이름 열은 `""`(빈 값) 처리해야 함.**
  * `[12]`: 16번 답안 (세런디피티 개념)
  * `[13]`: 17번 답안 (연구 수행자)
  * `[14]`: 18번 답안 (개발 동기)
  * `[15]`: 19번 답안 (페니실린 박테리아 억제)
  * `[16]`: 20번 답안 (그람 음성균 효과 없음)

### 3. 필수 검증 수칙 (Verify)
* **실시간 적재 확인**: 데이터 추가 API 호출 직후, 반드시 해당 스프레드시트의 값을 다시 조회(Read)하여 **실제 입력 완료 여부 및 행 수 증가를 확인**해야 합니다.
* **이름 중복 및 전후 비교**: 입력 전 해당 학생이 이전에 제출한 내역(기존 타임스탬프)이 있는지 이름을 우선 검색하고, 중복 제출이 발견되면 기존 데이터와의 정합성을 비교하고 중복을 정리해야 합니다.
"""

encodings = ['utf-8', 'cp949', 'euc-kr']
content = None
read_encoding = 'utf-8'

if os.path.exists(standard_path):
    for enc in encodings:
        try:
            with open(standard_path, 'r', encoding=enc) as f:
                content = f.read()
            read_encoding = enc
            print(f"Successfully read file with encoding: {enc}")
            break
        except Exception:
            pass

try:
    if content is not None:
        if "구글 폼/시트 수기 입력 자동화 표준 가이드" not in content:
            new_content = content + guide_content
            with open(standard_path, 'w', encoding=read_encoding) as f:
                f.write(new_content)
            print(f"Successfully appended the standard in encoding {read_encoding}.")
        else:
            print("Standard already documented in automation_standard.md.")
    else:
        with open(standard_path, 'w', encoding='utf-8') as f:
            f.write("# Automation Standards\n" + guide_content)
        print("Created automation_standard.md with the standard guide.")
except Exception as e:
    print("Error updating automation standard file:", e)
