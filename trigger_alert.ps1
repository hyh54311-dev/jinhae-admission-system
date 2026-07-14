# trigger_alert.ps1
# 고해상도/대형 알림창 트리거 (유니코드 직접 매핑으로 인코딩 문제 완벽 차단)

param (
    # 유니코드 문자를 직접 사용하여 어떤 환경에서도 한글이 깨지지 않게 함
    [string]$Title = "$([char]0xC7E0)$([char]0xD574)$([char]0xACE0) $([char]0xCC2B)$([char]0xBD07) $([char]0xD54C)$([char]0xB9BC)", # 진해고 챗봇 알림
    [string]$Message = "$([char]0xC120)$([char]0xC0DD)$([char]0xB2D8) $([char]0xC2DC)$([char]0xD0A4)$([char]0xC2E0) $([char]0xC77C)$([char]0xC774) $([char]0xC644)$([char]0xB8CC)$([char]0xB418)$([char]0xC5C8)$([char]0xC2B5)$([char]0xB2C8)$([char]0xB2E4)!" # 선생님 시키신 일이 완료되었습니다!
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$btnText = "$([char]0xD655)$([char]0xC778)" # 확인

$form = New-Object Windows.Forms.Form
$form.Text = $Title
$form.Size = New-Object Drawing.Size(600, 320)
$form.StartPosition = "CenterScreen"
$form.TopMost = $true
$form.BackColor = [Drawing.Color]::FromArgb(0, 45, 88)
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.MinimizeBox = $false

$label = New-Object Windows.Forms.Label
$label.Text = $Message
$label.Size = New-Object Drawing.Size(550, 150)
$label.Location = New-Object Drawing.Point(25, 50)
$label.Font = New-Object Drawing.Font("Malgun Gothic", 18, [Drawing.FontStyle]::Bold)
$label.ForeColor = [Drawing.Color]::White
$label.TextAlign = "MiddleCenter"
$form.Controls.Add($label)

$button = New-Object Windows.Forms.Button
$button.Text = $btnText
$button.Size = New-Object Drawing.Size(140, 50)
$button.Location = New-Object Drawing.Point(230, 210)
$button.Font = New-Object Drawing.Font("Malgun Gothic", 12, [Drawing.FontStyle]::Bold)
$button.FlatStyle = "Flat"
$button.BackColor = [Drawing.Color]::FromArgb(197, 160, 89)
$button.ForeColor = [Drawing.Color]::Black
$button.Add_Click({ $form.Close() })
$form.Controls.Add($button)

# 딩동 소리
[System.Media.SystemSounds]::Exclamation.Play()

$form.ShowDialog() | Out-Null
