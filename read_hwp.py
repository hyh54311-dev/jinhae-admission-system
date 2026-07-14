import win32com.client as win32
import os

hwp_path = r'd:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\개인적인 일\2026년 교육대학원연계 AI융합교육 전문과정 교육대상자 선발 추진 계획\2026년 교육대학원연계 AI융합교육 전문과정 교육대상자 선발 추진 계획.hwp'
out_path = 'hwp_text.txt'

try:
    hwp = win32.gencache.EnsureDispatch('HWPFrame.HwpObject')
    hwp.RegisterModule('FilePathCheckDLL', 'SecurityModule')
    hwp.Open(hwp_path)
    hwp.InitScan()
    text = ''
    while True:
        state, t = hwp.GetText()
        if t:
            text += t
        if state <= 1:
            break
    hwp.ReleaseScan()
    hwp.Quit()

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Success')
except Exception as e:
    print(f'Error: {e}')
