import sys
import win32gui
import win32process

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

target_pid = 24736  # tasklist에서 확인한 Hwp.exe의 PID

def enum_windows_callback(hwnd, extra):
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
    except:
        return True
        
    if pid == target_pid:
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        visible = win32gui.IsWindowVisible(hwnd)
        print(f"HWND: {hwnd} | Class: {class_name} | Visible: {visible} | Title: {title}")
        
        # 자식 윈도우 출력
        children = []
        def enum_child_callback(child_hwnd, param):
            c_title = win32gui.GetWindowText(child_hwnd)
            c_class = win32gui.GetClassName(child_hwnd)
            children.append((child_hwnd, c_class, c_title))
            return True
            
        try:
            win32gui.EnumChildWindows(hwnd, enum_child_callback, None)
            for c_hwnd, c_class, c_title in children:
                print(f"  [Child] HWND: {c_hwnd} | Class: {c_class} | Text: {c_title}")
        except Exception as e:
            print(f"  Error enumerating children: {e}")
        print("-" * 60)
    return True

print(f"=== Hwp.exe (PID: {target_pid}) Windows ===")
win32gui.EnumWindows(enum_windows_callback, None)
print("==========================================")
