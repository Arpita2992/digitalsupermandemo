# Production Deployment Script for Digital Superman
param(
    [string]$Environment = "production",
    [switch]$SkipTests = $false
)

Write-Host "🚀 Starting Digital Superman Production Deployment..." -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found. Please create one based on .env.example" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Blue
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Blue
@("uploads", "output", "logs") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force
    }
}

# Clean up old logs and uploads
Write-Host "🧹 Cleaning up old files..." -ForegroundColor Blue
Get-ChildItem uploads\* -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem logs\*.log -ErrorAction SilentlyContinue | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-7) } | Remove-Item -Force

# Production environment checks
Write-Host "🔍 Running production checks..." -ForegroundColor Yellow

# Check required environment variables
$requiredVars = @(
    'AZURE_AI_AGENT1_ENDPOINT',
    'AZURE_AI_AGENT1_KEY',
    'AZURE_AI_AGENT2_ENDPOINT',
    'AZURE_AI_AGENT2_KEY',
    'AZURE_AI_AGENT3_ENDPOINT',
    'AZURE_AI_AGENT3_KEY',
    'AZURE_AI_AGENT4_ENDPOINT',
    'AZURE_AI_AGENT4_KEY',
    'SECRET_KEY'
)

$missingVars = @()
foreach ($var in $requiredVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if (-not $value) {
        # Try to load from .env file
        $envContent = Get-Content .env -ErrorAction SilentlyContinue
        $envVar = $envContent | Where-Object { $_ -match "^$var=" }
        if (-not $envVar) {
            $missingVars += $var
        }
    }
}

if ($missingVars.Count -gt 0) {
    Write-Host "❌ Missing required environment variables: $($missingVars -join ', ')" -ForegroundColor Red
    exit 1
}

Write-Host "✅ All required environment variables are set" -ForegroundColor Green

# Test application startup if not skipped
if (-not $SkipTests) {
    Write-Host "🧪 Testing application startup..." -ForegroundColor Yellow
    
    $appProcess = Start-Process -FilePath "python" -ArgumentList "app.py" -PassThru -NoNewWindow -RedirectStandardOutput "nul" -RedirectStandardError "nul"
    Start-Sleep -Seconds 5
    
    if ($appProcess.HasExited) {
        Write-Host "❌ Application failed to start" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "✅ Application starts successfully" -ForegroundColor Green
        $appProcess.Kill()
    }
}

Write-Host "✅ Production deployment completed successfully!" -ForegroundColor Green
Write-Host "🚀 To start the application:" -ForegroundColor Cyan
Write-Host "   - For development: python app.py" -ForegroundColor White
Write-Host "   - For production: gunicorn -w 4 -b 0.0.0.0:8000 app:app" -ForegroundColor White
Write-Host "   - For Windows service: Use the provided start_flask.ps1" -ForegroundColor White
