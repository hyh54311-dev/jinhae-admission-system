# 이 스크립트는 학교 컴퓨터에서 실행해 주세요. (업무 자동화 시스템 통합 자동 시작 설정)
$PythonPath = (Get-Command pythonw.exe).Source
$StartupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Antigravity_Full_Suite.bat"

# 가동할 핵심 서비스 리스트 (명확한 배열 선언)
$Scripts = "verify_nlm_session.py", "daily_news.py"

$Content = "@echo off`r`n"
foreach ($S in $Scripts) {
    $FullPath = Join-Path $PSScriptRoot $S
    if (Test-Path $FullPath) {
        $Content += "start `"`" `"$PythonPath`" `"$FullPath`"`r`n"
        Write-Host "➕ 등록 대기: $S"
    } else {
        Write-Warning "⚠️ 파일을 찾을 수 없어 건너뜁니다: $S"
    }
}

if (-not $PythonPath) {
    Write-Error "pythonw.exe를 찾을 수 없습니다."
    exit
}

# 시작프로그램용 통합 배치 파일 생성
[System.IO.File]::WriteAllText($StartupPath, $Content, [System.Text.Encoding]::UTF8)

Write-Host "`n✅ 학교 컴퓨터 시작프로그램에 통합 등록되었습니다: $StartupPath"
Write-Host "🚀 시스템 가동을 위해 배치 파일을 직접 실행합니다..."

# 기존 프로세스 종료 후 재시작 (충돌 방지)
taskkill /f /im pythonw.exe /fi "status eq running" 2>$null
Start-Process -FilePath $StartupPath
Write-Host "✨ 모든 서비스가 백그라운드에서 가동되었습니다."
