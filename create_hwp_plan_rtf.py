import os

def create_pro_rtf_hwp():
    desktop = r"D:\OneDrive - 경상남도교육청\바탕 화면"
    file_path = os.path.join(desktop, "대만 여행 계획.hwp")
    
    # RTF 서식 (한글 2018 이상에서 완벽 호환)
    # \f0: 폰트, \fs: 글자크기(Half-points, 40=20pt), \b: 굵게, \qc: 중앙정렬, \ql: 왼쪽정렬
    rtf_content = r"""{\rtf1\ansi\ansicpg949\deff0
{\fonttbl{\f0\fmodern\fcharset129 Malgun Gothic;}}
{\colortbl ;\red0\green51\blue102;\red0\green64\blue128;\red128\green128\blue128;}
\viewkind4\uc1\pard\qc\cf1\b\f0\fs44 [   ȹ -   4]\b0\fs24\par
\par
\pard\ql\cf2\b\fs28 1.   \b0\fs20\par
  -  : 2027 1 25() ~ 2 3() (   )\par
  - :  (̹, )\par
  - :   4\par
\par
\pard\ql\cf2\b\fs28 2.         (Golden Strategy)\b0\fs20\par
\par
\pard\ql\b [    ]\b0  2026 7 ~ 8 (LCC     )\par
\b [   ]\b0     (Fly & Sale),    (JJIM),      \par
\b [ ]\b0  2+2    ,   Ȱ,   2  \par
\par
\pard\ql\cf2\b\fs28 3.      \b0\fs20\par
  - :  (Ximen)         \par
  -  : 4     / Ȱ?     \par
\par
\pard\qr\cf3\i\fs18 :       Antigravity\par
}"""

    # RTF 파일로 쓰되 확장자는 .hwp로 저장 (한글에서 자동으로 인식)
    try:
        with open(file_path, "w", encoding="ascii") as f:
            f.write(rtf_content)
        print(f"SUCCESS: Professional HWP created at {file_path}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    create_pro_rtf_hwp()
