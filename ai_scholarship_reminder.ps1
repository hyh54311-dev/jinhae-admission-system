# ai_scholarship_reminder.ps1
# 2026학년도 AI융합교육 대학원 선발 공문 확인 정기 알림창 + 텔레그램 발송 (6월 ~ 12월)
# 매달 첫 번째 월요일 12:30 실행 (PC 꺼져있었을 시 다음 날 로그인 후 즉시 실행)

# 1. 2026년 6월~12월 기간 검사 (그 외 기간은 실행하지 않고 즉시 종료)
$now = Get-Date
if ($now.Year -ne 2026 -or $now.Month -lt 6 -or $now.Month -gt 12) {
    exit
}

# 2. 텔레그램 메시지 동시 발송 (초정밀 이중 알림 설계)
$telegramToken = "8799464748:AAE5vGid7_UOfE9Q0h9kL_3uI0gVOfYOnmU"
$telegramChatId = "8518409134"
$telegramMessage = "🏆 [진해고등학교 AI 대학원 진학 리마인더]`n`n" +
                  "선생님, 오늘 12시 30분은 AI융합교육 대학원 학자금 지원 공문 확인 시간입니다!`n`n" +
                  "★ 중요 미션: 2026년 교육대학원 연계 AI융합교육 과정 교육대상자 선발 추진 계획`n" +
                  "- 학자금의 절반 이상을 교육부에서 파격 지원해주는 전형이 내년에 최종 마감됩니다.`n" +
                  "- 따라서 올해 교육부 및 교육청의 인공지능(AI) 관련 공문, 연구, 사업이나 기회를 절대 놓치지 마시고 적극 도전해보셔야 합니다!`n`n" +
                  "💻 현재 시간 기준으로 학교 PC에 고대비 알림 팝업창이 표시되었으며, 팝업창의 버튼을 누르시면 PC에서 관련 계획서 폴더가 자동으로 열립니다.`n`n" +
                  "선생님의 AI 대학원 진학 합격과 장학생 선발을 진심으로 응원합니다. 화이팅입니다! 👍"

try {
    $uri = "https://api.telegram.org/bot$telegramToken/sendMessage"
    $body = @{
        chat_id = $telegramChatId
        text = $telegramMessage
    } | ConvertTo-Json
    
    # UTF-8 보장 처리하여 발송
    $response = Invoke-RestMethod -Uri $uri -Method Post -ContentType "application/json; charset=utf-8" -Body $body -TimeoutSec 10
} catch {
    # 인터넷 미연결 등으로 실패 시 팝업 진행을 방해하지 않고 에러 로그 우회
    Write-Warning "텔레그램 메시지 발송 실패: $_"
}

# 3. Windows WinForms 로드
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 4. 폼 설정 (고급스러운 딥 블루 & 골드 테마)
$form = New-Object Windows.Forms.Form
$form.Text = "★ [Antigravity] AI융합교육 대학원 학자금 지원 공문 알림"
$form.Size = New-Object Drawing.Size(650, 420)
$form.StartPosition = "CenterScreen"
$form.TopMost = $true
$form.BackColor = [Drawing.Color]::FromArgb(15, 23, 42) # Slate Dark (#0f172a)
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.MinimizeBox = $false

# 5. 상단 장식바
$headerBar = New-Object Windows.Forms.Panel
$headerBar.Size = New-Object Drawing.Size(650, 6)
$headerBar.Location = New-Object Drawing.Point(0, 0)
$headerBar.BackColor = [Drawing.Color]::FromArgb(59, 130, 246) # Vibrant Blue (#3b82f6)
$form.Controls.Add($headerBar)

# 6. 아이콘/타이틀 라벨
$titleLabel = New-Object Windows.Forms.Label
$titleLabel.Text = "🚨 대학원 학자금 지원 공문 확인일"
$titleLabel.Size = New-Object Drawing.Size(600, 40)
$titleLabel.Location = New-Object Drawing.Point(25, 25)
$titleLabel.Font = New-Object Drawing.Font("Malgun Gothic", 18, [Drawing.FontStyle]::Bold)
$titleLabel.ForeColor = [Drawing.Color]::FromArgb(248, 250, 252) # White-ish
$titleLabel.TextAlign = "MiddleLeft"
$form.Controls.Add($titleLabel)

# 7. 메인 알림 메시지
$msgText = "선생님, 오늘 12시 30분은 AI융합교육 대학원 지원 공문을 확인하는 날입니다.`n`n" +
           "📢 [핵심 목표]`n" +
           "- 2026년 교육대학원 연계 AI융합교육 과정 교육대상자 선발 추진 계획 관련`n" +
           "- 학자금 절반 이상을 지원해주는 교육부 전형이 내년에 최종 마감됩니다!`n" +
           "- 올해 교육부 및 교육청의 AI 관련 사업이나 업무 기회를 절대 놓치지 마세요.`n`n" +
           "📂 아래 버튼을 누르면 관련 추진 계획 폴더가 자동으로 열립니다.`n" +
           "💬 텔레그램(Telegram)으로도 실시간 메시지가 안전하게 발송되었습니다."

$msgLabel = New-Object Windows.Forms.Label
$msgLabel.Text = $msgText
$msgLabel.Size = New-Object Drawing.Size(580, 200)
$msgLabel.Location = New-Object Drawing.Point(25, 80)
$msgLabel.Font = New-Object Drawing.Font("Malgun Gothic", 11)
$msgLabel.ForeColor = [Drawing.Color]::FromArgb(203, 213, 225) # Light Gray
$msgLabel.TextAlign = "TopLeft"
$form.Controls.Add($msgLabel)

# 8. 버튼 클릭 이벤트 (확인 및 관련 계획 폴더 자동 열기)
$folderPath = "D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\개인적인 일\2026년 교육대학원연계 AI융합교육 전문과정 교육대상자 선발 추진 계획"

$button = New-Object Windows.Forms.Button
$button.Text = "확인 및 관련 계획 폴더 열기"
$button.Size = New-Object Drawing.Size(280, 50)
$button.Location = New-Object Drawing.Point(175, 300)
$button.Font = New-Object Drawing.Font("Malgun Gothic", 12, [Drawing.FontStyle]::Bold)
$button.FlatStyle = "Flat"
$button.BackColor = [Drawing.Color]::FromArgb(59, 130, 246) # Blue (#3b82f6)
$button.ForeColor = [Drawing.Color]::White
$button.Cursor = [Windows.Forms.Cursors]::Hand

$button.Add_Click({
    if (Test-Path $folderPath) {
        Start-Process "explorer.exe" "`"$folderPath`""
    } else {
        [Windows.Forms.MessageBox]::Show("계획 폴더를 찾을 수 없습니다.`n경로: $folderPath", "경로 오류", [Windows.Forms.MessageBoxButtons]::OK, [Windows.Forms.MessageBoxIcon]::Error)
    }
    $form.Close()
})
$form.Controls.Add($button)

# 9. 경고음 재생
[System.Media.SystemSounds]::Exclamation.Play()

# 10. 폼 실행
$form.ShowDialog() | Out-Null
