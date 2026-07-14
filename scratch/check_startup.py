import os
import sys

def main():
    user_startup = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup')
    common_startup = os.path.expandvars(r'%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\StartUp')
    
    print("=== User Startup Folder ===")
    print(f"Path: {user_startup}")
    if os.path.exists(user_startup):
        for f in os.listdir(user_startup):
            print(f"- {f}")
    else:
        print("Does not exist.")
        
    print("\n=== Common Startup Folder ===")
    print(f"Path: {common_startup}")
    if os.path.exists(common_startup):
        for f in os.listdir(common_startup):
            print(f"- {f}")
    else:
        print("Does not exist.")

if __name__ == '__main__':
    main()
