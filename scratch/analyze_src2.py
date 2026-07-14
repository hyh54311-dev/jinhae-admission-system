# -*- coding: utf-8 -*-
import os
import json

src2 = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더_정리완료"

def main():
    if not os.path.exists(src2):
        print("src2 path does not exist")
        return
        
    files_by_year = {}
    total_files = 0
    
    # 상위 경로 몇 단계가 연도인지 분석
    for root, dirs, files in os.walk(src2):
        for file in files:
            total_files += 1
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, src2)
            
            # rel_path는 '2011학년도\학급 및 학생\이름표6-4.pdf' 같은 형식임
            parts = rel_path.split(os.sep)
            if parts:
                year_dir = parts[0] # '2011학년도' 등
                files_by_year.setdefault(year_dir, []).append(rel_path)
                
    print(f"Total files in src2: {total_files}")
    for ydir in sorted(files_by_year.keys()):
        print(f" - Folder '{ydir}': {len(files_by_year[ydir])} files")
        
    # 각 연도별 샘플 5개씩 출력
    print("\nSample paths in src2:")
    for ydir in sorted(files_by_year.keys()):
        print(f"[{ydir}] sample files:")
        for path in files_by_year[ydir][:5]:
            print(f"   {path}")

if __name__ == "__main__":
    main()
