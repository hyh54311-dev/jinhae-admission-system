import sys
import win32gui

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

print("=== Scanning All Visible Windows ===")

def enum_handler(hwnd, extra):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        # 타이틀이나 클래스에 '글' 또는 'Hwnd' 또는 '32770'이 들어가는 모든 윈도우 출력
        if title or class_name == "#32770" or "Hwnd" in class_name:
            print(f"HWND: {hwnd} | Class: {class_name} | Title: {title}")
            
            # 자식 윈도우 정보도 출력
            children = []
            def enum_child(c_hwnd, param):
                c_title = win32gui.GetWindowText(c_hwnd)
                c_class = win32gui.GetClassName(c_hwnd)
                children.append((c_hwnd, c_class, c_title))
                return True
            try:
                win32gui.EnumChildWindows(hwnd, enum_child, None)
                for ch, cc, ct in children:
                    if ct or "Button" in cc or "Static" in cc or "Edit" in cc:
                        print(f"  -> Child HWND: {ch} | Class: {cc} | Text: {ct}")
            except Exception as e:
                print(f"  -> Error enum children: {e}")
            print("-" * 50)
    return True

win32gui.EnumWindows(enum_handler, None)
print("=== Scanning Complete ===")
