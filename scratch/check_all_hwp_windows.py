import sys
import win32gui
import win32process
import subprocess

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# Hwp.exe의 PID 목록 가져오기
try:
    output = subprocess.check_output('tasklist /fi "imagename eq Hwp.exe" /fo csv', shell=True).decode('cp949', errors='ignore')
    pids = []
    for line in output.strip().split('\n')[1:]:
        parts = line.split(',')
        if len(parts) > 1:
            pid_str = parts[1].strip('"')
            if pid_str.isdigit():
                pids.append(int(pid_str))
except Exception as e:
    print(f"Error getting PIDs: {e}")
    pids = []

print(f"Found Hwp.exe PIDs: {pids}")

def enum_windows_callback(hwnd, extra):
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
    except:
        return True
        
    if pid in pids:
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        visible = win32gui.IsWindowVisible(hwnd)
        print(f"HWND: {hwnd} | PID: {pid} | Class: {class_name} | Visible: {visible} | Title: {title}")
        
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

print("=== Hwp.exe Windows ===")
win32gui.EnumWindows(enum_windows_callback, None)
print("=======================")
