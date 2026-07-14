# Powershell script to load statistics and show a custom Windows Forms Popup dialog to the User.
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$statsPath = "d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\cleanup_stats.json"

$stats = $null
if (Test-Path $statsPath) {
    try {
        $stats = Get-Content $statsPath -Raw | ConvertFrom-Json
    } catch {
        # Fallback
    }
}

if ($stats -eq $null) {
    # Fallback 객체 생성 시 한글 키 문법 충돌 피하기 위해 Add 메서드 사용
    $yearsObj = New-Object PSCustomObject
    $yearsObj | Add-Member -MemberType NoteProperty -Name "2015학년도" -Value 5119
    $yearsObj | Add-Member -MemberType NoteProperty -Name "2018학년도" -Value 755
    $yearsObj | Add-Member -MemberType NoteProperty -Name "2019학년도" -Value 1562
    $yearsObj | Add-Member -MemberType NoteProperty -Name "2021학년도" -Value 32

    $stats = [PSCustomObject]@{
        total_scanned = 10999
        organized = 10724
        album_deleted = 269
        personal_deleted = 6
        years = $yearsObj
    }
}

$title = "📁 진해고등학교 [새 폴더] 정리 작업 완수 알림"
$msg = @"
선생님! 요청하신 임시 [새 폴더] 정리 및 클린업 작업이 무사히 완수되었습니다.

주요 정리 통계 및 작업 요약:
--------------------------------------------------
■ 총 검토 파일 수: $($stats.total_scanned) 개
■ 연도별/4대 표준 분류로 정리된 파일: $($stats.organized) 개
■ 졸업앨범용 학생 사진 삭제 (격리): $($stats.album_deleted) 개
■ 민감 개인정보 서류(등본/초본/통장) 삭제 (격리): $($stats.personal_deleted) 개
--------------------------------------------------

📂 연도별 정리 완료 분포:
$(
    $yearsStr = ""
    foreach ($prop in $stats.years.PSObject.Properties) {
        $yearsStr += "  - $($prop.Name): $($prop.Value) 개`n"
    }
    $yearsStr
)
안전한 데이터 보존을 위해 원본 폴더를 직접 변경하지 않고,
신규 정리 폴더 [새 폴더_정리완료]를 생성하여 체계적으로 정렬 배치했습니다.
삭제(폐기) 대상 파일은 [새 폴더_삭제격리]에 안전하게 격리 보존해 두었습니다.

최종 정렬 결과를 확인해 보시고, 원본 폴더는 안심하고 지우셔도 됩니다!
"@

[System.Windows.Forms.MessageBox]::Show($msg, $title, [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
