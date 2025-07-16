@echo off
REM Digital Superman Flask App Startup Script (Windows Batch)
echo 🚀 Starting Digital Superman Flask App...

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found. Creating new one...
    python -m venv venv
    echo ✅ Virtual environment created
    
    REM Install requirements
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    echo ✅ Dependencies installed
) else (
    echo ✅ Virtual environment found
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️ .env file not found. Copying from .env.example...
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo ✅ .env file created from example
        echo 📝 Please edit .env file with your OpenAI API key
    ) else (
        echo ❌ .env.example not found. Please create .env manually
    )
)

REM Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=1

REM Start Flask app
echo 🌐 Starting Flask server on http://127.0.0.1:5000...
venv\Scripts\python.exe app.py

echo 👋 Flask app stopped
pause
