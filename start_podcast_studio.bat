@echo off
echo ========================================
echo   🎙️  INTERACTIVE PODCAST STUDIO
echo ========================================
echo.
echo 🚀 Starting server...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo 📦 Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo 📥 Installing dependencies...
    pip install -r requirements_podcast_studio.txt
)

echo.
echo ✅ All set! Starting server...
echo.
echo 📱 Open in browser: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python interactive_podcast_studio.py

pause
