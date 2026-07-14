import os
import glob
import datetime

target_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교"
now = datetime.datetime.now()
five_minutes_ago = now - datetime.timedelta(minutes=5)

print(f"Checking for PDFs created in {target_dir} since {five_minutes_ago.strftime('%Y-%m-%d %H:%M:%S')}...")

pdf_files = glob.glob(os.path.join(target_dir, "**", "*.pdf"), recursive=True)
recent_pdfs = []

for pdf_path in pdf_files:
    try:
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(pdf_path))
        if mtime > five_minutes_ago:
            recent_pdfs.append((pdf_path, mtime))
    except Exception:
        pass

# 수정 시간 기준 내림차순 정렬
recent_pdfs.sort(key=lambda x: x[1], reverse=True)

print(f"Total PDFs found: {len(pdf_files)}")
print(f"Recent PDFs created/modified in last 5 minutes: {len(recent_pdfs)}")
for i, (path, mtime) in enumerate(recent_pdfs[:15]):
    print(f"[{i+1}] {mtime.strftime('%H:%M:%S')} - {os.path.basename(path)}")
