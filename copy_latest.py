import os
import shutil

def find_file():
    path = r"D:\OneDrive - 寃쎌긽?⑤룄援먯쑁泥?諛뷀깢 ?붾㈃\吏꾪빐怨좊벑?숆탳\2026?숇뀈???낅Т(?ν븰湲?諛??낇븰?띾낫)\2. ?ν븰湲??쒓뎅?ν븰?щ떒) 2026???쒓뎅?ν븰?щ떒 蹂듦텒湲곌툑 轅덉궗?ㅻ━ ?곗닔 ?ν븰?ъ뾽 ?됯??꾩썝 ?щ쭩???쒖텧"
    filename ="(吏꾪빐怨좊벑?숆탳-4793 (蹂몃Ц) 寃쎌긽?⑤룄援먯쑁泥?以묐벑援먯쑁怨? [?쒖텧] 2026???쒓뎅?ν븰?щ떒 蹂듦텒湲곌툑 轅덉궗?ㅻ━ ?곗닔 ?ν븰?ъ뾽 ?됯??꾩썝 ?щ쭩???쒖텧.pdf"
    full_path = os.path.join(path, filename)
    
    if os.path.exists(full_path):
        dest = os.path.join(os.environ.get("TEMP", "C:\\temp"), "notice_4793.pdf")
        shutil.copy(full_path, dest)
        print(f"COPIED: {dest}")
    else:
        print("NOT FOUND")

if __name__ == "__main__":
    find_file()
