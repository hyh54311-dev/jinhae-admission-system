import win32gui
import win32con
import sys

def enum_top_windows(hwnd, lparam):
    class_name = win32gui.GetClassName(hwnd)
    title = win32gui.GetWindowText(hwnd)
    # Filter for standard dialogs, windows with Hwp class, or titles mentioning Hwp/Hancom/한글
    if class_name == "#32770" or "한글" in title or "Hwp" in class_name or "Hancom" in title:
        print(f"Top HWND: {hwnd}, Class: {class_name}, Title: '{title}'")
        def enum_child_proc(child_hwnd, param):
            c_class = win32gui.GetClassName(child_hwnd)
            c_text = win32gui.GetWindowText(child_hwnd)
            print(f"  Child HWND: {child_hwnd}, Class: {c_class}, Text: '{c_text}'")
            return True
        try:
            win32gui.EnumChildWindows(hwnd, enum_child_proc, None)
        except Exception as e:
            print(f"  Error enum child: {e}")
    return True

print("Enumerating windows...")
win32gui.EnumWindows(enum_top_windows, None)
print("Done.")
