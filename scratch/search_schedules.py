import os

def search_files(directory, keyword):
    results = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if keyword.lower() in file.lower():
                full_path = os.path.join(root, file)
                results.append(full_path)
    return results

def main():
    workspace = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
    keywords = ["학사", "일정", "jinhae", "진해고", "calendar", "schedule", "plan", "지필"]
    
    print("Searching workspace for schedule-related files...")
    for kw in keywords:
        found = search_files(workspace, kw)
        if found:
            print(f"\nKeyword '{kw}':")
            for path in found:
                print(f"  - {path} ({os.path.getsize(path)} bytes)")

if __name__ == '__main__':
    main()
