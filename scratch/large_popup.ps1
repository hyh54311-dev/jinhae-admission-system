Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.Text = "작업 완료 알림"
$form.Size = New-Object System.Drawing.Size(600,400)
$form.StartPosition = 'CenterScreen'
$form.TopMost = $true

$label = New-Object System.Windows.Forms.Label
$label.Text = "장학생 명부 최신화 및`n[2026_장학금_정리] 탭 연동 작업이`n모두 성공적으로 완료되었습니다!"
$label.Font = New-Object System.Drawing.Font("Malgun Gothic", 20, [System.Drawing.FontStyle]::Bold)
$label.AutoSize = $true
$label.Location = New-Object System.Drawing.Point(40, 80)

$button = New-Object System.Windows.Forms.Button
$button.Text = "확인"
$button.Font = New-Object System.Drawing.Font("Malgun Gothic", 16)
$button.Size = New-Object System.Drawing.Size(150, 60)
$button.Location = New-Object System.Drawing.Point(220, 250)
$button.Add_Click({ $form.Close() })

$form.Controls.Add($label)
$form.Controls.Add($button)

$form.ShowDialog()
