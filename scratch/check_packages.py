import sys

sys.stdout.reconfigure(encoding='utf-8')

for pkg in ['selenium', 'playwright', 'gspread', 'google.auth', 'requests']:
    try:
        __import__(pkg)
        print(f"Package '{pkg}' is INSTALLED")
    except ImportError:
        print(f"Package '{pkg}' is NOT installed")
