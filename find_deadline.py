import os
import shutil
import re

def find_and_copy_file():
    base_dir = r"D:\OneDrive - 寃쎌긽?⑤룄援먯쑁泥?諛뷀깢 ?붾㈃\吏꾪빐怨좊벑?숆탳\2026?숇뀈??
    search_keywords = ["蹂듦텒湲곌툑", "?됯??꾩썝"]
    
    found_file = None
    for root, dirs, files in os.walk(base_dir):
        # ?대뜑紐낆뿉 ?ㅼ썙?쒓? ?ы븿?섏뼱 ?덈뒗吏 ?뺤씤
        if any(kw in root for kw in search_keywords):
            for f in files:
                if "蹂몃Ц" in f and f.endswith(".pdf"):
                    found_file = os.path.join(root, f)
                    break
        if found_file:
            break
            
    if found_file:
        destination = os.path.join(os.environ.get("TEMP", "C:\\temp"), "notice_temp.pdf")
        if not os.path.exists(os.path.dirname(destination)):
            os.makedirs(os.path.dirname(destination))
        shutil.copy(found_file, destination)
        print(f"SUCCESS: {found_file} copied to {destination}")
        return destination
    else:
        print("FAILURE: File not found.")
        return None

if __name__ == "__main__":
    find_and_copy_file()
