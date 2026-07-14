import json
import os
import re

scan_result_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\scan_result.json"

with open(scan_result_path, "r", encoding="utf-8") as f:
    files = json.load(f)

img_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic"}

# 1. 졸업앨범 관련 정밀 매칭
# 졸업앨범 사진 검토용이므로 "졸업"과 "사진" 또는 "앨범"이 경로/파일명에 결합되거나, "증명사진", "졸업사진" 등이 명시된 경우
def is_graduation_album_pic(filename, rel_path, ext):
    if ext not in img_exts:
        return False
    
    path_lower = rel_path.lower()
    file_lower = filename.lower()
    
    # 앨범 자체 또는 졸업사진용 폴더인지 검사
    if "졸업앨범" in path_lower or "졸업사진" in path_lower or "앨범사진" in path_lower:
        return True
        
    # 파일명 매칭
    if "졸업" in file_lower and "사진" in file_lower:
        return True
    if "앨범" in file_lower and "사진" in file_lower:
        return True
    if "증명사진" in file_lower or "프로필사진" in file_lower:
        return True
        
    return False

# 2. 극심한 개인정보 파일 (등본, 초본, 가족관계증명서, 신분증 스캔본 등)
# 단순 안내문이나 동의서 서식을 제외하기 위한 규칙
def is_highly_sensitive_personal_info(filename, rel_path):
    path_lower = rel_path.lower()
    file_lower = filename.lower()
    
    # 제외 키워드 (서식, 안내문, 공문, 계획, 신청서) - 실제 증명서가 아닐 가능성이 높음
    exclude_kws = ["안내", "양식", "서식", "공문", "계획", "방법", "작성법", "일정", "제출", "규정"]
    for ex in exclude_kws:
        if ex in file_lower:
            return False
            
    # 핵심 민감 개인정보 키워드
    sensitive_kws = [
        "등본", "초본", "주민등록", "가족관계", "가족기록", "가족증명", "기본증명", 
        "신분증", "주민등록증", "여권", "면허증", "통장사본", "통장 사본", "보건증",
        "가족관계증명서", "주민등록등본", "주민등록초본"
    ]
    
    for kw in sensitive_kws:
        if kw in file_lower:
            return True
            
    return False

album_deletes = []
personal_deletes = []
keep_and_organize = []

for file_info in files:
    filename = file_info["filename"]
    rel_path = file_info["rel_path"]
    _, ext = os.path.splitext(filename.lower())
    
    if is_highly_sensitive_personal_info(filename, rel_path):
        personal_deletes.append(file_info)
    elif is_graduation_album_pic(filename, rel_path, ext):
        album_deletes.append(file_info)
    else:
        keep_and_organize.append(file_info)

print(f"=== 정밀 분류 결과 ===")
print(f"전체 파일: {len(files)}")
print(f"실제 졸업앨범 삭제 대상: {len(album_deletes)} 개")
print(f"실제 개인정보 삭제 대상: {len(personal_deletes)} 개")
print(f"정리/보존 대상: {len(keep_and_organize)} 개")

# 정밀 분류용 샘플 저장
refined_summary = {
    "album_delete_count": len(album_deletes),
    "personal_delete_count": len(personal_deletes),
    "keep_count": len(keep_and_organize),
    "sample_album_deletes": [f["rel_path"] for f in album_deletes[:15]],
    "sample_personal_deletes": [f["rel_path"] for f in personal_deletes[:15]],
    "sample_keeps": [f["rel_path"] for f in keep_and_organize[:15]]
}

refined_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\refined_summary.json"
with open(refined_path, "w", encoding="utf-8") as f:
    json.dump(refined_summary, f, ensure_ascii=False, indent=2)
print(f"Refined summary saved to {refined_path}")
