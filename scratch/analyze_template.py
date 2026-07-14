import win32com.client
import os

def list_tables(file_path):
    hwp = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckDLL")
    hwp.Open(file_path)
    
    ctrl = hwp.HeadCtrl
    table_count = 0
    while ctrl:
        if ctrl.CtrlID == "tbl":
            table_count += 1
            print(f"Table {table_count}:")
            # Try to get some content from the first cell
            # This is complex in HWP API, but let's just count them for now
        ctrl = ctrl.Next
    
    hwp.Quit()

template_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무 이외\국어과 총무\1학기 수업 나눔(국어과, 강필성T)\2026. 1학기 1차 교과 협의록 양식(국어).hwp"
print(f"Analyzing template: {template_path}")
list_tables(template_path)
