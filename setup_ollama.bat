@echo off
echo ========================================
echo  OLLAMA SETUP FOR PODCAST GENERATOR
echo ========================================
echo.

echo Step 1: Installing Python package...
pip install ollama
echo.

echo Step 2: Checking if Ollama is installed...
ollama --version
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Ollama not found!
    echo.
    echo Please install Ollama:
    echo 1. Download from: https://ollama.com/download
    echo 2. Install it
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

echo.
echo Step 3: Pulling llama3.2 model (2GB)...
echo This may take a few minutes...
ollama pull llama3.2

echo.
echo ========================================
echo  SETUP COMPLETE!
echo ========================================
echo.
echo You can now run:
echo   python podcast_generator_ollama.py
echo   python web_podcast_ollama.py
echo.
echo No API limits! Unlimited podcasts!
echo.
pause
