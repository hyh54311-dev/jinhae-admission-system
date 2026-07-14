Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.Text = "오늘의 기업 추천 (08:30)"
$form.Size = New-Object System.Drawing.Size(700, 500)
$form.StartPosition = 'CenterScreen'
$form.TopMost = $true
$form.BackColor = [System.Drawing.Color]::White

$titleLabel = New-Object System.Windows.Forms.Label
$titleLabel.Text = "오늘의 추천 분석 기업: HD현대중공업"
$titleLabel.Font = New-Object System.Drawing.Font("Malgun Gothic", 22, [System.Drawing.FontStyle]::Bold)
$titleLabel.AutoSize = $true
$titleLabel.Location = New-Object System.Drawing.Point(30, 30)
$titleLabel.ForeColor = [System.Drawing.Color]::DarkBlue

$contentLabel = New-Object System.Windows.Forms.Label
$contentLabel.Text = "IT, 배터리, 자동차 섹터를 보셨으니,`n오늘은 새로운 사이클을 맞이한 '조선/방산' 대장주를 추천합니다!`n`n[추천 포인트]`n1. 10년 만에 찾아온 조선업 장기 슈퍼사이클`n2. 글로벌 친환경 선박 교체 수요 수혜`n3. K-방산(함정 수출) 모멘텀 탑재`n`n출근 잘 하셨나요? 오늘 시간 나실 때 분석을 요청해 주세요!"
$contentLabel.Font = New-Object System.Drawing.Font("Malgun Gothic", 16)
$contentLabel.AutoSize = $true
$contentLabel.Location = New-Object System.Drawing.Point(30, 100)

$button = New-Object System.Windows.Forms.Button
$button.Text = "확인"
$button.Font = New-Object System.Drawing.Font("Malgun Gothic", 16)
$button.Size = New-Object System.Drawing.Size(150, 60)
$button.Location = New-Object System.Drawing.Point(260, 350)
$button.BackColor = [System.Drawing.Color]::LightGray
$button.Add_Click({ $form.Close() })

$form.Controls.Add($titleLabel)
$form.Controls.Add($contentLabel)
$form.Controls.Add($button)

$form.ShowDialog()
