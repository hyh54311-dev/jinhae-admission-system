@echo off
schtasks /create /tn "MorningCompanyRecommendation" /tr "\"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\run_recommend.bat\"" /sc once /sd 2026/05/13 /st 08:30 /f
