import olefile
import os
import re
import win32com.client
import sys
import subprocess

# Set encoding for stdout to avoid cp949 errors
if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

def get_hwp_text(filename):
    try:
        f = olefile.OleFileIO(filename)
        if ['PrvText'] in f.listdir():
            text = f.openstream('PrvText').read().decode('utf-16le')
            return text
    except:
        pass
    return ""

def extract_plan_info(text, filename):
    info = {}
    # Extract teacher from filename
    match = re.search(r'\(([^)]+)\)\.hwp', filename)
    if not match: match = re.search(r'([가-힣]{2,4})\.hwp', filename)
    info['teacher'] = match.group(1) if match else "미상"
    
    # Regex for info
    dt_match = re.search(r'일\s*시\s*[:：]?\s*([^\n\r]+)', text)
    loc_match = re.search(r'장\s*소\s*[:：]?\s*([^\n\r]+)', text)
    tgt_match = re.search(r'대\s*상\s*[:：]?\s*([^\n\r]+)', text)
    sub_match = re.search(r'과\s*목\s*[:：]?\s*([^\n\r]+)', text)
    topic_match = re.search(r'(?:주제|단원)\s*[:：]?\s*([^\n\r]+)', text)
    
    info['datetime'] = dt_match.group(1).strip() if dt_match else ""
    info['location'] = loc_match.group(1).strip() if loc_match else ""
    info['target'] = tgt_match.group(1).strip() if tgt_match else ""
    info['subject'] = sub_match.group(1).strip() if sub_match else ""
    info['topic'] = topic_match.group(1).strip() if topic_match else ""
    
    return info

def extract_feedback_info(text):
    feedback = []
    # Look for "장점", "제언", "참관 소감"
    sections = re.split(r'[\d\.]\s*(?:수업의 장점|제언|참관 소감|의견)', text)
    if len(sections) > 1:
        for s in sections[1:]:
            clean = s.split('\r\n\r\n')[0].strip()
            if clean: feedback.append(clean)
    return " / ".join(feedback)

def notify_user(title, message):
    ps_command = f'[reflection.assembly]::loadwithpartialname("System.Windows.Forms"); [System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'
    subprocess.run(["powershell", "-Command", ps_command])

def main():
    plan_folder = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 나눔의 날\국어과"
    obs_folder = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록"
    template_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무 이외\국어과 총무\1학기 수업 나눔(국어과, 강필성T)\2026. 1학기 1차 교과 협의록 양식(국어).hwp"
    output_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 참관록\2026. 1학기 2차 교과 협의록(국어).hwp"

    print("Extracting plans...")
    plans = []
    for f in os.listdir(plan_folder):
        if f.endswith(".hwp"):
            text = get_hwp_text(os.path.join(plan_folder, f))
            plans.append(extract_plan_info(text, f))
    plans.sort(key=lambda x: x.get('teacher', ''))

    print("Extracting feedback...")
    feedbacks = {}
    for f in os.listdir(obs_folder):
        if "참관록" in f and f.endswith(".hwp"):
            text = get_hwp_text(os.path.join(obs_folder, f))
            match = re.search(r'\(([^)]+)\)', f)
            teacher = match.group(1) if match else ""
            if teacher:
                feedbacks[teacher] = extract_feedback_info(text)

    print("Generating HWP...")
    try:
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.XHwpWindows.Item(0).Visible = True
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckDLL")
        hwp.Open(template_path, "HWP", "forceopen:true")
        
        ctrl = hwp.HeadCtrl
        target_table = None
        while ctrl:
            if ctrl.CtrlID == "tbl":
                hwp.SetPosBySet(ctrl.GetAnchorPos())
                hwp.FindCtrl()
                hwp.Run("TableCellBlock")
                hwp.InitScan()
                res, msg = hwp.GetText()
                hwp.ReleaseScan()
                hwp.Run("Cancel")
                if "수업" in msg and "나눔" in msg:
                    target_table = ctrl
                    break
            ctrl = ctrl.Next
        
        if target_table:
            hwp.SetPosBySet(target_table.GetAnchorPos())
            hwp.FindCtrl()
            hwp.Run("TableCellBlock")
            hwp.Run("TableLowerCell")
            
            for i, p in enumerate(plans):
                # Teacher
                hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
                hwp.HParameterSet.HInsertText.Text = p.get('teacher', '')
                hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
                
                hwp.Run("TableRightCell")
                hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet.SetItem("Text", p.get('datetime', '')))
                
                hwp.Run("TableRightCell")
                hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet.SetItem("Text", p.get('location', '')))
                
                hwp.Run("TableRightCell")
                hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet.SetItem("Text", f"{p.get('target', '')} ({p.get('subject', '')})"))
                
                hwp.Run("TableRightCell")
                hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet.SetItem("Text", p.get('topic', '')))
                
                if i < len(plans) - 1:
                    res = hwp.Run("TableLowerCell")
                    if not res:
                        hwp.Run("TableAppendRow")
                        hwp.Run("TableLowerCell")
                    for _ in range(4): hwp.Run("TableLeftCell")

        hwp.MovePos(2)
        if hwp.FindQuestion("협의 내용", 1, 0):
            hwp.Run("MoveDown")
            for t, f in feedbacks.items():
                hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet.SetItem("Text", f"[{t} 선생님 수업] {f}\n"))

        hwp.SaveAs(output_path, "HWP", "")
        hwp.Quit()
        
        notify_user("교과 협의록 작성 완료", f"{output_path}에 저장이 완료되었습니다.")
        
    except Exception as e:
        log_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\error_log.txt"
        with open(log_path, "w", encoding="utf-8") as err_file:
            err_file.write(str(e))
        notify_user("오류 발생", f"작업 중 오류가 발생했습니다. 로그를 확인하세요: {log_path}")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
