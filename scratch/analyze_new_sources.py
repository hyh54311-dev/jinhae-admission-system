# -*- coding: utf-8 -*-
import os
import json
import re
from datetime import datetime

src1 = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더 (2)"
src2 = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더_정리완료"

# 교과서 업체 키워드
publisher_keywords = [
    "비상교육", "비상", "천재교육", "천재", "미래엔", "지학사", 
    "금성교과서", "금성", "동아출판", "동아", "ybm", "YBM", 
    "visang", "chunjae", "miraen", "jihak", "교학사", "디딤돌"
]

# 학생 사진 관련 키워드
photo_keywords = [
    "사진", "일상", "생활", "얼굴", "증명", "단체", "졸업", 
    "수학여행", "체육대회", "소풍", "축제", "동아리", "학급", "야외", "여행", 
    "photo", "image", "pic", "album", "graduation"
]

img_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic"}

def scan_all_files():
    all_files = []
    
    # Scan Src1
    if os.path.exists(src1):
        for root, dirs, files in os.walk(src1):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, src1)
                size = os.path.getsize(full_path)
                mtime = os.path.getmtime(full_path)
                all_files.append({
                    "source": "새 폴더 (2)",
                    "rel_path": rel_path,
                    "full_path": full_path,
                    "name": file,
                    "size": size,
                    "mtime": mtime
                })
                
    # Scan Src2
    if os.path.exists(src2):
        for root, dirs, files in os.walk(src2):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, src2)
                size = os.path.getsize(full_path)
                mtime = os.path.getmtime(full_path)
                all_files.append({
                    "source": "새 폴더_정리완료",
                    "rel_path": rel_path,
                    "full_path": full_path,
                    "name": file,
                    "size": size,
                    "mtime": mtime
                })
                
    return all_files

def analyze():
    print("Scanning folders...")
    files = scan_all_files()
    print(f"Total files scanned: {len(files)}")
    
    publisher_deletes = []
    student_photo_deletes = []
    normal_files = []
    
    # 정규식으로 파일명에서 학생이름 패턴 감지 (예: "3학년1반 01번 홍길동.jpg", "홍길동_증명.jpg" 등)
    # 한국인 이름(2~4자 한글) 패턴
    name_pattern = re.compile(r"[가-힣]{2,4}")
    
    for f in files:
        name = f["name"]
        rel_path = f["rel_path"]
        _, ext = os.path.splitext(name.lower())
        
        # 1. 교과서 업체 자료 판별
        is_publisher = False
        # 파일명이나 상대경로에 교과서 업체 키워드가 있는지 검사
        path_lower = rel_path.lower()
        name_lower = name.lower()
        for kw in publisher_keywords:
            if kw in name_lower or kw in path_lower:
                is_publisher = True
                break
                
        if is_publisher:
            publisher_deletes.append(f)
            continue
            
        # 2. 학생 사진 판별 (이미지 확장자 중 사진 관련 키워드나 이름 패턴이 있는 경우)
        is_student_photo = False
        if ext in img_extensions:
            # 2-1) 키워드 매칭
            for kw in photo_keywords:
                if kw in name_lower or kw in path_lower:
                    is_student_photo = True
                    break
            
            # 2-2) 이름 패턴 매칭 (사진 파일인데 한글 이름이 들어가 있는 경우)
            if not is_student_photo and name_pattern.search(name):
                # 단, 너무 광범위한 매칭을 막기 위해 숫자+이름 조합이나 특정 자릿수를 좀 더 볼 수 있으나
                # 이미지 파일인데 한글 2~4글자가 들어가면 학생 사진일 가능성이 매우 높음
                is_student_photo = True
                
        if is_student_photo:
            student_photo_deletes.append(f)
            continue
            
        normal_files.append(f)
        
    # 연도별 정리 대상 분류
    # 연도 추출 규칙:
    # 1) 상대 경로에 "20XX학년도"가 포함되어 있으면 그것을 학년도로 지정
    # 2) 파일명에 "20XX"가 포함되어 있으면 학년도로 지정
    # 3) 파일명에 "XX학년도"가 포함되어 있으면 "20XX학년도"로 지정
    # 4) 수정일자(mtime)의 연도
    year_map = {}
    unclassified = []
    
    for f in normal_files:
        rel_path = f["rel_path"]
        name = f["name"]
        
        detected_year = None
        
        # 경로에서 학년도 감지 (예: 2011학년도, 2011학)
        match_path = re.search(r"(20\d{2})학년도", rel_path)
        if match_path:
            detected_year = match_path.group(1)
        else:
            # 파일명에서 학년도 감지
            match_name = re.search(r"(20\d{2})학년도", name)
            if match_name:
                detected_year = match_name.group(1)
            else:
                # 4자리 연도 숫자 감지 (2010 ~ 2027)
                match_num = re.search(r"\b(20[1-2]\d)\b", rel_path + "/" + name)
                if match_num:
                    detected_year = match_num.group(1)
                else:
                    # 2자리 학년도 감지 (예: 21학년도 -> 2021)
                    match_short = re.search(r"\b(\d{2})학년도", rel_path + "/" + name)
                    if match_short:
                        detected_year = "20" + match_short.group(1)
                        
        if not detected_year:
            # 수정 시간 활용
            dt = datetime.fromtimestamp(f["mtime"])
            if 2010 <= dt.year <= 2027:
                detected_year = str(dt.year)
                
        if detected_year:
            f["detected_year"] = detected_year
            year_map.setdefault(detected_year, []).append(f)
        else:
            unclassified.append(f)
            
    print("\n--- 분석 결과 요약 ---")
    print(f"1. 교과서 업체 자료 삭제 대상: {len(publisher_deletes)} 개")
    print(f"2. 학생 개인 사진 삭제 대상: {len(student_photo_deletes)} 개")
    print(f"3. 정상 정리 대상 파일: {len(normal_files)} 개")
    print("\n--- 정상 정리 대상 연도별 분포 ---")
    for y in sorted(year_map.keys()):
        print(f" - {y}학년도: {len(year_map[y])} 개")
    print(f" - 연도 미분류: {len(unclassified)} 개")
    
    # 결과 파일 저장
    summary_data = {
        "stats": {
            "total_scanned": len(files),
            "publisher_delete_count": len(publisher_deletes),
            "student_photo_delete_count": len(student_photo_deletes),
            "normal_file_count": len(normal_files),
            "unclassified_count": len(unclassified)
        },
        "year_stats": {y: len(year_map[y]) for y in year_map},
        "samples": {
            "publisher_deletes": [f["rel_path"] for f in publisher_deletes[:15]],
            "student_photo_deletes": [f["rel_path"] for f in student_photo_deletes[:15]],
            "normal_files": [f["rel_path"] for f in normal_files[:15]]
        }
    }
    
    out_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\analyze_new_sources_summary.json"
    with open(out_path, "w", encoding="utf-8") as out_f:
        json.dump(summary_data, out_f, ensure_ascii=False, indent=2)
    print(f"\n상세 분석 요약이 {out_path} 에 저장되었습니다.")

if __name__ == "__main__":
    analyze()
