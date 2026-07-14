Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.Text = "폴더 정리 완료 알림"
$form.Size = New-Object System.Drawing.Size(650,420)
$form.StartPosition = 'CenterScreen'
$form.TopMost = $true
$form.BackColor = [System.Drawing.Color]::White

$titleLabel = New-Object System.Windows.Forms.Label
$titleLabel.Text = "📁 이전 학년도 자료 정리 완료!"
$titleLabel.Font = New-Object System.Drawing.Font("Malgun Gothic", 22, [System.Drawing.FontStyle]::Bold)
$titleLabel.ForeColor = [System.Drawing.Color]::FromArgb(43, 87, 154) # Sleek blue
$titleLabel.Size = New-Object System.Drawing.Size(550, 50)
$titleLabel.Location = New-Object System.Drawing.Point(40, 40)

$contentLabel = New-Object System.Windows.Forms.Label
$contentLabel.Text = "2021학년도 자료 폴더 정리가 성공적으로 완료되었습니다!`n`n학급 경영, 수업, 창체 동아리, 기획(학교행사 및 홍보)`n4개 핵심 대분류 카테고리로 체계적으로 구조화되었으며,`n임시/잠금 파일 정리 및 중복 파일 안전 처리가 완료되었습니다."
$contentLabel.Font = New-Object System.Drawing.Font("Malgun Gothic", 13)
$contentLabel.ForeColor = [System.Drawing.Color]::FromArgb(51, 51, 51) # Elegant charcoal
$contentLabel.Size = New-Object System.Drawing.Size(550, 160)
$contentLabel.Location = New-Object System.Drawing.Point(40, 110)

$button = New-Object System.Windows.Forms.Button
$button.Text = "확인"
$button.Font = New-Object System.Drawing.Font("Malgun Gothic", 13, [System.Drawing.FontStyle]::Bold)
$button.BackColor = [System.Drawing.Color]::FromArgb(43, 87, 154)
$button.ForeColor = [System.Drawing.Color]::White
$button.Size = New-Object System.Drawing.Size(140, 50)
$button.Location = New-Object System.Drawing.Point(250, 290)
$button.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$button.FlatAppearance.BorderSize = 0
$button.Add_Click({ $form.Close() })

$form.Controls.Add($titleLabel)
$form.Controls.Add($contentLabel)
$form.Controls.Add($button)

$form.ShowDialog()
