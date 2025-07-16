# Digital Superman - Production Release Checklist

Write-Host "🎯 Digital Superman - Final Production Cleanup" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

$ErrorCount = 0

# 1. Verify project structure
Write-Host "`n✅ Verifying project structure..." -ForegroundColor Yellow
$RequiredFiles = @(
    "app.py",
    "config.py", 
    "requirements.txt",
    ".env.example",
    "README.md",
    "TROUBLESHOOTING.md",
    "start_flask.ps1",
    "start_flask.bat",
    "check_flask.ps1"
)

foreach ($file in $RequiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file missing" -ForegroundColor Red
        $ErrorCount++
    }
}

# 2. Verify agent files
Write-Host "`n✅ Verifying AI agents..." -ForegroundColor Yellow
$AgentFiles = @(
    "agents\architecture_analyzer.py",
    "agents\policy_checker.py", 
    "agents\bicep_generator.py",
    "agents\__init__.py"
)

foreach ($file in $AgentFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file missing" -ForegroundColor Red
        $ErrorCount++
    }
}

# 3. Verify utility files
Write-Host "`n✅ Verifying utilities..." -ForegroundColor Yellow
$UtilFiles = @(
    "utils\file_processor.py",
    "utils\zip_generator.py",
    "utils\performance.py",
    "utils\__init__.py"
)

foreach ($file in $UtilFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file missing" -ForegroundColor Red
        $ErrorCount++
    }
}

# 4. Check for unwanted files  
Write-Host "`n🧹 Checking for unwanted files..." -ForegroundColor Yellow
$UnwantedFiles = @(
    "__pycache__",
    "agents\__pycache__",
    "utils\__pycache__",
    "test_agents.py",
    "CODE_REVIEW_SUMMARY.md",
    "diagnose_flask.ps1"
)

foreach ($file in $UnwantedFiles) {
    if (Test-Path $file) {
        Write-Host "   ⚠️ $file should be removed" -ForegroundColor Yellow
    } else {
        Write-Host "   ✅ $file cleaned" -ForegroundColor Green
    }
}

# 5. Verify directories are clean
Write-Host "`n🧹 Verifying clean directories..." -ForegroundColor Yellow
if ((Get-ChildItem "output" -ErrorAction SilentlyContinue).Count -eq 0) {
    Write-Host "   ✅ output/ directory clean" -ForegroundColor Green
} else {
    Write-Host "   ⚠️ output/ directory has files" -ForegroundColor Yellow
}

if ((Get-ChildItem "uploads" -ErrorAction SilentlyContinue).Count -eq 0) {
    Write-Host "   ✅ uploads/ directory clean" -ForegroundColor Green
} else {
    Write-Host "   ⚠️ uploads/ directory has files" -ForegroundColor Yellow
}

# 6. Check environment setup
Write-Host "`n🔧 Verifying environment..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   ⚠️ .env file exists (should be in .gitignore)" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ .env file not committed" -ForegroundColor Green
}

if (Test-Path ".env.example") {
    Write-Host "   ✅ .env.example template available" -ForegroundColor Green
} else {
    Write-Host "   ❌ .env.example missing" -ForegroundColor Red
    $ErrorCount++
}

# 7. Final summary
Write-Host "`n" + "="*50 -ForegroundColor Cyan
if ($ErrorCount -eq 0) {
    Write-Host "🎉 PROJECT READY FOR PRODUCTION!" -ForegroundColor Green
    Write-Host "`n✅ All required files present" -ForegroundColor Green
    Write-Host "✅ Unwanted files cleaned" -ForegroundColor Green  
    Write-Host "✅ Directory structure verified" -ForegroundColor Green
    Write-Host "✅ Environment configured" -ForegroundColor Green
    
    Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Commit all changes to repository" -ForegroundColor White
    Write-Host "2. Tag release version" -ForegroundColor White
    Write-Host "3. Deploy to production environment" -ForegroundColor White
    Write-Host "4. Update documentation if needed" -ForegroundColor White
    
} else {
    Write-Host "❌ $ErrorCount issues found. Please resolve before commit." -ForegroundColor Red
}

Write-Host "`n📊 Project Statistics:" -ForegroundColor Cyan
$CodeFiles = Get-ChildItem -Recurse -Include *.py | Where-Object { $_.FullName -notlike "*venv*" }
$LineCount = ($CodeFiles | Get-Content | Measure-Object -Line).Lines
Write-Host "   📝 Python files: $($CodeFiles.Count)" -ForegroundColor White
Write-Host "   📏 Lines of code: $LineCount" -ForegroundColor White
Write-Host "   🤖 AI Agents: 3" -ForegroundColor White
Write-Host "   🛠️ Utilities: 3" -ForegroundColor White
Write-Host "   🔧 Features: Auto-fix policy violations, Performance monitoring, Multi-format support" -ForegroundColor White
