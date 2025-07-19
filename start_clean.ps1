#!/usr/bin/env powershell

# Digital Superman Flask Application - SSL Error Suppression Version
# This script starts Flask with proper SSL error handling

Write-Host "🚀 Digital Superman - Clean Flask Startup (SSL Error Suppression)" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green

# Stop any existing Python processes
Write-Host "🛑 Stopping existing Python processes..." -ForegroundColor Yellow
try {
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "✅ Stopped existing processes" -ForegroundColor Green
} catch {
    Write-Host "ℹ️  No existing processes to stop" -ForegroundColor Cyan
}

# Wait for ports to be released
Start-Sleep -Seconds 2

# Activate virtual environment
Write-Host "🐍 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Start with SSL error suppression
Write-Host "🌐 Starting Flask with SSL error suppression..." -ForegroundColor Yellow
Write-Host "📡 Application will be available at: http://localhost:8888" -ForegroundColor Cyan
Write-Host "�️  SSL/TLS handshake errors will be suppressed" -ForegroundColor Cyan
Write-Host "🔒 Security features: Enabled" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

# Use the clean runner
python run_clean.py
