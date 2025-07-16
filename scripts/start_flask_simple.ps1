# Simple Flask startup script
Write-Host "Starting Flask..." -ForegroundColor Green

if (Test-Path ".\venv\Scripts\python.exe") {
    Write-Host "Virtual environment found" -ForegroundColor Green
    .\venv\Scripts\python.exe app.py
} else {
    Write-Host "Virtual environment not found, using system Python" -ForegroundColor Yellow
    python app.py
}
