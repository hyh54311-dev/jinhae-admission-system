import json
import os
import re

scan_result_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\scan_result.json"

if not os.path.exists(scan_result_path):
    print("scan_result.json does not exist!")
    exit(1)

with open(scan_result_path, "r", encoding="utf-8") as f:
    files = json.load(f)

# 확장자 소문자화
img_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic"}

album_keywords = ["졸업", "앨범", "사진", "album", "graduation", "증명사진", "프로필", "단체사진"]
personal_keywords = ["등본", "초본", "가족", "주민등록", "가족관계", "기본증명", "신분증", "여권", "면허", "통장", "주민", "개인정보", "서약서", "동의서", "건강진단", "보건증"]

album_delete_targets = []
personal_delete_targets = []
other_files = []

# 연도별 정리를 위한 연도 파싱 정규식
year_pattern = re.compile(r"(20\d{2})|(2\d{1})학?년?도?")

for file_info in files:
    filename = file_info["filename"]
    rel_path = file_info["rel_path"]
    full_path = file_info["full_path"]
    _, ext = os.path.splitext(filename.lower())
    
    # 1. 개인정보 민감 파일인지 우선 확인 (파일명 또는 경로에 키워드 포함)
    is_personal = False
    for kw in personal_keywords:
        if kw in filename or kw in rel_path:
            is_personal = True
            break
            
    if is_personal:
        personal_delete_targets.append(file_info)
        continue

    # 2. 졸업앨범 이미지 파일인지 확인
    is_album = False
    if ext in img_exts:
        for kw in album_keywords:
            if kw in filename or kw in rel_path:
                is_album = True
                break
    
    if is_album:
        album_delete_targets.append(file_info)
        continue
        
    other_files.append(file_info)

# 연도별 분류 분석
year_counts = {}
unclassified_files = []

for file_info in other_files:
    filename = file_info["filename"]
    rel_path = file_info["rel_path"]
    
    # 파일명 및 경로에서 연도 추출 시도
    # 예: 2021학년도, 2021, 22학년도, 22 등
    # 가장 먼저 매칭되는 4자리 연도를 찾고, 없으면 2자리 연도 매칭
    found_year = None
    
    # 4자리 연도 매칭
    match4 = re.search(r"20(2\d|1\d)", rel_path + "/" + filename)
    if match4:
        found_year = match4.group(0)
    else:
        # 2자리 학년도 매칭 (예: 21학년도 -> 2021, 25학년도 -> 2025)
        match2 = re.search(r"\b(2\d|1\d)학년도", rel_path + "/" + filename)
        if match2:
            found_year = "20" + match2.group(1)
            
    if found_year:
        year_counts[found_year] = year_counts.get(found_year, 0) + 1
        file_info["detected_year"] = found_year
    else:
        # 연도를 유추할 수 없는 경우, 원본 파일의 mtime(수정 시간)에서 추출 시도
        try:
            mtime = os.path.getmtime(file_info["full_path"])
            from datetime import datetime
            dt = datetime.fromtimestamp(mtime)
            # 학교 특성상 1~2월은 이전 학년도에 해당할 수 있으나, 일단 심플하게 연도 추출
            mtime_year = str(dt.year)
            # 만약 mtime_year가 유효한 범위(2010~2026)인 경우 활용
            if 2010 <= int(mtime_year) <= 2026:
                year_counts[mtime_year] = year_counts.get(mtime_year, 0) + 1
                file_info["detected_year"] = mtime_year
            else:
                unclassified_files.append(file_info)
        except Exception:
            unclassified_files.append(file_info)

print("=== 분석 결과 요약 ===")
print(f"전체 스캔 파일 수: {len(files)}")
print(f"1. 졸업앨범 이미지 삭제 대상: {len(album_delete_targets)} 개")
print(f"2. 개인정보 민감 삭제 대상: {len(personal_delete_targets)} 개")
print(f"3. 정리 대상 파일 수: {len(other_files)} 개")
print("\n=== 연도별 정리 대상 통계 (파일명/경로/수정시간 분석) ===")
for y in sorted(year_counts.keys()):
    print(f" - {y}학년도: {year_counts[y]} 개")
print(f" - 연도 미분류: {len(unclassified_files)} 개")

# 예시용 일부 데이터 저장
analysis_summary = {
    "total": len(files),
    "album_delete_count": len(album_delete_targets),
    "personal_delete_count": len(personal_delete_targets),
    "other_count": len(other_files),
    "year_counts": year_counts,
    "unclassified_count": len(unclassified_files),
    "sample_album_deletes": [f["rel_path"] for f in album_delete_targets[:10]],
    "sample_personal_deletes": [f["rel_path"] for f in personal_delete_targets[:10]],
    "sample_others": [f["rel_path"] for f in other_files[:10]]
}

summary_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\analysis_summary.json"
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(analysis_summary, f, ensure_ascii=False, indent=2)
print(f"\n상세 분석 샘플이 {summary_path} 에 저장되었습니다.")
