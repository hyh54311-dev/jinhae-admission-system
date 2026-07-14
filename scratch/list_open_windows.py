import sys
import win32gui

# UTF-8 출력 강제 (오류 방지)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def winEnumHandler(hwnd, ctx):
    if win32gui.IsWindowVisible(hwnd):
        try:
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            if title:
                # CP949 콘솔 출력을 위해 안전하게 인코딩 처리
                log_msg = f"HWND: {hwnd} | Class: {class_name} | Title: {title}"
                try:
                    print(log_msg)
                except UnicodeEncodeError:
                    print(log_msg.encode('cp949', errors='replace').decode('cp949'))
        except Exception:
            pass

print("--- Listing Visible Windows ---")
win32gui.EnumWindows(winEnumHandler, None)
