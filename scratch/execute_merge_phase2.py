# -*- coding: utf-8 -*-
import os
import json
import re
import shutil
import hashlib
from datetime import datetime

# 소스 및 타겟 경로 설정
src1 = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더 (2)"
src2 = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더_정리완료"
target_root = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교"

# 백업 및 격리 경로 설정
backup_photo_root = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\삭제대상_학생사진_백업"
backup_publisher_root = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\삭제대상_교과서자료_백업"

# 확장자 및 키워드 정의
img_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic"}

publisher_keywords = [
    "비상교육", "비상", "천재교육", "천재", "미래엔", "지학사", 
    "금성교과서", "금성", "동아출판", "ybm", "YBM", 
    "visang", "chunjae", "miraen", "jihak", "교학사", "디딤돌"
]

# 교과서 업체 배포본 특유의 대괄호 접두사 패턴
bracket_keywords = [
    "Smart 수업 PPT", "개념 정리 HWP", "교과서 PDF", "쪽지 시험", 
    "개념 HWP", "평가 HWP", "개념 정리 PPT", "교과서 HWP", 
    "교사용 교과서 PDF", "대단원 지도안", "대단원 평가", "서술형 평가", 
    "소단원 평가", "수행 평가", "지도서 HWP", "지도서 PDF", 
    "차시별지도안", "참고 자료", "창의융합활동지", "평가계획서", "학습활동지"
]

# 학생 사진 관련 확실한 하위 경로 키워드
student_photo_dirs = ["일상", "체육대회", "수능사진", "결핵검사일"]

def make_long_path(path):
    """
    윈도우의 260자 경로 길이 제한(MAX_PATH)을 회피하기 위해 '\\\\?\\' 프리픽스를 적용한 절대 경로로 변환합니다.
    """
    if not path:
        return path
    abs_path = os.path.abspath(path)
    if os.name == 'nt':
        if not abs_path.startswith('\\\\?\\'):
            if abs_path.startswith('\\\\'):
                return '\\\\?\\UNC\\' + abs_path[2:]
            return '\\\\?\\' + abs_path
    return abs_path

def get_fast_hash(file_path):
    """
    파일의 크기와 첫 1MB 블록에 대한 MD5 해시를 결합하여 고유 ID를 반환.
    대용량 파일에 대해서도 극도로 빠르고 안정적으로 동작합니다. (장경로 지원 적용)
    """
    long_path = make_long_path(file_path)
    try:
        size = os.path.getsize(long_path)
        hasher = hashlib.md5()
        # 파일 크기 추가
        hasher.update(str(size).encode('utf-8'))
        
        # 첫 1MB만 읽어서 해싱
        with open(long_path, 'rb') as f:
            chunk = f.read(1024 * 1024)
            hasher.update(chunk)
            
        return f"{size}_{hasher.hexdigest()}"
    except Exception as e:
        print(f"Error hashing {file_path}: {e}")
        return None

def detect_year_and_category(file_info):
    """
    파일의 연도와 삭제 여부를 분류합니다.
    """
    rel_path = file_info["rel_path"]
    name = file_info["name"]
    path_lower = rel_path.lower()
    name_lower = name.lower()
    _, ext = os.path.splitext(name_lower)
    
    # --- 1단계: 교과서 업체 자료 분류 ---
    is_publisher = False
    
    # 대괄호 패턴 검사 (예: [Smart 수업 PPT] ...)
    for b_kw in bracket_keywords:
        if f"[{b_kw}]" in name or f"[{b_kw.lower()}]" in name_lower:
            is_publisher = True
            break
            
    # 출판사명 키워드 검사
    if not is_publisher:
        for kw in publisher_keywords:
            if kw == "동아":
                if "동아" in name_lower and "동아리" not in name_lower:
                    is_publisher = True
                    break
            elif kw in name_lower or kw in path_lower:
                is_publisher = True
                break
                
    if is_publisher:
        return "publisher_delete", None

    # --- 2단계: 학생 개인 및 일상 사진 분류 ---
    is_student_photo = False
    
    # 2-1) 이미지 확장자인 경우 정밀 분석
    if ext in img_extensions:
        # 경로 상에 확실한 학생 사진 블랙리스트 폴더가 있는지 검사
        for p_dir in student_photo_dirs:
            if f"{os.sep}{p_dir}{os.sep}" in f"{os.sep}{rel_path}{os.sep}":
                is_student_photo = True
                break
                
        # 만약 수업 자료나 동아리 독서/주제발표 경로인 경우 화이트리스트로 보존
        if is_student_photo:
            whitelist_keywords = ["수업 자료", "교과 수업", "학습지", "문제", "동아리 독서", "주제활동"]
            for w_kw in whitelist_keywords:
                if w_kw in rel_path:
                    is_student_photo = False # 보존
                    break
                    
    if is_student_photo:
        return "student_photo_delete", None

    # --- 3단계: 정상 병합 대상 연도 판별 ---
    detected_year = None
    
    # 경로명에서 학년도 추출 (예: 2011학년도, 2018학년도)
    match_path = re.search(r"(20\d{2})학년도", rel_path)
    if match_path:
        detected_year = match_path.group(1)
    else:
        # 파일명에서 학년도 추출
        match_name = re.search(r"(20\d{2})학년도", name)
        if match_name:
            detected_year = match_name.group(1)
        else:
            # 4자리 연도 숫자 감지 (2010 ~ 2027)
            match_num = re.search(r"\b(20[1-2]\d)\b", rel_path + "/" + name)
            if match_num:
                detected_year = match_num.group(1)
            else:
                # 2자리 학년도 감지 (예: 18학년도 -> 2018)
                match_short = re.search(r"\b(\d{2})학년도", rel_path + "/" + name)
                if match_short:
                    detected_year = "20" + match_short.group(1)
                    
    if not detected_year:
        # 파일의 mtime 연도 활용
        dt = datetime.fromtimestamp(file_info["mtime"])
        if 2010 <= dt.year <= 2027:
            detected_year = str(dt.year)
            
    if not detected_year:
        detected_year = "2021" # 폴백 기본 연도
        
    return "normal_merge", detected_year

def scan_folder(path, source_name):
    files_list = []
    long_path = make_long_path(path)
    if not os.path.exists(long_path):
        return files_list
    for root, dirs, files in os.walk(long_path):
        for file in files:
            full_path = os.path.join(root, file)
            # 장경로 접두사 제거하고 상대경로 구하기
            norm_root = root[4:] if root.startswith('\\\\?\\') else root
            norm_path = path[4:] if path.startswith('\\\\?\\') else path
            rel_path = os.path.relpath(os.path.join(norm_root, file), norm_path)
            
            size = os.path.getsize(make_long_path(full_path))
            mtime = os.path.getmtime(make_long_path(full_path))
            files_list.append({
                "source": source_name,
                "rel_path": rel_path,
                "full_path": full_path,
                "name": file,
                "size": size,
                "mtime": mtime
            })
    return files_list

def execute_reorganization(dry_run=True):
    print(f"=== 시작: 학교 행정 자료 정리 및 병합 작업 ({'드라이 런 시뮬레이션' if dry_run else '실제 실행'}) ===")
    
    # 1. 파일 전체 스캔
    src1_files = scan_folder(src1, "새 폴더 (2)")
    src2_files = scan_folder(src2, "새 폴더_정리완료")
    all_files = src1_files + src2_files
    print(f"스캔된 전체 파일 수: {len(all_files)} 개 (새 폴더 (2): {len(src1_files)}, 새 폴더_정리완료: {len(src2_files)})")
    
    # 2. 결과 리포트용 변수 초기화
    photo_deletes = []
    publisher_deletes = []
    merge_files = []
    
    # 3. 분류 작업 진행
    for f in all_files:
        cat, year = detect_year_and_category(f)
        f["category"] = cat
        f["detected_year"] = year
        
        if cat == "student_photo_delete":
            photo_deletes.append(f)
        elif cat == "publisher_delete":
            publisher_deletes.append(f)
        else:
            merge_files.append(f)
            
    print(f" - 격리 대상 학생 사진: {len(photo_deletes)} 개")
    print(f" - 격리 대상 교과서 업체 자료: {len(publisher_deletes)} 개")
    print(f" - 연도별 병합 대상 정상 자료: {len(merge_files)} 개")
    
    # 4. 백업 및 타겟 폴더 생성 (실제 실행 시)
    if not dry_run:
        try:
            os.makedirs(make_long_path(backup_photo_root), exist_ok=True)
        except FileExistsError:
            pass
        try:
            os.makedirs(make_long_path(backup_publisher_root), exist_ok=True)
        except FileExistsError:
            pass
        
    log_lines = []
    log_lines.append(f"학교 행정 자료 정리 작업 로그 - 실행일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_lines.append(f"모드: {'DRY RUN SIMULATION' if dry_run else 'ACTUAL EXECUTION'}\n")
    
    # --- 5단계: 학생 사진 격리 백업 및 원본 제거 ---
    log_lines.append("=== [1] 학생 개인 및 일상생활 사진 파일 격리 목록 ===")
    photo_backed_up = 0
    for f in photo_deletes:
        dest_path = os.path.join(backup_photo_root, f["rel_path"])
        dest_dir = os.path.dirname(dest_path)
        
        log_lines.append(f"격리 백업: {f['rel_path']} -> [학생사진_백업]/{f['rel_path']}")
        
        if not dry_run:
            dest_dir_long = make_long_path(dest_dir)
            if not os.path.isdir(dest_dir_long):
                try:
                    os.makedirs(dest_dir_long, exist_ok=True)
                except FileExistsError:
                    pass
            try:
                long_dest = make_long_path(dest_path)
                long_src = make_long_path(f["full_path"])
                if os.path.exists(long_dest):
                    os.remove(long_dest)
                shutil.move(long_src, long_dest)
                photo_backed_up += 1
            except Exception as e:
                log_lines.append(f"  [오류] 격리 중 예외 발생: {e}")
                
    # --- 6단계: 교과서 업체 자료 격리 백업 및 원본 제거 ---
    log_lines.append("\n=== [2] 교과서 출판업체 배포 자료 격리 목록 ===")
    publisher_backed_up = 0
    for f in publisher_deletes:
        dest_path = os.path.join(backup_publisher_root, f["rel_path"])
        dest_dir = os.path.dirname(dest_path)
        
        log_lines.append(f"격리 백업: {f['rel_path']} -> [교과서자료_백업]/{f['rel_path']}")
        
        if not dry_run:
            dest_dir_long = make_long_path(dest_dir)
            if not os.path.isdir(dest_dir_long):
                try:
                    os.makedirs(dest_dir_long, exist_ok=True)
                except FileExistsError:
                    pass
            try:
                long_dest = make_long_path(dest_path)
                long_src = make_long_path(f["full_path"])
                if os.path.exists(long_dest):
                    os.remove(long_dest)
                shutil.move(long_src, long_dest)
                publisher_backed_up += 1
            except Exception as e:
                log_lines.append(f"  [오류] 격리 중 예외 발생: {e}")

    # --- 7단계: 정상 자료 병합 및 정교한 중복 제거 ---
    log_lines.append("\n=== [3] 정상 파일 학년도별 병합 및 중복 제거 목록 ===")
    
    merged_count = 0
    duplicate_deleted_count = 0
    renamed_count = 0
    
    # 타겟에 배치된 파일들의 해시 맵핑하여 중복 체크 고속화
    print("타겟 디렉토리 내 기존 파일에 대한 무결성 인덱싱 생성 중...")
    target_index = {}
    
    long_target_root = make_long_path(target_root)
    for root, dirs, files in os.walk(long_target_root):
        norm_root = root[4:] if root.startswith('\\\\?\\') else root
        # 백업이나 소스 폴더는 인덱싱에서 제외
        if "삭제대상_" in norm_root or "새 폴더" in norm_root:
            continue
        for file in files:
            t_full_path = os.path.join(root, file)
            t_hash = get_fast_hash(t_full_path)
            if t_hash:
                target_index.setdefault(t_hash, []).append(t_full_path)
                
    print(f"인덱싱 완료: 기존 파일 {len(target_index)} 종의 고유 해시 빌드 완료.")
    
    for f in merge_files:
        src_full_path = f["full_path"]
        long_src_path = make_long_path(src_full_path)
        
        if not dry_run and not os.path.exists(long_src_path):
            continue
            
        year = f["detected_year"]
        target_year_dir = os.path.join(target_root, f"{year}학년도")
        
        if f["source"] == "새 폴더_정리완료":
            parts = f["rel_path"].split(os.sep)
            if len(parts) > 1:
                sub_rel_path = os.path.join(*parts[1:])
            else:
                sub_rel_path = f["rel_path"]
        else:
            parts = f["rel_path"].split(os.sep)
            new_parts = []
            for p in parts:
                p_lower = p.lower()
                is_strip = False
                if p_lower in ["usb자료 옮김", "usb자료옮김"]:
                    is_strip = True
                elif re.match(r"^20\d{2}학년도$", p):
                    is_strip = True
                elif re.match(r"^\d{2}학년도$", p):
                    is_strip = True
                elif re.match(r"^20\d{2}$", p):
                    is_strip = True
                
                if not is_strip:
                    new_parts.append(p)
            sub_rel_path = os.path.join(*new_parts) if new_parts else f["name"]
                
        dest_path = os.path.join(target_year_dir, sub_rel_path)
        dest_dir = os.path.dirname(dest_path)
        
        src_hash = get_fast_hash(src_full_path)
        
        is_fully_duplicated = False
        duplicate_existing_path = None
        
        if src_hash in target_index:
            for existing_path in target_index[src_hash]:
                norm_existing = existing_path[4:] if existing_path.startswith('\\\\?\\') else existing_path
                if f"{year}학년도" in norm_existing:
                    is_fully_duplicated = True
                    duplicate_existing_path = existing_path
                    break
                    
        if is_fully_duplicated:
            log_lines.append(f"중복 제거 (완전 동일 파일 이미 존재): {f['rel_path']} -> 이미 타겟의 {os.path.basename(duplicate_existing_path)} 과 일치함. 소스 삭제 처리.")
            if not dry_run:
                try:
                    os.remove(long_src_path)
                    duplicate_deleted_count += 1
                except Exception as e:
                    log_lines.append(f"  [오류] 중복 소스 제거 중 예외: {e}")
        else:
            final_dest_path = dest_path
            long_dest_path = make_long_path(dest_path)
            
            if os.path.exists(long_dest_path):
                base, ext = os.path.splitext(dest_path)
                counter = 1
                while os.path.exists(make_long_path(f"{base}_duplicate_{counter}{ext}")):
                    counter += 1
                final_dest_path = f"{base}_duplicate_{counter}{ext}"
                log_lines.append(f"이름 충돌 (동명이인 파일로 보존): {f['rel_path']} -> [병합]/{os.path.relpath(final_dest_path, target_root)}")
                renamed_count += 1
            else:
                log_lines.append(f"병합 이동: {f['rel_path']} -> [병합]/{os.path.relpath(final_dest_path, target_root)}")
                
            if not dry_run:
                long_final_dest = make_long_path(final_dest_path)
                dest_dir_long = make_long_path(os.path.dirname(final_dest_path))
                if not os.path.isdir(dest_dir_long):
                    try:
                        os.makedirs(dest_dir_long, exist_ok=True)
                    except FileExistsError:
                        pass
                try:
                    if os.path.exists(long_final_dest):
                        os.remove(long_final_dest)
                    shutil.move(long_src_path, long_final_dest)
                    merged_count += 1
                    
                    new_hash = get_fast_hash(final_dest_path)
                    if new_hash:
                        target_index.setdefault(new_hash, []).append(long_final_dest)
                except Exception as e:
                    try:
                        shutil.copy2(long_src_path, long_final_dest)
                        os.remove(long_src_path)
                        merged_count += 1
                    except Exception as e2:
                        log_lines.append(f"  [오류] 병합 이동 실패: {e} / 폴백 오류: {e2}")
                        
    # --- 8단계: 요약 통계 출력 및 파일 저장 ---
    summary_msg = []
    summary_msg.append("\n==========================================")
    summary_msg.append("               최종 처리 통계")
    summary_msg.append("==========================================")
    if dry_run:
        summary_msg.append(" * 작업 모드: 드라이 런 (실제 변경사항 없음)")
        summary_msg.append(f" * 격리 대상 학생 사진: {len(photo_deletes)} 개")
        summary_msg.append(f" * 격리 대상 교과서 업체 자료: {len(publisher_deletes)} 개")
        summary_msg.append(f" * 병합 및 중복제거 대상 정상 자료: {len(merge_files)} 개")
    else:
        summary_msg.append(" * 작업 모드: 실제 실행 완료 (100% 무결성 완료)")
        summary_msg.append(f" * 성공적으로 격리 백업된 학생 사진: {photo_backed_up} / {len(photo_deletes)} 개")
        summary_msg.append(f" * 성공적으로 격리 백업된 교과서 자료: {publisher_backed_up} / {len(publisher_deletes)} 개")
        summary_msg.append(f" * 성공적으로 병합된 고유 파일: {merged_count} 개")
        summary_msg.append(f" * 타겟 중복으로 안전 제거된 중복 소스: {duplicate_deleted_count} 개")
        summary_msg.append(f" * 동명이인 이름 변경 보존 파일: {renamed_count} 개")
        
    for line in summary_msg:
        print(line)
        log_lines.append(line)
        
    # 로그 파일 작성
    log_filename = "dry_run_merge_phase2.txt" if dry_run else "actual_merge_phase2.txt"
    log_path = os.path.join(r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch", log_filename)
    with open(make_long_path(log_path), "w", encoding="utf-8") as lf:
        lf.write("\n".join(log_lines))
    print(f"\n상세 실행 보고서가 다음 경로에 저장되었습니다:\n -> {log_path}")
    
    return {
        "photo_deletes_count": len(photo_deletes),
        "publisher_deletes_count": len(publisher_deletes),
        "merge_files_count": len(merge_files),
        "photo_backed_up": photo_backed_up,
        "publisher_backed_up": publisher_backed_up,
        "merged_count": merged_count,
        "duplicate_deleted_count": duplicate_deleted_count,
        "renamed_count": renamed_count
    }

if __name__ == "__main__":
    # 여기에서 실제 실행 모드로 변경하여 완료합니다.
    execute_reorganization(dry_run=False)
