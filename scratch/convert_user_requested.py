import os
import sys
import time
import subprocess
import threading
import win32com.client as win32
import win32gui
import win32con

# Set console output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Targets
files_to_convert = [
    r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록\2026. 1학기 2차 수업나눔의 날 수업참관록_교사용(강필성).hwp",
    r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록\2026. 1학기 2차 수업나눔의 날 수업참관록_교사용(강지영).hwp"
]

def kill_hwp_processes():
    print("Force killing any hanging Hwp.exe processes...")
    try:
        subprocess.run(["taskkill", "/f", "/im", "Hwp.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(f"Error during taskkill: {e}")

def dismiss_hwp_popups():
    print("Starting background thread to auto-dismiss Hancom Office security/comment popups...")
    while True:
        try:
            target_hwnds = []
            
            def enum_top_windows(hwnd, lparam):
                class_name = win32gui.GetClassName(hwnd)
                if class_name == "#32770":
                    target_hwnds.append(hwnd)
                return True
                
            win32gui.EnumWindows(enum_top_windows, None)
            
            for hwnd in target_hwnds:
                texts = []
                def enum_child_proc(child_hwnd, param):
                    text = win32gui.GetWindowText(child_hwnd)
                    if text:
                        texts.append(text)
                    return True
                
                try:
                    win32gui.EnumChildWindows(hwnd, enum_child_proc, None)
                except Exception:
                    continue
                
                is_target_popup = False
                for t in texts:
                    if any(x in t for x in ["숨은 설명", "보안 설정", "문서 보안", "보안"]):
                        is_target_popup = True
                        break
                
                if is_target_popup:
                    title = win32gui.GetWindowText(hwnd)
                    print(f"[Popup Dismiss] Detected Hancom Office popup (HWND: {hwnd}, Title: '{title}').")
                    
                    btn_hwnd = None
                    def find_button(child_hwnd, param):
                        nonlocal btn_hwnd
                        c_class = win32gui.GetClassName(child_hwnd)
                        c_text = win32gui.GetWindowText(child_hwnd)
                        if c_class == "Button":
                            if any(x in c_text for x in ["열기", "Y", "확인", "Yes", "OK"]):
                                btn_hwnd = child_hwnd
                                return False
                        return True
                    
                    try:
                        win32gui.EnumChildWindows(hwnd, find_button, None)
                    except Exception:
                        pass
                    
                    if btn_hwnd:
                        btn_text = win32gui.GetWindowText(btn_hwnd)
                        print(f"[Popup Dismiss] Clicking button '{btn_text}' (HWND: {btn_hwnd})...")
                        win32gui.SendMessage(btn_hwnd, win32con.BM_CLICK, 0, 0)
                    else:
                        print("[Popup Dismiss] Sending Enter key as fallback...")
                        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                    
                    time.sleep(1.0)
        except Exception:
            pass
        time.sleep(0.5)

def convert_files():
    kill_hwp_processes()
    
    # Start the popup thread
    popup_thread = threading.Thread(target=dismiss_hwp_popups, daemon=True)
    popup_thread.start()
    
    print("Launching Hancom Office (Hwp)...")
    try:
        hwp = win32.gencache.EnsureDispatch('HWPFrame.HwpObject')
        hwp.RegisterModule('FilePathCheckDLL', 'SecurityModule')
        # Make invisible to avoid screen flicker, or let it be visible if needed. Let's make it invisible.
        try:
            hwp.XHwpWindows.Item(0).Visible = False
        except Exception:
            pass
        # Suppress message boxes
        try:
            hwp.SetMessageBoxMode(0xF0000)
        except Exception:
            pass
    except Exception as e:
        print(f"Error launching Hwp: {e}")
        return

    for hwp_path in files_to_convert:
        if not os.path.exists(hwp_path):
            print(f"Error: File not found: {hwp_path}")
            continue
            
        pdf_path = os.path.splitext(hwp_path)[0] + ".pdf"
        print(f"Converting: {hwp_path} -> {pdf_path}")
        
        try:
            hwp.Open(hwp_path, "HWP", "forceopen:true;skipcomment:true")
            # Wait a moment for file to open completely
            time.sleep(1.0)
            
            # Save as PDF
            # Check the default SaveAsPdf action or standard SaveAs
            success = False
            try:
                hwp.HAction.GetDefault("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
                hwp.HParameterSet.HFileOpenSave.filename = pdf_path
                hwp.HParameterSet.HFileOpenSave.Format = "PDF"
                hwp.HAction.Execute("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
                success = True
                print("Converted successfully via FileSaveAsPdf action.")
            except Exception as e:
                print(f"Action conversion failed ({e}), trying standard SaveAs...")
                
            if not success:
                try:
                    hwp.SaveAs(pdf_path, "PDF", "")
                    success = True
                    print("Converted successfully via SaveAs method.")
                except Exception as e:
                    print(f"SaveAs method failed: {e}")
            
            if success:
                print(f"Success: Created {pdf_path}")
            else:
                print(f"Failed to convert {hwp_path}")
                
            hwp.Clear(1)
        except Exception as e:
            print(f"Error processing {hwp_path}: {e}")
            
    try:
        hwp.Quit()
    except Exception:
        pass
        
    # Final cleanup
    kill_hwp_processes()
    print("All specific conversions completed.")

if __name__ == "__main__":
    convert_files()
