# -*- coding: utf-8 -*-
import os
import shutil

src_root = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\새 폴더 (2)"
target_root = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교"

wrong_moves = [
    ("1. 문학 수업 자료\\난쏘공 발표 자료\\2반\\2220 조예원.pptx", "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\2반_duplicate_2"),
    ("1. 문학 수업 자료\\난쏘공 발표 자료\\3반\\20304 여진쓰~~.pptx", "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\3반"),
    ("1. 문학 수업 자료\\난쏘공 발표 자료\\3반\\20314 이서영.pptx", "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\3반_duplicate_1"),
    ("1. 문학 수업 자료\\난쏘공 발표 자료\\3반\\20316 이지후 국어 세특 피피티.pptx", "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\3반_duplicate_2"),
    ("1. 문학 수업 자료\\난쏘공 발표 자료\\4반\\20410.pptx", "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\4반"),
    ("1. 문학 수업 자료\\난쏘공 발표 자료\\8반\\20811 박진서 난쏘공.pptx", "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\8반_duplicate_1"),
    ("1. 문학 수업 자료\\난쏘공 발표 자료\\8반\\20817이나래.pptx", "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\8반_duplicate_2"),
    ("1. 문학 수업 자료\\난쏘공 발표 자료\\8반\\20818이유진.pptx", "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\8반_duplicate_3"),
    ("1. 문학 수업 자료\\난쏘공 발표 자료\\9반\\20904 김아연.pptx", "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\9반"),
    ("1. 문학 수업 자료\\난쏘공 발표 자료\\9반\\20910 박주미.pptx", "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\9반_duplicate_1"),
    ("1. 문학 수업 자료\\난쏘공 발표 자료\\9반\\20918 정채은 문학.pptx", "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\9반_duplicate_2"),
    ("1. 문학 수업 자료\\난쏘공 발표 자료\\9반\\20923 최우영.pptx", "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\9반_duplicate_3"),
    ("2. 언어와 매체 수업 자료\\2020 국어 학습지(피동과 사동 점검하기) - 학생용.hwp", "2020학년도\\2. 언어와 매체 수업 자료"),
    ("usb자료 옮김\\수업 전 잡담 자료\\2019. 01. 31.(목) 하이원 카빙 업다운 연습 중 사고.MP4", "2019학년도\\수업 전 잡담 자료"),
    ("자율동아리 독서 토론\\[차클 마스터클라스] 르브론 제임스가 받는 연봉은 공정할까_🙄🏀 능력주의란(Meritocracy) 무엇인가!｜마이클 샌델｜JTBC 210204 방송.mp4", "2021학년도\\자율동아리 독서 토론_duplicate_1"),
    ("창의주제활동 발표 자료\\새 폴더\\his_scrsp41_r00_2019.xls", "2021학년도\\창의주제활동 발표 자료\\새 폴더"),
]

def make_long_path(path):
    if not path:
        return path
    abs_path = os.path.abspath(path)
    if os.name == 'nt':
        if not abs_path.startswith('\\\\?\\'):
            if abs_path.startswith('\\\\'):
                return '\\\\?\\UNC\\' + abs_path[2:]
            return '\\\\?\\' + abs_path
    return abs_path

print("=== [복구 작업 시작] 잘못 병합된 파일들 원위치 및 타겟 찌꺼기 소거 ===")

restored_count = 0
for src_rel, dest_rel in wrong_moves:
    original_src = os.path.join(src_root, src_rel)
    wrong_dest = os.path.join(target_root, dest_rel)
    
    long_wrong_dest = make_long_path(wrong_dest)
    long_original_src = make_long_path(original_src)
    
    if os.path.exists(long_wrong_dest) and os.path.isfile(long_wrong_dest):
        # 원본 소스 디렉토리 생성
        src_dir = os.path.dirname(long_original_src)
        if not os.path.isdir(src_dir):
            try:
                os.makedirs(src_dir, exist_ok=True)
            except FileExistsError:
                pass
                
        # 복구 이동
        try:
            if os.path.exists(long_original_src):
                os.remove(long_original_src)
            shutil.move(long_wrong_dest, long_original_src)
            print(f"복구 성공: {dest_rel} -> [새 폴더 (2)]/{src_rel}")
            restored_count += 1
        except Exception as e:
            print(f"[오류] 복구 실패 ({dest_rel}): {e}")
    else:
        print(f"이미 복구되었거나 파일 없음: {dest_rel}")

# 타겟 디렉토리에 잘못 생성된 파일들(폴더가 되었어야 하나 파일이 된 것들) 최종 삭제
print("\n=== [클린업 시작] 타겟 디렉토리 내 방해 파일 삭제 ===")
files_to_clean = [
    "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\1반",
    "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\2반",
    "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\2반_duplicate_1",
    "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\2반_duplicate_2",
    "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\3반",
    "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\3반_duplicate_1",
    "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\3반_duplicate_2",
    "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\4반",
    "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\9반",
    "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\9반_duplicate_1",
    "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\9반_duplicate_2",
    "2021학년도\\1. 문학 수업 자료\\난쏘공 발표 자료\\9반_duplicate_3",
    "2020학년도\\2. 언어와 매체 수업 자료",
    "2019학년도\\수업 전 잡담 자료",
    "2021학년도\\자율동아리 독서 토론_duplicate_1",
    "2021학년도\\창의주제활동 발표 자료\\새 폴더",
]

cleaned_count = 0
for rel_path in files_to_clean:
    full_path = os.path.join(target_root, rel_path)
    long_path = make_long_path(full_path)
    if os.path.exists(long_path):
        if os.path.isfile(long_path):
            try:
                os.remove(long_path)
                print(f"방해 파일 삭제 성공: {rel_path}")
                cleaned_count += 1
            except Exception as e:
                print(f"[오류] 파일 삭제 실패 ({rel_path}): {e}")
        elif os.path.isdir(long_path):
            # 5반, 8반처럼 원래 디렉토리인 경우는 지우지 않음
            print(f"디렉토리 보존: {rel_path}")
            
print(f"\n=== 작업 결과: 복구 완료 {restored_count}개 | 클린업 완료 {cleaned_count}개 ===")
