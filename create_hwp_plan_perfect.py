import win32com.client
import os

def create_perfect_hwp():
    try:
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.XHwpWindows.Item(0).Visible = False
        
        desktop = r"D:\OneDrive - 경상남도교육청\바탕 화면"
        file_path = os.path.join(desktop, "대만 여행 계획.hwp")
        
        # 전문적인 HTML 서식 작성 (HWP가 이를 해석하여 문서로 변환함)
        html_content = """
        <html>
        <body style="font-family: '함초롬바탕';">
            <div style="text-align: center;">
                <h1 style="color: #003366; font-size: 24pt;">대만 여행 계획서 (성인 남성 4인)</h1>
            </div>
            <br>
            <h2 style="color: #004080; border-left: 5px solid #004080; padding-left: 10px;">1. 여행 개요</h2>
            <ul>
                <li><b>일정:</b> 2027년 1월 25일(월) ~ 2월 3일(수) (설 연휴 제외)</li>
                <li><b>목적지:</b> 대만 (타이베이, 가오슝)</li>
                <li><b>인원:</b> 성인 남성 4명</li>
            </ul>
            <br>
            <h2 style="color: #004080; border-left: 5px solid #004080; padding-left: 10px;">2. 항공권 예매 최저가 공략</h2>
            <table border="1" style="border-collapse: collapse; width: 100%; border-color: #cccccc;">
                <tr style="background-color: #f2f2f2;">
                    <th style="padding: 8px; width: 30%;">항목</th>
                    <th style="padding: 8px;">세부 전략</th>
                </tr>
                <tr>
                    <td style="padding: 8px; text-align: center;"><b>예매 타이밍</b></td>
                    <td style="padding: 8px;">2026년 7월 ~ 8월 (LCC 동계 스케줄 오픈 즉시)</td>
                </tr>
                <tr>
                    <td style="padding: 8px; text-align: center;"><b>추천 항공사</b></td>
                    <td style="padding: 8px;">에어부산(Fly & Sale), 제주항공(JJIM), 타이거에어</td>
                </tr>
                <tr>
                    <td style="padding: 8px; text-align: center;"><b>핵심 전술</b></td>
                    <td style="padding: 8px;">2+2 분할 예매, 가오슝 루트 활용, 수하물 선택적 추가</td>
                </tr>
            </table>
            <br>
            <h2 style="color: #004080; border-left: 5px solid #004080; padding-left: 10px;">3. 숙소 및 현지 이동</h2>
            <p style="margin-left: 20px;">
                - <b>숙소:</b> 시먼딩(Ximen) 인근 거실이 포함된 아파트형 숙소 권장<br>
                - <b>이동:</b> 4인 이동 시 택시/우버 활용이 가장 효율적
            </p>
            <br><br>
            <p style="text-align: right; color: #888888; font-style: italic;">작성: 인공지능 비서 Antigravity</p>
        </body>
        </html>
        """
        
        hwp.Run("FileNew")
        # HTML 형식을 한글 문서로 변환하여 삽입
        hwp.SetTextFile(html_content, "HTML")
        
        hwp.SaveAs(file_path)
        hwp.Quit()
        print(f"SUCCESS: Perfect HWP created at {file_path}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    create_perfect_hwp()
