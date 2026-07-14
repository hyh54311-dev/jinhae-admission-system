import json
import os
import shutil
import re
from datetime import datetime

source_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더"
target_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더_정리완료"
quarantine_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더_삭제격리"

scan_result_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\scan_result.json"

if not os.path.exists(scan_result_path):
    print("scan_result.json does not exist. Run scanner first.")
    exit(1)

with open(scan_result_path, "r", encoding="utf-8") as f:
    files = json.load(f)

img_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic"}

# 1. 개인정보 민감 파일 필터
def is_highly_sensitive_personal_info(filename, rel_path):
    path_lower = rel_path.lower()
    file_lower = filename.lower()
    
    exclude_kws = ["안내", "양식", "서식", "공문", "계획", "방법", "작성법", "일정", "제출", "규정"]
    for ex in exclude_kws:
        if ex in file_lower:
            return False
            
    sensitive_kws = [
        "등본", "초본", "주민등록", "가족관계", "가족기록", "가족증명", "기본증명", 
        "신분증", "주민등록증", "여권", "면허증", "통장사본", "통장 사본", "보건증",
        "가족관계증명서", "주민등록등본", "주민등록초본"
    ]
    for kw in sensitive_kws:
        if kw in file_lower:
            return True
    return False

# 2. 졸업앨범용 학생 사진 필터
def is_graduation_album_pic(filename, rel_path, ext):
    if ext not in img_exts:
        return False
    path_lower = rel_path.lower()
    file_lower = filename.lower()
    
    if "졸업앨범" in path_lower or "졸업사진" in path_lower or "앨범사진" in path_lower:
        return True
    if "졸업" in file_lower and "사진" in file_lower:
        return True
    if "앨범" in file_lower and "사진" in file_lower:
        return True
    if "증명사진" in file_lower or "프로필사진" in file_lower:
        return True
    return False

# 3. 4대 분류 매핑 규칙
def classify_category(filename, rel_path):
    comb = (rel_path + "/" + filename).lower()
    
    # 창체 동아리
    if any(kw in comb for kw in ["동아리", "창체", "자율동아리"]):
        return "창체 동아리"
        
    # 수업
    class_kws = [
        "수업", "문학", "언어와 매체", "활동자료", "교과", "학습지", "시험", "평가", 
        "문제", "ppt", "국어", "독서", "작문", "화법", "문법", "seteuk", "세특", 
        "수능", "모의고사", "학습", "교재", "교육과정", "고전문학", "현대문학"
    ]
    if any(kw in comb for kw in class_kws):
        return "수업"
        
    # 학급 경영
    management_kws = [
        "학급", "조회", "종례", "담임", "생활기록부", "생기부", "출석", "출결", 
        "야자", "자율학습", "상담", "자리", "번호", "주소록", "명렬", "학생",
        "1반", "2반", "3반", "4반", "5반", "6반", "7반", "8반", "9반", "10반"
    ]
    if any(kw in comb for kw in management_kws):
        return "학급 경영"
        
    # 기획(학교행사 및 홍보)
    planning_kws = [
        "기획", "행사", "홍보", "설명회", "발표회", "축제", "대회", "기념식", 
        "졸업식", "입학식", "학부모", "운영위원회", "계획서", "공동교육과정"
    ]
    if any(kw in comb for kw in planning_kws):
        return "기획(학교행사 및 홍보)"
        
    return "기타 공통 업무"

# 폴더 청소 및 생성
if os.path.exists(target_dir):
    shutil.rmtree(target_dir)
os.makedirs(target_dir, exist_ok=True)

if os.path.exists(quarantine_dir):
    shutil.rmtree(quarantine_dir)
os.makedirs(quarantine_dir, exist_ok=True)

stats = {
    "total_scanned": len(files),
    "personal_deleted": 0,
    "album_deleted": 0,
    "organized": 0,
    "years": {}
}

print("[START] Reorganization and classification process started...")

for idx, file_info in enumerate(files):
    full_path = file_info["full_path"]
    filename = file_info["filename"]
    rel_path = file_info["rel_path"]
    _, ext = os.path.splitext(filename.lower())
    
    # 실제 파일 미존재 방어선
    if not os.path.exists(full_path):
        continue

    # 1. 개인정보 민감 파일 격리 (삭제)
    if is_highly_sensitive_personal_info(filename, rel_path):
        dest = os.path.join(quarantine_dir, "개인정보", rel_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(full_path, dest)
        stats["personal_deleted"] += 1
        continue

    # 2. 졸업앨범 학생 사진 격리 (삭제)
    if is_graduation_album_pic(filename, rel_path, ext):
        dest = os.path.join(quarantine_dir, "졸업앨범사진", rel_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(full_path, dest)
        stats["album_deleted"] += 1
        continue

    # 3. 보존 및 연도별 정렬
    # 연도 추출
    found_year = None
    match4 = re.search(r"20(2\d|1\d)", rel_path + "/" + filename)
    if match4:
        found_year = match4.group(0)
    else:
        match2 = re.search(r"\b(2\d|1\d)학년도", rel_path + "/" + filename)
        if match2:
            found_year = "20" + match2.group(1)
            
    if not found_year:
        try:
            mtime = os.path.getmtime(full_path)
            dt = datetime.fromtimestamp(mtime)
            mtime_year = str(dt.year)
            if 2010 <= int(mtime_year) <= 2026:
                found_year = mtime_year
        except Exception:
            pass
            
    if not found_year:
        found_year = "연도미상"

    year_folder = f"{found_year}학년도" if found_year != "연도미상" else "연도미분류"
    category = classify_category(filename, rel_path)
    
    # 최종 보존 파일 복사 경로 설정
    dest_path = os.path.join(target_dir, year_folder, category, filename)
    
    # 동일 파일명 중복 충돌 방지 로직
    base, extension = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(target_dir, year_folder, category, f"{base}_{counter}{extension}")
        counter += 1
        
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy2(full_path, dest_path)
    
    stats["organized"] += 1
    stats["years"][year_folder] = stats["years"].get(year_folder, 0) + 1

    if idx % 1000 == 0:
        print(f" > 진행 중... {idx}/{len(files)} 완료")

print("\n[SUCCESS] Reorganization and cleanup completed successfully!")
print(f" - Total Checked: {stats['total_scanned']} files")
print(f" - Graduation Album Pictures Deleted (Quarantined): {stats['album_deleted']} files")
print(f" - Sensitive Personal Documents Deleted (Quarantined): {stats['personal_deleted']} files")
print(f" - Successfully Organized Files: {stats['organized']} files")

# 격리 폴더에 격리했으니 원본 파일 삭제 여부를 지휘할 준비를 마쳤습니다.
# 최종 통계 json 파일로 저장하여 Powershell 팝업 알림에서 로드하여 사용하도록 연계합니다.
stats_output_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\cleanup_stats.json"
with open(stats_output_path, "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)
