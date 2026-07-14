import win32gui
import win32con
import sys
import time

def test_dismiss():
    target_hwnds = []
    def enum_top_windows(hwnd, lparam):
        class_name = win32gui.GetClassName(hwnd)
        if class_name == "#32770":
            target_hwnds.append(hwnd)
        return True
    
    win32gui.EnumWindows(enum_top_windows, None)
    print(f"Collected {len(target_hwnds)} standard dialogs.")
    
    for hwnd in target_hwnds:
        edit_hwnds = []
        button_hwnds = []
        def enum_child_proc(child_hwnd, param):
            c_class = win32gui.GetClassName(child_hwnd)
            if c_class == "Edit":
                edit_hwnds.append(child_hwnd)
            elif c_class == "Button":
                button_hwnds.append(child_hwnd)
            return True
            
        try:
            win32gui.EnumChildWindows(hwnd, enum_child_proc, None)
        except Exception as e:
            print(f"Error enum: {e}")
            continue
            
        if len(edit_hwnds) == 1 and len(button_hwnds) >= 1:
            print(f"Found candidate password window: HWND {hwnd}")
            edit_hwnd = edit_hwnds[0]
            try:
                # WM_SETTEXT
                print("Sending WM_SETTEXT '12345'...")
                win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, "12345")
                print("Sent WM_SETTEXT successfully.")
            except Exception as e:
                print(f"Error sending WM_SETTEXT: {e}")
                
            btn_hwnd = None
            for b_hwnd in button_hwnds:
                c_text = win32gui.GetWindowText(b_hwnd)
                print(f"Button HWND: {b_hwnd}, Text: '{c_text}'")
                if any(x in c_text for x in ["확인", "OK", "열기", "Y", "Yes"]):
                    btn_hwnd = b_hwnd
                    break
            if not btn_hwnd:
                btn_hwnd = button_hwnds[0]
                
            if btn_hwnd:
                try:
                    print(f"Clicking button HWND {btn_hwnd}...")
                    win32gui.SendMessage(btn_hwnd, win32con.BM_CLICK, 0, 0)
                    print("Button clicked successfully.")
                except Exception as e:
                    print(f"Error clicking button: {e}")
            else:
                print("No button found to click.")
                
test_dismiss()
