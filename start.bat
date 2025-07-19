@echo off
echo.
echo ========================================
echo   Digital Superman Flask - Quick Start
echo ========================================
echo.

echo Stopping any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1

echo.
echo Starting Flask application...
echo URL: http://localhost:5000
echo Health Check: http://localhost:5000/health
echo Test Endpoint: http://localhost:5000/test
echo.
echo Press Ctrl+C to stop the server
echo.

REM Use the virtual environment Python directly
.\venv\Scripts\python.exe app_simple.py

pause
