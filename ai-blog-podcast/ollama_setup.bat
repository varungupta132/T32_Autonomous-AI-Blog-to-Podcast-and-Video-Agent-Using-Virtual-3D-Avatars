@echo off
echo ========================================
echo Ollama Setup for AI Blog-to-Podcast Agent
echo ========================================
echo.

echo Checking if Ollama is installed...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama is not installed!
    echo.
    echo Please install Ollama from: https://ollama.ai
    echo.
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo [OK] Ollama is installed
echo.

echo Pulling llama2 model for podcast generation...
echo This may take a few minutes depending on your internet connection.
echo.

ollama pull llama2

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to pull llama2 model
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now run the podcast generator.
echo.
echo Next steps:
echo 1. Setup backend: cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt
echo 2. Setup frontend: cd ../frontend && npm install
echo 3. Start Ollama: ollama serve
echo 4. Start backend: cd backend && python run.py
echo 5. Start frontend: cd frontend && npm run dev
echo.
pause
