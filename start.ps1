Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PersonaLingo v2 - PowerShell Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$root = $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }

# [1/2] Backend
Write-Host "[1/2] Starting Backend (port 9849)..." -ForegroundColor Yellow
$backendCmd = "Set-Location `"$root\backend`"; " +
    "if (Test-Path requirements.txt) { pip install -r requirements.txt | Out-Null }; " +
    "python run.py"
Start-Process -WindowStyle Hidden -FilePath "powershell" -ArgumentList "-NoProfile", "-Command", $backendCmd

# [2/2] Frontend
Write-Host "[2/2] Starting Frontend (port 5273)..." -ForegroundColor Yellow
$frontendCmd = "Set-Location `"$root\frontend`"; " +
    "if (-not (Test-Path node_modules)) { npm install | Out-Null }; " +
    "npm run dev"
Start-Process -WindowStyle Hidden -FilePath "powershell" -ArgumentList "-NoProfile", "-Command", $frontendCmd

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:9849" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:5273" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Services started in background. Close their PowerShell windows to stop." -ForegroundColor Gray
