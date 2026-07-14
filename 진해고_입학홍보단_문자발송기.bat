@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

:menu
cls
echo ==========================================================
echo    🏆 진해고등학교 입학홍보단 단체 문자 발송 시스템 🏆
echo ==========================================================
echo.
echo  [1] 디버그용 독립 크롬 창 실행 (발송용)
echo      - 기존 열려있는 크롬 창을 닫지 않고 실행할 수 있습니다.
echo      - 최초 실행 시 구글 메시지 QR 코드를 한 번만 스캔해 주세요.
echo.
echo  [2] 단체 문자 발송 시작 (Playwright 자동화)
echo      - [1]번 크롬 창이 켜져 있고 페어링된 상태에서 실행합니다.
echo      - 합격생 20명에게 1:1 맞춤 안내 문자를 순차 발송합니다.
echo.
echo  [3] 시스템 사용 설명서 및 문제 해결 가이드 보기
echo.
echo  [4] 종료
echo.
echo ==========================================================
set /p menu_choice="원하시는 작업의 번호를 입력하고 Enter를 누르세요 (1-4): "

if "%menu_choice%"=="1" goto launch_chrome
if "%menu_choice%"=="2" goto start_sms
if "%menu_choice%"=="3" goto show_guide
if "%menu_choice%"=="4" goto exit_sys
goto menu

:launch_chrome
cls
echo ----------------------------------------------------------
echo  [1] 디버그용 독립 크롬 창을 실행합니다...
echo ----------------------------------------------------------
echo  * 새 크롬 창이 열리면 아래 주소로 접속해 페어링을 완료해 주세요:
echo    👉 https://messages.google.com/web
echo.
set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
start "" "%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\Antigravity_Debug_Session"
echo  [OK] 크롬이 실행되었습니다. 페어링 완료 후 아무 키나 누르세요.
pause
goto menu

:start_sms
cls
echo ----------------------------------------------------------
echo  [2] 단체 문자 발송을 시작합니다...
echo ----------------------------------------------------------
echo  * 주의: 반드시 [1]번 크롬 창이 켜져 있고 페어링되어 있어야 합니다.
echo.
python send_bulk_sms.py
echo.
echo  발송 작업이 완료되었습니다. 아무 키나 누르면 메뉴로 돌아갑니다.
pause
goto menu

:show_guide
cls
echo ==========================================================
echo             📋 시스템 사용법 및 자가 진단
echo ==========================================================
echo  1. 매번 새로 페어링해야 하나요?
echo     - 아닙니다! [1]번 버튼으로 열린 크롬 창은 로그인 세션이 
echo       안전하게 저장되므로, 최초 1회만 스마트폰 QR 코드로 
echo       페어링해 두시면 이후에는 바로 사용하실 수 있습니다.
echo.
echo  2. ECONNREFUSED 에러가 발생합니다.
echo     - 디버그용 크롬 창이 켜져 있지 않을 때 발생합니다.
echo       반드시 [1]번을 실행하여 크롬 창을 띄운 뒤 발송해 주세요.
echo.
echo  3. 학생 번호나 내용을 수정하려면 어떻게 하나요?
echo     - 같은 폴더 내의 'send_bulk_sms.py' 파일을 메모장 등으로 
echo       열어 상단의 메시지 템플릿(MESSAGE_TEMPLATE)을 
echo       수정해 주시면 됩니다.
echo ==========================================================
echo  상세한 가이드는 폴더 내의 'SMS_발송_가이드.md'를 확인하세요.
echo.
pause
goto menu

:exit_sys
echo 시스템을 종료합니다. 감사합니다.
timeout /t 2 >nul
exit
