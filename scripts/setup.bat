@echo off
REM Setup script for AI Blog-to-Podcast Generator (Windows)

echo ==================================
echo AI Blog-to-Podcast Generator Setup
echo ==================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.8 or higher
    exit /b 1
)

REM Check if Ollama is installed
echo.
echo Checking Ollama installation...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama not found!
    echo Please install from: https://ollama.com/download
    exit /b 1
) else (
    echo Ollama is installed
)

REM Install Python dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements.txt

REM Pull default model
echo.
echo Pulling default AI model (llama2)...
ollama pull llama2

REM Create necessary directories
echo.
echo Creating directories...
if not exist "audio_segments" mkdir audio_segments
if not exist "final_podcasts" mkdir final_podcasts

echo.
echo ==================================
echo Setup complete!
echo ==================================
echo.
echo Run the application:
echo   python web_podcast_ollama.py
echo.
pause
