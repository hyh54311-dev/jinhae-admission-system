@echo off
chcp 65001 >nul
echo ========================================================
echo 2026학년도 고사 HWP -> PDF 자동 변환 스케줄러 등록
echo ========================================================
echo.
echo [주의] 이 스크립트를 가동하면 백그라운드에서 주기적으로
echo        한글 파일을 PDF로 변환하는 작업이 돌아갑니다.
echo        원안 작업 중 한글이 닫히는 현상을 예방하려면
echo        중요 작업(원안 출제 등)이 완료된 후 실행해 주세요.
echo.
echo 실행하려면 아무 키나 누르세요... (Ctrl+C를 누르면 취소됩니다)
pause >nul

set TASK_NAME="Auto Convert HWP to PDF"
set VBS_PATH="D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\run_hwp_convert.vbs"

:: 기존 작업 삭제 후 재등록
schtasks /delete /tn %TASK_NAME% /f >nul 2>&1
schtasks /create /tn %TASK_NAME% /tr "wscript.exe %VBS_PATH%" /sc minute /mo 60 /f

echo.
echo --------------------------------------------------------
echo [완료] HWP -> PDF 자동 변환 스케줄러가 등록되었습니다.
echo        (매 1시간마다 백그라운드 자동 변환 작동)
echo --------------------------------------------------------
echo.
pause
