import os
import sys
import time
import subprocess
import threading
import pyhwpx
import win32gui
import win32con

# Set console output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Input files
files = [
    r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록\2026. 1학기 2차 수업나눔의 날 수업참관록_교사용(황요한).hwp",
    r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록\2026. 1학기 2차 수업나눔의 날 수업참관록_교사용(강지영).hwp",
    r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록\2026. 1학기 2차 수업나눔의 날 수업참관록_교사용(강필성).hwp",
    r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록\2026. 1학기 2차 수업나눔의 날 수업참관록_교사용(이병의).hwp",
    r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록\2026. 1학기 2차 수업나눔의 날 수업참관록_교사용(조진희).hwp"
]
output_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록\2026. 1학기 2차 수업나눔의 날 수업참관록_교사용(국어).hwp"

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

def merge_hwps():
    kill_hwp_processes()
    
    # Start the popup thread
    popup_thread = threading.Thread(target=dismiss_hwp_popups, daemon=True)
    popup_thread.start()
    
    print("Launching Hancom Office (Hwp) via pyhwpx...")
    try:
        hwp = pyhwpx.Hwp(visible=False)
        try:
            hwp.SetMessageBoxMode(0xF0000)
        except Exception:
            pass
    except Exception as e:
        print(f"Error launching Hwp: {e}")
        return

    try:
        # Open the first file
        print(f"Opening first file: {files[0]}")
        hwp.Open(files[0], "HWP", "forceopen:true;skipcomment:true")
        time.sleep(1.0)
        
        # Append the other files
        for i, filepath in enumerate(files[1:], start=2):
            if not os.path.exists(filepath):
                print(f"Warning: File not found, skipping: {filepath}")
                continue
            
            print(f"Appending [{i}/{len(files)}]: {filepath}")
            # Move cursor to end of document
            hwp.MoveDocEnd()
            # Break page
            hwp.BreakPage()
            # Insert file content using pyhwpx's insert_file
            # It accepts filename, keep_section, keep_charshape, keep_parashape, keep_style, move_doc_end
            hwp.insert_file(filepath, keep_section=1, keep_charshape=1, keep_parashape=1, keep_style=1, move_doc_end=True)
            time.sleep(1.0)
            
        print(f"Saving merged document to: {output_path}")
        hwp.SaveAs(output_path, "HWP", "")
        print("Merged document saved successfully.")
        
        # Convert to PDF as well since the user might need it
        pdf_output_path = os.path.splitext(output_path)[0] + ".pdf"
        print(f"Converting merged document to PDF: {pdf_output_path}")
        pdf_success = False
        try:
            hwp.HAction.GetDefault("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
            hwp.HParameterSet.HFileOpenSave.filename = pdf_output_path
            hwp.HParameterSet.HFileOpenSave.Format = "PDF"
            hwp.HAction.Execute("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
            pdf_success = True
        except Exception as e:
            print(f"FileSaveAsPdf action failed: {e}")
            
        if not pdf_success:
            try:
                hwp.SaveAs(pdf_output_path, "PDF", "")
                pdf_success = True
            except Exception as e:
                print(f"SaveAs PDF failed: {e}")
                
        if pdf_success:
            print("Successfully created PDF version as well.")
            
    except Exception as e:
        print(f"Error during merging process: {e}")
    finally:
        try:
            hwp.Quit()
        except Exception:
            pass
        kill_hwp_processes()
        print("Process completed.")

if __name__ == "__main__":
    merge_hwps()
