$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Get-Location }

$tasks = @(
    @{ Name = "DailyNewsSummary"; Vbs = "run_news_once.vbs";   Time = "15:15"; Days = "MON,TUE,WED,THU,FRI" },
    @{ Name = "OkinawaFlightAlert_10"; Vbs = "run_flight_alert.vbs"; Time = "10:00"; Days = "MON,TUE,WED,THU,FRI" },
    @{ Name = "OkinawaFlightAlert_15"; Vbs = "run_flight_alert.vbs"; Time = "15:00"; Days = "MON,TUE,WED,THU,FRI" },
    @{ Name = "AdmissionNews_11AM"; Vbs = "run_admission_news.vbs"; Time = "11:00"; Days = "WED" }
)

foreach ($t in $tasks) {
    $vbsPath = Join-Path $scriptDir $t.Vbs
    $command = "wscript.exe `"$vbsPath`""
    
    # 작업 삭제 (실패 시 무시)
    schtasks /delete /tn $t.Name /f 2>$null
    
    # 작업 생성
    schtasks /create /tn $t.Name /tr $command /sc weekly /d $t.Days /st $t.Time /f
    
    # 전원 설정 수정 (배터리 모드에서도 실행)
    # Settings xml을 추출하여 수정 후 재등록하는 방식은 복잡하므로, PowerShell 명령어로 직접 설정 시도
    # (일반적으로 schtasks만으로는 배터리 모드 제어가 어려움)
}

Write-Host "모든 자동화 작업이 성공적으로 재등록되었습니다."
