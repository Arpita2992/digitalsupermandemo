# Digital Superman Flask App Startup Script
# This script ensures reliable Flask server startup

Write-Host "🚀 Starting Digital Superman Flask App..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found. Creating new one..." -ForegroundColor Red
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
    
    # Activate and install requirements
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️ .env file not found. Copying from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ .env file created from example" -ForegroundColor Green
        Write-Host "📝 Please edit .env file with your OpenAI API key" -ForegroundColor Yellow
    } else {
        Write-Host "❌ .env.example not found. Please create .env manually" -ForegroundColor Red
    }
}

# Start Flask app
Write-Host "🌐 Starting Flask server on http://127.0.0.1:5000..." -ForegroundColor Cyan

try {
    # Set environment variables for Flask
    $env:FLASK_APP = "app.py"
    $env:FLASK_ENV = "development"
    $env:FLASK_DEBUG = "1"
    
    # Start Flask using the virtual environment Python
    .\venv\Scripts\python.exe app.py
}
catch {
    Write-Host "❌ Error starting Flask: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "🔧 Trying alternative startup method..." -ForegroundColor Yellow
    
    # Alternative: Use flask command
    .\venv\Scripts\flask.exe run --host=0.0.0.0 --port=5000 --debug
}

Write-Host "👋 Flask app stopped" -ForegroundColor Yellow
