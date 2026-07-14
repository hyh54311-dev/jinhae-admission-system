param(
    [string]$Title = "Antigravity AI",
    [string]$Message = "요청하신 작업이 조용히 완료되었습니다."
)

# Load Windows Forms
Add-Type -AssemblyName System.Windows.Forms

# Create NotifyIcon
$global:balloon = New-Object System.Windows.Forms.NotifyIcon
$balloon.Icon = [System.Drawing.SystemIcons]::Information
$balloon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
$balloon.BalloonTipTitle = $Title
$balloon.BalloonTipText = $Message
$balloon.Visible = $true

# Show Balloon Tip
$balloon.ShowBalloonTip(3000)

# Keep script alive long enough for toast to appear, then cleanup
Start-Sleep -Seconds 4
$balloon.Dispose()
