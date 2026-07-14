import os

def create_shortcut(desktop_path, name, url):
    shortcut_path = os.path.join(desktop_path, f"{name}.url")
    content = f"[InternetShortcut]\nURL={url}\n"
    try:
        # Create directory if not exists
        os.makedirs(desktop_path, exist_ok=True)
        with open(shortcut_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created shortcut at: {shortcut_path}")
    except Exception as e:
        print(f"Failed to create shortcut at {shortcut_path}: {e}")

def main():
    doc_url = "https://docs.google.com/document/d/1UkV1Vc_8m_vO7bzhS5JpjE4SwIZu8Ocs24rS7PPX5EE/edit?usp=drivesdk"
    shortcut_name = "AI동행_분과교육_신청_회신내용"
    
    # Path 1: OneDrive Desktop
    onedrive_desktop = r"d:\OneDrive - 경상남도교육청\바탕 화면"
    create_shortcut(onedrive_desktop, shortcut_name, doc_url)
    
    # Path 2: Standard Local Desktop
    local_desktop = r"C:\Users\admin\Desktop"
    create_shortcut(local_desktop, shortcut_name, doc_url)

if __name__ == '__main__':
    main()
