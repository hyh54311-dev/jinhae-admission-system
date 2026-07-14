import os

def main():
    path = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Antigravity_Full_Suite.bat')
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            with open("scratch/startup_bat_content.txt", "w", encoding="utf-8") as f:
                f.write(content)
            print("Successfully read and saved to scratch/startup_bat_content.txt")
        except Exception as e:
            print("Error reading file:", e)
    else:
        print("File does not exist.")

if __name__ == '__main__':
    main()
