#!/usr/bin/env powershell
# Production Deployment Script for Digital Superman
# Run this script to deploy Digital Superman in production mode

Write-Host "🚀 Starting Digital Superman Production Deployment..." -ForegroundColor Green

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found. Please run setup first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host "❌ .env file not found. Please create it with required environment variables." -ForegroundColor Red
    Write-Host "Required variables: OPENAI_API_KEY, FLASK_SECRET_KEY" -ForegroundColor Yellow
    exit 1
}

# Install/update dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# Set production environment variables
$env:FLASK_ENV = "production"
$env:FLASK_DEBUG = "0"

# Start the Flask application
Write-Host "🌟 Starting Digital Superman in production mode..." -ForegroundColor Green
Write-Host "🔗 Application will be available at: http://localhost:5000" -ForegroundColor Cyan

python app.py
