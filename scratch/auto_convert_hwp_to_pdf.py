import win32com.client
import os
import glob
import sys
import datetime
import subprocess
import threading
import time
import win32gui
import win32con

# --- 설정: 변환할 대상 폴더 목록 ---
TARGET_FOLDERS = [
    r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교"
]

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hwp_convert_log.txt")
RECYCLE_THRESHOLD = 25  # 25개 파일 변환마다 한글 프로그램 재시작

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {msg}"
    try:
        print(log_msg)
    except UnicodeEncodeError:
        print(log_msg.encode(sys.stdout.encoding or 'cp949', errors='replace').decode(sys.stdout.encoding or 'cp949'))
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    except Exception:
        pass

def kill_hwp_processes():
    """만약 한글 프로세스가 엉켜 있거나 좀비로 남았을 경우를 대비해 작업관리자에서 강제 종료"""
    log("Force killing any hanging Hwp.exe processes...")
    try:
        subprocess.run(["taskkill", "/f", "/im", "Hwp.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        log(f"Error during taskkill: {e}")

def get_hwp_instance():
    try:
        import pyhwpx
        log("Launching new Hancom Office (Hwp) via pyhwpx (visible=True)...")
        hwp = pyhwpx.Hwp(visible=True)
        # Suppress all dialog popups and message boxes completely to avoid stealing focus or blocking
        try:
            # hwp.SetMessageBoxMode(0xF0000)
            log("Skipped setting HWP message box mode to silent to allow password dialog to pop up")
        except Exception as msg_err:
            log(f"Warning: Could not set MessageBoxMode: {msg_err}")
        return hwp
    except Exception as e:
        log(f"Critical: Failed to launch Hancom Office via pyhwpx. {e}")
        return None

def dismiss_hwp_popups():
    log("Starting background thread to auto-dismiss Hancom Office security/comment/password popups (robust mode)...")
    while True:
        try:
            target_hwnds = []
            
            def enum_top_windows(hwnd, lparam):
                class_name = win32gui.GetClassName(hwnd)
                # 표준 대화상자(#32770)인 경우만 후보군으로 수집
                if class_name == "#32770":
                    target_hwnds.append(hwnd)
                return True
                
            win32gui.EnumWindows(enum_top_windows, None)
            
            for hwnd in target_hwnds:
                # 자식 윈도우들의 텍스트 조사
                texts = []
                edit_hwnds = []
                button_hwnds = []
                def enum_child_proc(child_hwnd, param):
                    text = win32gui.GetWindowText(child_hwnd)
                    c_class = win32gui.GetClassName(child_hwnd)
                    if text:
                        texts.append(text)
                    if c_class == "Edit":
                        edit_hwnds.append(child_hwnd)
                    elif c_class == "Button":
                        button_hwnds.append(child_hwnd)
                    return True
                
                try:
                    win32gui.EnumChildWindows(hwnd, enum_child_proc, None)
                except Exception:
                    continue
                
                is_target_popup = False
                is_password_popup = False
                
                # 휴리스틱: Edit 컨트롤이 딱 1개 존재하고 버튼이 있으면 암호 대화상자로 판단 (인코딩 깨짐 우회)
                if len(edit_hwnds) == 1 and len(button_hwnds) >= 1:
                    is_password_popup = True
                else:
                    for t in texts:
                        if "숨은 설명" in t or "보안 설정" in t or "문서 보안" in t:
                            is_target_popup = True
                            break
                        if "암호" in t or "비밀번호" in t:
                            is_password_popup = True
                            break
                
                if is_password_popup:
                    title = win32gui.GetWindowText(hwnd)
                    log(f"Detected Hancom Office Password popup (HWND: {hwnd}, Title: '{title}'). Entering password '12345'...")
                    
                    if edit_hwnds:
                        edit_hwnd = edit_hwnds[0]
                        win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, "12345")
                        log("Entered password '12345' into Edit control.")
                        
                    # '확인' 혹은 '확인' 계열 버튼 찾기
                    btn_hwnd = None
                    for b_hwnd in button_hwnds:
                        c_text = win32gui.GetWindowText(b_hwnd)
                        # 깨진 인코딩 대응
                        if any(x in c_text for x in ["확인", "OK", "열기", "Y", "Yes"]):
                            btn_hwnd = b_hwnd
                            break
                    
                    # 텍스트로 찾지 못했으면 첫 번째 버튼을 확인 버튼으로 가정
                    if not btn_hwnd and button_hwnds:
                        btn_hwnd = button_hwnds[0]
                        
                    if btn_hwnd:
                        btn_text = win32gui.GetWindowText(btn_hwnd)
                        win32gui.SendMessage(btn_hwnd, win32con.BM_CLICK, 0, 0)
                        log(f"Clicked button '{btn_text}' (HWND: {btn_hwnd}) for password confirmation.")
                    else:
                        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                        log("Sent Enter key as fallback for password confirmation.")
                    time.sleep(1.0)
                    continue
                
                if is_target_popup:
                    title = win32gui.GetWindowText(hwnd)
                    log(f"Detected Hancom Office Security/Comment popup (HWND: {hwnd}, Title: '{title}').")
                    
                    # '열기(Y)' 혹은 '확인' 혹은 'Y' 버튼 찾기
                    btn_hwnd = None
                    def find_button(child_hwnd, param):
                        nonlocal btn_hwnd
                        c_class = win32gui.GetClassName(child_hwnd)
                        c_text = win32gui.GetWindowText(child_hwnd)
                        if c_class == "Button":
                            # '열기', 'Y', '확인', 'Yes', 'OK'가 들어있는 버튼
                            if any(x in c_text for x in ["열기", "Y", "확인", "Yes", "OK"]):
                                btn_hwnd = child_hwnd
                                return False  # 중단
                        return True
                    
                    try:
                        win32gui.EnumChildWindows(hwnd, find_button, None)
                    except Exception:
                        pass
                    
                    if btn_hwnd:
                        btn_text = win32gui.GetWindowText(btn_hwnd)
                        log(f"Found auto-dismiss button '{btn_text}' (HWND: {btn_hwnd}). Clicking it automatically...")
                        win32gui.SendMessage(btn_hwnd, win32con.BM_CLICK, 0, 0)
                    else:
                        log("Target button not found. Sending Enter key as fallback...")
                        try:
                            win32gui.SetForegroundWindow(hwnd)
                        except:
                            pass
                        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                    
                    time.sleep(1.0) # 다이얼로그 닫힐 대기시간
        except Exception as e:
            # 백그라운드 스레드 오류 안전 격리
            log(f"Error in popup dismiss thread: {e}")
        time.sleep(0.5)


def auto_convert_missing_pdfs():
    converted_count = 0
    cycle_converted = 0
    hwp = None
    
    # 시작 시 잔존하는 한글 좀비 프로세스 전면 청소
    kill_hwp_processes()
    
    # 백그라운드 팝업 감지 프로세스 가동 (메인 스레드 블락 우회용 독립 프로세스)
    log("Launching background process for auto-dismissing popups...")
    popup_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "popup_process_log.txt")
    try:
        popup_log = open(popup_log_path, "w", encoding="utf-8")
        popup_process = subprocess.Popen([sys.executable, __file__, "--dismiss-only"], stdout=popup_log, stderr=subprocess.STDOUT)
    except Exception as pop_err:
        log(f"Failed to start popup process with logs: {pop_err}")
        popup_process = subprocess.Popen([sys.executable, __file__, "--dismiss-only"])
    
    try:
        for folder in TARGET_FOLDERS:
            if not os.path.exists(folder):
                log(f"Warning: Folder does not exist: {folder}")
                continue
                
            log(f"Scanning folder: {folder}")
            # 하위 폴더까지 모두 검색 (.hwp, .hwpx, .odt)
            hwp_files = []
            for ext_pattern in ["*.hwp", "*.hwpx", "*.odt"]:
                search_pattern = os.path.join(folder, "**", ext_pattern)
                hwp_files.extend(glob.glob(search_pattern, recursive=True))
            
            for hwp_path in hwp_files:
                base, ext = os.path.splitext(hwp_path)
                pdf_path = base + ".pdf"
                
                # PDF가 이미 존재하면 건너뜀
                if os.path.exists(pdf_path):
                    continue
                    
                log(f"Found missing PDF for: {hwp_path}")
                
                # 리사이클 임계값 확인
                if cycle_converted >= RECYCLE_THRESHOLD:
                    log(f"Reached threshold ({RECYCLE_THRESHOLD} files). Recycling Hancom Office instance...")
                    if hwp is not None:
                        try:
                            hwp.Quit()
                        except Exception:
                            pass
                        hwp = None
                    kill_hwp_processes()
                    cycle_converted = 0
                
                # 한글 인스턴스 지연 실행 및 복구
                if hwp is None:
                    hwp = get_hwp_instance()
                    if hwp is None:
                        log("Could not initialize HWP instance. Stopping conversion cycle.")
                        return
                
                try:
                    log(f"Converting [{converted_count + 1}] -> {pdf_path}")
                    
                    # 확장자별 적절한 포맷 지정
                    ext_lower = ext.lower()
                    if ext_lower == ".hwp":
                        fmt = "HWP"
                    elif ext_lower == ".hwpx":
                        fmt = "HWPX"
                    elif ext_lower == ".odt":
                        fmt = "ODT"
                    else:
                        fmt = ""
                        
                    hwp.Open(hwp_path, fmt, "forceopen:true;skipcomment:true;password:12345")
                    
                    try:
                        hwp.HAction.GetDefault("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
                        hwp.HParameterSet.HFileOpenSave.filename = pdf_path
                        hwp.HParameterSet.HFileOpenSave.Format = "PDF"
                        hwp.HAction.Execute("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
                    except Exception:
                        hwp.SaveAs(pdf_path, "PDF", "")
                        
                    converted_count += 1
                    cycle_converted += 1
                    log("Conversion successful.")
                except Exception as e:
                    log(f"Failed to convert {hwp_path}: {e}")
                    log("Attempting to recover by closing and re-opening HWP instance...")
                    # 오류 발생 시 인스턴스를 무효화하여 다음 루프에서 새로 열도록 함
                    if hwp is not None:
                        try:
                            hwp.Quit()
                        except:
                            pass
                        hwp = None
                    kill_hwp_processes()
                finally:
                    if hwp is not None:
                        try:
                            hwp.Clear(1)
                        except:
                            pass
                            
    except Exception as e:
        log(f"Critical error in main loop: {e}")
    finally:
        # 팝업 감지 독립 프로세스 종료
        try:
            popup_process.terminate()
            log("Terminated background popup dismiss process.")
        except Exception as proc_err:
            log(f"Warning: Could not terminate popup process: {proc_err}")
        try:
            popup_log.close()
        except:
            pass

        if hwp is not None:
            try:
                hwp.Quit()
            except:
                pass
        
    log(f"Auto-conversion cycle finished. Total converted: {converted_count}")
    if converted_count > 0:
        show_completion_popup(converted_count)

def show_completion_popup(converted_count):
    try:
        import tkinter as tk
        import winsound
        
        # 사운드 알림
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
        
        root = tk.Tk()
        root.title("문서 PDF 변환 완료")
        
        # 윈도우 크기 및 위치 설정 (화면 중앙)
        window_width = 460
        window_height = 200
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        x = int((screen_width/2) - (window_width/2))
        y = int((screen_height/2) - (window_height/2))
        
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 항상 최상단에 표시 및 포커스 강제
        root.attributes('-topmost', True)
        root.lift()
        root.focus_force()
        root.after(100, root.focus_force)
        root.configure(bg="#f8f9fa")
        
        # 메인 메시지
        message = f"문서 파일(HWP/HWPX/ODT) PDF 변환이 완료되었습니다!\n\n총 {converted_count}개의 파일이 성공적으로 변환되었습니다."
        label = tk.Label(root, text=message, font=("Malgun Gothic", 12, "bold"), 
                         pady=20, fg="#003366", bg="#f8f9fa", justify="center")
        label.pack(expand=True, fill="both")
        
        # 확인 버튼
        btn = tk.Button(root, text="확인", command=root.destroy, width=12, 
                        font=("Malgun Gothic", 11, "bold"), bg="#003366", fg="white", 
                        relief="flat", cursor="hand2")
        btn.pack(side="bottom", pady=15)
        
        # 엔터 키 바인딩
        root.bind('<Return>', lambda event: root.destroy())
        
        root.mainloop()
    except Exception as popup_err:
        log(f"Failed to display Completion popup: {popup_err}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--dismiss-only":
        dismiss_hwp_popups()
    else:
        auto_convert_missing_pdfs()

