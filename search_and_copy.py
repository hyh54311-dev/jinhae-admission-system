import os
import shutil

def find_latest_4793():
    base = r"D:\OneDrive - 寃쎌긽?⑤룄援먯쑁泥?諛뷀깢 ?붾㈃\吏꾪빐怨좊벑?숆탳\2026?숇뀈??
    for root, dirs, files in os.walk(base):
        for f in files:
            if "4793" in f and "蹂몃Ц" in f and f.endswith(".pdf"):
                full_path = os.path.join(root, f)
                dest = os.path.join(os.environ.get("TEMP", "C:\\temp"), "important_notice.pdf")
                shutil.copy(full_path, dest)
                print(f"FOUND: {full_path}")
                print(f"COPIED TO: {dest}")
                return
    print("NOT FOUND")

if __name__ == "__main__":
    find_latest_4793()
