# -*- coding: utf-8 -*-
import os
import shutil
import re

class HistoricalOrganizer:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.source_root = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\0. 이전 학년도 자료\2021학년도 자료"
        self.target_root = self.source_root
        self.moves = [] # tuples of (src_file, dst_file)
        self.deletes = [] # lists of lock files to delete
        self.empty_dirs_to_clean = [] # dirs that should be cleaned up if empty
        
    def plan_organization(self):
        # We walk through all files recursively in source_root and determine their target paths
        for root, dirs, files in os.walk(self.source_root):
            # Check if this directory itself is a system-created or temporary empty directory
            rel_dir = os.path.relpath(root, self.source_root)
            
            # Skip walking into target directories if they already exist (to avoid infinite loops or re-moving)
            # However, since they don't exist yet, this is safe. But let's be careful.
            path_parts = rel_dir.split(os.sep)
            if path_parts[0] in ['학급 경영', '수업', '기획(학교행사 및 홍보)', '창체 동아리']:
                continue
                
            for file in files:
                src_path = os.path.join(root, file)
                
                # 1. Safely handle temporary lock files
                if file.startswith("~$"):
                    self.deletes.append(src_path)
                    continue
                
                # 2. Determine target path based on relative path parts or filename patterns
                target_rel_path = self.get_target_rel_path(rel_dir, file)
                if target_rel_path:
                    dst_path = os.path.join(self.target_root, target_rel_path)
                    self.moves.append((src_path, dst_path))
                    
        # Find all old directories to potentially clean up
        for root, dirs, files in os.walk(self.source_root, topdown=False):
            rel_dir = os.path.relpath(root, self.source_root)
            path_parts = rel_dir.split(os.sep)
            if rel_dir != "." and path_parts[0] not in ['학급 경영', '수업', '기획(학교행사 및 홍보)', '창체 동아리']:
                self.empty_dirs_to_clean.append(root)

    def get_target_rel_path(self, rel_dir, filename):
        parts = rel_dir.split(os.sep)
        first_dir = parts[0] if parts and parts[0] != "." else ""
        
        # Mapping rules based on the source folder
        if first_dir == "2021학년도 정책제안발표회":
            # Event presentation
            return os.path.join("기획(학교행사 및 홍보)", "정책제안발표회", os.path.relpath(os.path.join(rel_dir, filename), "2021학년도 정책제안발표회"))
            
        elif first_dir == "학교교육과정 설명회 자료(온라인)":
            # Curriculum briefing event
            return os.path.join("기획(학교행사 및 홍보)", "교육과정설명회", os.path.relpath(os.path.join(rel_dir, filename), "학교교육과정 설명회 자료(온라인)"))
            
        elif first_dir == "2학년 1반":
            # Homeroom class organization / student charts
            return os.path.join("학급 경영", "학급 현황", filename)
            
        elif first_dir == "출결 관련":
            # homeroom attendance folder
            return os.path.join("학급 경영", "출결 관련", os.path.relpath(os.path.join(rel_dir, filename), "출결 관련"))
            
        elif first_dir == "야간자율학습 출석부":
            # 야자 출석부 is part of class attendance/records
            return os.path.join("학급 경영", "야간자율학습", filename)
            
        elif first_dir == "생기부 자료":
            # Check files in '생기부 자료'
            sub_path = os.path.relpath(os.path.join(rel_dir, filename), "생기부 자료")
            sub_parts = sub_path.split(os.sep)
            
            # File specific mappings
            if filename == "2021학년도 2학년 생활기록부(2학년 1반) 기록 파일.xlsx":
                return os.path.join("학급 경영", "생활기록부", filename)
            elif filename == "2021학년도 2학년 생활기록부(창체-동아리) 기록 파일.xlsx":
                return os.path.join("창체 동아리", filename)
            elif filename == "경상남도교육청 중등교육과_학생부 종합 지원센터 질의·회신사례집(최종).pdf":
                return os.path.join("학급 경영", "생활기록부", filename)
                
            # Under '1학기'
            if len(sub_parts) > 1 and sub_parts[0] == "1학기":
                if "NEIS입력 내용" in filename:
                    return os.path.join("학급 경영", "생활기록부", filename)
                elif "세특-1학기 문학" in filename:
                    return os.path.join("수업", "문학", filename)
                elif "문학 석차" in filename:
                    return os.path.join("수업", "문학", filename)
                elif "문학 학습 내용 정리" in filename:
                    return os.path.join("수업", "문학", filename)
                else:
                    return os.path.join("수업", "기타", filename)
                    
            # Under '2학기'
            elif len(sub_parts) > 1 and sub_parts[0] == "2학기":
                if "생기부 점검 계획" in filename or "학교생활기록부 점검표" in filename:
                    return os.path.join("학급 경영", "생활기록부", filename)
                elif "점검 일정" in filename or "현장 점검 결과" in filename:
                    return os.path.join("학급 경영", "생활기록부", filename)
                elif "세특-2학기 언어와 매체" in filename:
                    return os.path.join("수업", "언어와 매체", filename)
                elif "꽃그리기" in filename:
                    return os.path.join("수업", "활동자료", filename)
                else:
                    return os.path.join("수업", "기타", filename)
            
            # Default fallback for biological elements inside 생기부 자료
            return os.path.join("학급 경영", "생활기록부", filename)
            
        elif first_dir == "새 폴더":
            # Empty folder, no files should exist
            return None
            
        # Any loose files in root
        return os.path.join("학급 경영", "기타", filename)

    def execute(self):
        log = []
        log.append(f"=== {'DRY RUN' if self.dry_run else 'ACTUAL EXECUTION'} ===")
        
        # Create directories in dry run or actual move
        target_dirs = set(os.path.dirname(dst) for src, dst in self.moves)
        for d in sorted(target_dirs):
            log.append(f"Directory creation: {d}")
            if not self.dry_run:
                os.makedirs(d, exist_ok=True)
                
        # Move files
        for src, dst in self.moves:
            # Handle destination conflict
            final_dst = dst
            if not self.dry_run:
                counter = 1
                base, ext = os.path.splitext(dst)
                while os.path.exists(final_dst):
                    final_dst = f"{base}_{counter}{ext}"
                    counter += 1
            
            log.append(f"Move: {src} -> {final_dst}")
            if not self.dry_run:
                shutil.move(src, final_dst)
                
        # Delete lock files
        for item in self.deletes:
            log.append(f"Delete temporary file: {item}")
            if not self.dry_run:
                if os.path.exists(item):
                    os.remove(item)
                    
        # Clean empty folders
        if not self.dry_run:
            # We do multiple passes of empty directory removal in case nested empty folders become empty
            import stat
            for _ in range(3):
                for d in self.empty_dirs_to_clean:
                    if os.path.exists(d) and os.path.isdir(d):
                        try:
                            if not os.listdir(d): # directory is empty
                                log.append(f"Clean up empty directory: {d}")
                                os.chmod(d, stat.S_IWRITE)
                                os.rmdir(d)
                        except Exception as e:
                            log.append(f"Failed to clean up empty directory {d}: {e}")
        else:
            for d in self.empty_dirs_to_clean:
                log.append(f"Will clean up empty directory: {d}")
                
        return log

if __name__ == "__main__":
    import sys
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        dry_run = False
        
    organizer = HistoricalOrganizer(dry_run=dry_run)
    organizer.plan_organization()
    log = organizer.execute()
    
    mode_name = "actual" if not dry_run else "dry_run"
    log_path = rf"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\{mode_name}_move.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log))
    print(f"[{mode_name.upper()}] Execution finished. Log saved to {log_path}!")

