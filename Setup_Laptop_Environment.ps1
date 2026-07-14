# Setup_Laptop_Environment.ps1
# 이 스크립트는 여름방학 동안 사용할 노트북의 개발 및 에이전트(Antigravity) 작동 환경을 진단하고 설정합니다.

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " [Antigravity] 여름방학 노트북 환경 진단 및 설정" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$Success = $true

# 1. Python Check
Write-Host "`n[1/5] Python 설치 확인 중..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $PyVer = python --version
    Write-Host "  -> Python이 설치되어 있습니다: $PyVer" -ForegroundColor Green
} else {
    Write-Host "  [!] Python이 설치되어 있지 않습니다!" -ForegroundColor Red
    Write-Host "  -> Microsoft Store에서 Python 3.11 또는 3.12를 설치하시거나 아래 링크에서 다운로드해 주세요:" -ForegroundColor Yellow
    Write-Host "     https://www.python.org/downloads/" -ForegroundColor Cyan
    $Success = $false
}

# 2. Node.js Check
Write-Host "`n[2/5] Node.js 설치 확인 중..." -ForegroundColor Yellow
if (Get-Command node -ErrorAction SilentlyContinue) {
    $NodeVer = node --version
    Write-Host "  -> Node.js가 설치되어 있습니다: $NodeVer" -ForegroundColor Green
} else {
    Write-Host "  [!] Node.js가 설치되어 있지 않습니다!" -ForegroundColor Red
    Write-Host "  -> 아래 링크에서 LTS 버전을 다운로드하여 설치해 주세요:" -ForegroundColor Yellow
    Write-Host "     https://nodejs.org/" -ForegroundColor Cyan
    $Success = $false
}

# 3. Git Check
Write-Host "`n[3/5] Git 설치 확인 중..." -ForegroundColor Yellow
if (Get-Command git -ErrorAction SilentlyContinue) {
    $GitVer = git --version
    Write-Host "  -> Git이 설치되어 있습니다: $GitVer" -ForegroundColor Green
} else {
    Write-Host "  [!] Git이 설치되어 있지 않습니다! (버전 관리 및 플러그인에 필요할 수 있습니다.)" -ForegroundColor Gray
    Write-Host "  -> https://git-scm.com/" -ForegroundColor Cyan
}

# 4. UV (Python 고속 패키지 매니저) Check & Install
Write-Host "`n[4/5] UV 패키지 매니저 설치 확인 중..." -ForegroundColor Yellow
if (Get-Command uv -ErrorAction SilentlyContinue) {
    $UvVer = uv --version
    Write-Host "  -> uv가 설치되어 있습니다: $UvVer" -ForegroundColor Green
} else {
    Write-Host "  -> uv가 없습니다. 자동 설치를 시작합니다..." -ForegroundColor Yellow
    try {
        powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
        # 환경 변수 강제 갱신
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        if (Get-Command uv -ErrorAction SilentlyContinue) {
            Write-Host "  -> uv 설치 완료!" -ForegroundColor Green
        } else {
            Write-Host "  -> uv 설치는 완료되었으나 현재 파워쉘 세션을 재시작해야 적용됩니다. (경로: $env:USERPROFILE\.local\bin\uv)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  [!] uv 설치 실패: $_" -ForegroundColor Red
    }
}

# 5. Python 의존성 라이브러리 설치
Write-Host "`n[5/5] Python 의존성 라이브러리 설치 (requirements.txt)" -ForegroundColor Yellow
$ReqPath = Join-Path $PSScriptRoot "requirements.txt"
if (Test-Path $ReqPath) {
    Write-Host "  -> requirements.txt 발견! 패키지 설치 중..." -ForegroundColor Yellow
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        uv pip install -r $ReqPath --system
    } else {
        pip install -r $ReqPath
    }
    Write-Host "  -> 라이브러리 설치 완료!" -ForegroundColor Green
} else {
    Write-Host "  -> requirements.txt가 이 폴더에 없습니다. 라이브러리 설치를 건너뜁니다." -ForegroundColor Gray
}

# 6. 클라우드 동기화 경로 체크 및 작업 공간 상태 진단
Write-Host "`n[추가] 작업 공간 경로 진단" -ForegroundColor Yellow
Write-Host "  -> 현재 스크립트 실행 경로: $PSScriptRoot" -ForegroundColor Green
if ($PSScriptRoot -like "*OneDrive*" -or $PSScriptRoot -like "*Google*" -or $PSScriptRoot -like "*Google Drive*" -or $PSScriptRoot -like "*My Drive*") {
    Write-Host "  -> 클라우드 동기화(OneDrive 또는 Google Drive)가 활성화된 정상 경로입니다." -ForegroundColor Green
} else {
    Write-Host "  [참고] 노트북의 작업 폴더가 클라우드 동기화(구글 드라이브 / 원드라이브) 폴더 내에 있는지 재차 확인해 주세요." -ForegroundColor Yellow
}

Write-Host "`n=========================================" -ForegroundColor Cyan
if ($Success) {
    Write-Host " [진단 완료] 노트북의 기본 환경 및 종속성이 정상적으로 준비되었습니다!" -ForegroundColor Green
} else {
    Write-Host " [확인 필요] 위에 표시된 미설치 도구들을 다운로드한 뒤 이 스크립트를 다시 실행해 주세요." -ForegroundColor Red
}
Write-Host "=========================================" -ForegroundColor Cyan
