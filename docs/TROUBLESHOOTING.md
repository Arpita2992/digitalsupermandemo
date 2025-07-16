# 🔧 Digital Superman Flask App - Troubleshooting Guide

## Common Issues and Solutions

### 1. Virtual Environment Path Issues

**Problem**: `.venv\Scripts\python.exe` not recognized
**Solutions**:
```powershell
# Option A: Use absolute path
$env:PROJECT_PATH = Get-Location
& "$env:PROJECT_PATH\venv\Scripts\python.exe" app.py

# Option B: Use PowerShell script
.\start_flask.ps1

# Option C: Use batch file
.\start_flask.bat

# Option D: Activate virtual environment first
.\venv\Scripts\Activate.ps1
python app.py
```

### 2. PowerShell Execution Policy Issues

**Problem**: PowerShell scripts cannot execute
**Solution**:
```powershell
# Check current policy
Get-ExecutionPolicy

# Temporarily allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass
powershell -ExecutionPolicy Bypass -File start_flask.ps1
```

### 3. Missing Dependencies

**Problem**: ImportError or module not found
**Solution**:
```powershell
# Reinstall requirements
.\venv\Scripts\pip.exe install -r requirements.txt

# Upgrade pip first
.\venv\Scripts\python.exe -m pip install --upgrade pip
```

### 4. Environment Variables Missing

**Problem**: OpenAI API key not found
**Solution**:
1. Copy `.env.example` to `.env`
2. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

### 5. Port Already in Use

**Problem**: Port 5000 is already in use
**Solution**:
```powershell
# Check what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /PID <process_id> /F

# Or use different port
$env:FLASK_RUN_PORT = "5001"
.\venv\Scripts\flask.exe run --port 5001
```

## Quick Start Commands

### Method 1: PowerShell Script (Recommended)
```powershell
.\start_flask.ps1
```

### Method 2: Direct Python
```powershell
.\venv\Scripts\python.exe app.py
```

### Method 3: Flask CLI
```powershell
$env:FLASK_APP = "app.py"
.\venv\Scripts\flask.exe run --host=0.0.0.0 --port=5000 --debug
```

### Method 4: VS Code Task
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "Start Digital Superman Flask App (Robust)"

## Environment Verification

Run these commands to verify your setup:

```powershell
# Check Python version
.\venv\Scripts\python.exe --version

# Check Flask installation
.\venv\Scripts\pip.exe show flask

# Check if .env exists
Test-Path .env

# List all installed packages
.\venv\Scripts\pip.exe list
```

## Alternative Startup Methods

If the main methods fail, try these alternatives:

### Using Python Module
```powershell
.\venv\Scripts\python.exe -m flask run --host=0.0.0.0 --port=5000
```

### Using Gunicorn (Production-like)
```powershell
.\venv\Scripts\gunicorn.exe -w 1 -b 0.0.0.0:5000 app:app
```

### Direct Import Test
```powershell
.\venv\Scripts\python.exe -c "import app; print('App imports successfully')"
```

## Logs and Debugging

Enable verbose logging:
```powershell
$env:FLASK_DEBUG = "1"
$env:PYTHONPATH = Get-Location
.\venv\Scripts\python.exe app.py
```

Check for syntax errors:
```powershell
.\venv\Scripts\python.exe -m py_compile app.py
```

## Need Help?

1. Check this troubleshooting guide first
2. Verify your virtual environment is properly set up
3. Ensure all dependencies are installed
4. Check the `.env` file exists and has valid API keys
5. Try different startup methods listed above

## Success Indicators

When Flask starts successfully, you should see:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Then visit: http://127.0.0.1:5000
