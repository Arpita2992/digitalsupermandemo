#!/usr/bin/env powershell
# Setup Script for Digital Superman
# Run this script to set up Digital Superman for the first time

Write-Host "🔧 Setting up Digital Superman..." -ForegroundColor Green

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Please edit .env file and add your OpenAI API key" -ForegroundColor Yellow
}

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
if (!(Test-Path "uploads")) { New-Item -ItemType Directory -Path "uploads" }
if (!(Test-Path "output")) { New-Item -ItemType Directory -Path "output" }

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Edit .env file with your OpenAI API key" -ForegroundColor White
Write-Host "  2. Run .\deploy.ps1 to start the application" -ForegroundColor White
