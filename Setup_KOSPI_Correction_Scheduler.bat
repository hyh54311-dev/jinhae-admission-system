@echo off
chcp 65001 > nul
echo ==========================================================
echo 📊 KOSPI 중기 조정 감지 봇 스케줄러 등록기
echo ==========================================================
echo.

SET PYTHON_PATH=C:\Users\admin\AppData\Local\Programs\Python\Python312\pythonw.exe
SET SCRIPT_PATH=d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\kospi_correction_detector.py

echo [설정 정보]
echo - Python 경로: %PYTHON_PATH%
echo - 스크립트 경로: %SCRIPT_PATH%
echo - 실행 시간: 매일 오후 2시 30분 (14:30)
echo.

schtasks /create /tn "KOSPI_Correction_Detector" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" /sc daily /st 14:30 /f

echo.
echo ==========================================================
echo ✅ 등록이 완료되었습니다.
echo ==========================================================
echo.
