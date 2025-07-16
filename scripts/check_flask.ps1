# Simple Flask Diagnostics Script
Write-Host "Flask Startup Diagnostics" -ForegroundColor Cyan

# Test 1: Check app.py
if (Test-Path "app.py") {
    Write-Host "✅ app.py found" -ForegroundColor Green
} else {
    Write-Host "❌ app.py not found" -ForegroundColor Red
}

# Test 2: Check virtual environment
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment missing" -ForegroundColor Red
}

# Test 3: Check Python version
try {
    $version = & ".\venv\Scripts\python.exe" --version
    Write-Host "✅ Python: $version" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not working" -ForegroundColor Red
}

# Test 4: Check Flask
try {
    & ".\venv\Scripts\python.exe" -c "import flask" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Flask installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Flask not installed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Cannot check Flask" -ForegroundColor Red
}

# Test 5: Check .env
if (Test-Path ".env") {
    Write-Host "✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "⚠️ .env file missing" -ForegroundColor Yellow
}

Write-Host "`nStartup Commands:" -ForegroundColor Cyan
Write-Host "1. .\venv\Scripts\python.exe app.py"
Write-Host "2. .\start_flask.ps1"
Write-Host "3. .\start_flask.bat"
