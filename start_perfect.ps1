#!/usr/bin/env powershell

# Digital Superman Flask - Perfect Local Setup
Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  Digital Superman Flask - Perfect Setup" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Stop any existing processes
Write-Host "🛑 Stopping existing Python processes..." -ForegroundColor Yellow
try {
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "✅ Stopped existing processes" -ForegroundColor Green
} catch {
    Write-Host "ℹ️  No existing processes to stop" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🚀 Starting Flask application..." -ForegroundColor Green
Write-Host "📡 URL: http://localhost:5000" -ForegroundColor Cyan
Write-Host "🏥 Health: http://localhost:5000/health" -ForegroundColor Cyan
Write-Host "🧪 Test: http://localhost:5000/test" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

# Start Flask with virtual environment
& ".\venv\Scripts\python.exe" app_simple.py
