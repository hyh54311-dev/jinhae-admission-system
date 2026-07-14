import sys
import win32gui
import win32process

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

def enum_windows_callback(hwnd, extra):
    title = win32gui.GetWindowText(hwnd)
    class_name = win32gui.GetClassName(hwnd)
    
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
    except:
        pid = 0
        
    # 대화상자(#32770)이거나 타이틀에 관련 키워드가 있는 경우 모두 출력
    if class_name == "#32770" or "글" in title or "보안" in title or "설정" in title or "HwndWrapper" in class_name:
        visible = win32gui.IsWindowVisible(hwnd)
        print(f"HWND: {hwnd} | PID: {pid} | Class: {class_name} | Visible: {visible} | Title: {title}")
        
        # 자식 윈도우 출력
        children = []
        def enum_child_callback(child_hwnd, param):
            c_title = win32gui.GetWindowText(child_hwnd)
            c_class = win32gui.GetClassName(child_hwnd)
            children.append(f"  [Child HWND: {child_hwnd} | Class: {c_class} | Text: {c_title}]")
            return True
        
        try:
            win32gui.EnumChildWindows(hwnd, enum_child_callback, None)
            for child in children:
                print(child)
        except Exception as e:
            print(f"  Error enum child: {e}")
        print("-" * 50)
    return True

print("=== START DIAGNOSTIC POPUPS ===")
win32gui.EnumWindows(enum_windows_callback, None)
print("=== END DIAGNOSTIC POPUPS ===")
